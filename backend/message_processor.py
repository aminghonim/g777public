"""
G777 Message Processor - Enhanced Media Support
================================================
Handles extraction and processing of text, images, audio, video, and documents.
"""

import logging
import asyncio
from typing import Tuple, Optional, Dict, Any
from .ai_engine import ai_engine
from .brain_trainer import BrainTrainer
from .db_service import get_db_cursor
from .baileys_client import baileys_client

logger = logging.getLogger(__name__)

# ============================================================================
# MEDIA TYPE DETECTION
# ============================================================================

SUPPORTED_MEDIA_TYPES = {
    'imageMessage': 'image',
    'audioMessage': 'audio',
    'videoMessage': 'video',
    'documentMessage': 'document',
    'stickerMessage': 'sticker',
    'pttMessage': 'voice_note'  # Push-to-Talk
}

def detect_media_type(message_obj: dict) -> Optional[str]:
    """
    Enhanced media type detection with priority order.
    Returns: media_type string or None
    """
    for key, media_type in SUPPORTED_MEDIA_TYPES.items():
        if message_obj.get(key):
            logger.info(f"📎 Media detected: {media_type} ({key})")
            return media_type
    return None

def extract_media_metadata(message_obj: dict, media_type: str) -> Dict[str, Any]:
    """
    Extract metadata from media message (URL, mimetype, caption, etc.)
    """
    media_key = f"{media_type}Message" if media_type in ['image', 'audio', 'video', 'document'] else media_type
    media_data = message_obj.get(media_key, {})
    
    return {
        'url': media_data.get('url'),
        'mimetype': media_data.get('mimetype'),
        'caption': media_data.get('caption', ''),
        'filename': media_data.get('fileName'),
        'filesize': media_data.get('fileLength'),
        'duration': media_data.get('seconds'),  # For audio/video
    }

# ============================================================================
# MESSAGE EXTRACTION (MAIN FUNCTION)
# ============================================================================

def extract_message_info(payload: dict) -> Tuple[str, str, bool, Optional[str], Optional[Dict]]:
    """
    🎯 CRITICAL FUNCTION - Returns 5 values (added media_metadata)
    
    Robust extraction of message data from Evolution API v2 / Baileys payload.
    Supports @lid and @s.whatsapp.net JIDs.
    
    Returns:
        Tuple of (message_text, remote_jid, is_from_me, media_type, media_metadata)
    
    Examples:
        >>> extract_message_info(text_payload)
        ("مرحبا", "201097752711@s.whatsapp.net", False, None, None)
        
        >>> extract_message_info(image_payload)
        ("شوف الصورة دي", "113357222854724@lid", False, "image", {...})
    """
    try:
        # Extract nested data
        msg_data = payload.get('data', {})
        if not msg_data:
            msg_data = payload  # Fallback if data is flat
            
        message_obj = msg_data.get('message', {})
        key_obj = msg_data.get('key', {})
        
        # ==================== TEXT EXTRACTION ====================
        message_text = (
            message_obj.get('conversation') or
            message_obj.get('extendedTextMessage', {}).get('text') or
            message_obj.get('imageMessage', {}).get('caption') or
            message_obj.get('videoMessage', {}).get('caption') or
            message_obj.get('documentMessage', {}).get('caption') or
            message_obj.get('text') or
            msg_data.get('text') or
            msg_data.get('content') or
            ""
        )
        
        # ==================== MEDIA DETECTION ====================
        media_type = detect_media_type(message_obj)
        media_metadata = None
        
        if media_type:
            media_metadata = extract_media_metadata(message_obj, media_type)
            logger.info(f"📎 Media Info: {media_type} | Caption: {message_text[:30] if message_text else 'N/A'}")
        
        # ==================== JID EXTRACTION ====================
        # Support both @lid (LID addressing) and @s.whatsapp.net
        remote_jid = (
            key_obj.get('remoteJid') or 
            msg_data.get('remoteJid') or 
            payload.get('remoteJid') or
            ""
        )
        
        # Fallback to remoteJidAlt if main is LID
        if '@lid' in remote_jid:
            remote_jid_alt = key_obj.get('remoteJidAlt') or msg_data.get('remoteJidAlt')
            if remote_jid_alt:
                logger.info(f"🔄 Using remoteJidAlt: {remote_jid_alt} (original: {remote_jid})")
                # Keep original for reply, but use alt for phone extraction
        
        # ==================== FROM_ME DETECTION ====================
        is_from_me = (
            key_obj.get('fromMe') is True or 
            msg_data.get('fromMe') is True or
            payload.get('fromMe') is True
        )
        
        # ==================== LOGGING ====================
        phone = remote_jid.split('@')[0] if '@' in remote_jid else remote_jid
        preview = message_text[:50] if message_text else f"[{media_type or 'unknown'}]"
        logger.info(f"📩 Extracted | From: {phone} | Text: {preview} | Media: {media_type} | FromMe: {is_from_me}")
        
        # 🎯 CRITICAL: Return 5 values
        return message_text, remote_jid, is_from_me, media_type, media_metadata
        
    except Exception as e:
        logger.error(f"❌ Error in extract_message_info: {e}", exc_info=True)
        # Return safe defaults
        return "", "", False, None, None

# ============================================================================
# AI RESPONSE PROCESSING
# ============================================================================

async def process_ai_response(
    message_text: str, 
    phone: str, 
    history_text: str, 
    media_type: Optional[str] = None,
    save_training: bool = True
) -> Optional[str]:
    """
    Enhanced AI pipeline with media context awareness.
    
    Pipeline:
    1. Generate Raw Response (AI Engine) - with media context
    2. Humanize Response (Brain Trainer)
    3. Save Training Sample (Optional)
    
    Args:
        message_text: The actual message text
        phone: Customer phone number
        history_text: Conversation history
        media_type: Type of media if present (image/audio/video/etc)
        save_training: Whether to save this interaction for training
    
    Returns:
        Humanized AI response or None
    """
    try:
        # Enhance prompt with media context
        enhanced_prompt = message_text
        if media_type:
            media_prefix = {
                'image': '📷 [المستخدم أرسل صورة]',
                'audio': '🎤 [المستخدم أرسل رسالة صوتية]',
                'video': '🎥 [المستخدم أرسل فيديو]',
                'document': '📄 [المستخدم أرسل مستند]',
                'sticker': '😊 [المستخدم أرسل ملصق]',
            }
            prefix = media_prefix.get(media_type, f'📎 [{media_type}]')
            enhanced_prompt = f"{prefix}\n{message_text}" if message_text else prefix
        
        # Step A: Generate Raw Response
        logger.info(f"🤖 Generating AI response for {phone} (media: {media_type})...")
        raw_response = await ai_engine.generate_response(enhanced_prompt, phone, history_text)
        
        if not raw_response:
            logger.warning(f"⚠️ AI Engine returned empty response for {phone}")
            return None

        logger.info(f"✅ Raw Response: {raw_response[:80]}...")

        # Step B: Humanize Response
        try:
            trainer = BrainTrainer()
            final_response = await trainer.humanize_bot_response(message_text, raw_response)
            logger.info(f"✨ Humanized: {final_response[:80] if final_response else 'FAILED'}")
        except Exception as trainer_err:
            logger.warning(f"⚠️ Humanizer failed: {trainer_err}. Using raw response.")
            final_response = raw_response
            
        # Ensure we have a response
        final_response = final_response or raw_response
        
        # Step C: Save Training Sample (async background task)
        if save_training and final_response:
            asyncio.create_task(
                save_training_task(enhanced_prompt, raw_response, final_response)
            )
        
        return final_response
        
    except Exception as e:
        logger.error(f"❌ Error in process_ai_response: {e}", exc_info=True)
        return None

async def save_training_task(question: str, raw: str, final: str):
    """Background task to save training samples."""
    try:
        from .db_service import get_db_cursor
        with get_db_cursor() as cur:
            if cur:
                cur.execute("""
                    INSERT INTO bot_training_samples 
                    (question, robotic_response, humanized_response, human_rating, created_at)
                    VALUES (%s, %s, %s, NULL, NOW())
                """, (question, raw, final))
                logger.info("💾 Training sample saved")
    except Exception as e:
        logger.error(f"❌ Failed to save training: {e}")
