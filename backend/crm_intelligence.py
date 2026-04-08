"""
G777 CRM Intelligence
=====================
Extracts customer data from chat history using Gemini AI 
and updates the CRM (customer_profiles) automatically.
"""

import os
import json
import asyncio
import logging
from backend.db_service import get_system_prompt, get_conversation_history, update_customer_profile
from backend.ai_service import generate_ai_response, call_gemini_direct

logger = logging.getLogger(__name__)

async def run_data_extraction(phone, conv_id):
    """
    Analyzes the conversation history and updates the CRM profile for the given phone.
    """
    logger.info(f"AI is extracting CRM data for {phone}...")
    
    # 1. Get Conversation History
    history = get_conversation_history(conv_id, limit=20)
    if not history:
        return
        
    # 2. Get the Extractor Prompt
    extractor_prompt_template = get_system_prompt('entity_extractor')
    if not extractor_prompt_template:
        logger.warning("Extractor prompt not found in DB.")
        return
        
    # 3. Format the Prompt
    full_prompt = extractor_prompt_template.replace('{conversation}', history)
    
    # 4. Call Gemini AI
    # (Using a direct approach to ensure it works with the current setup)
    # Note: Using the same logic as the main assistant but with the extractor prompt
    
    ai_raw_response = await call_gemini_direct(full_prompt)
    if not ai_raw_response:
        return

    # 5. Parse JSON Response
    try:
        # Clean up code blocks if AI included them
        clean_json = ai_raw_response.strip().replace('```json', '').replace('```', '')
        extracted_data = json.loads(clean_json)
        
        # 6. Map to Customer DB Fields
        # We only update fields that are NOT null and match our schema
        updates = {}
        if extracted_data.get('name'): updates['name'] = extracted_data['name']
        if extracted_data.get('city'): updates['city'] = extracted_data['city']
        
        # Store complex data in metadata
        metadata = {}
        if extracted_data.get('interests'): metadata['interests'] = extracted_data['interests']
        if extracted_data.get('budget_info'): metadata['budget_info'] = extracted_data['budget_info']
        if extracted_data.get('urgency'): metadata['urgency'] = extracted_data['urgency']
        if extracted_data.get('notes'): metadata['notes'] = extracted_data['notes']
        
        if metadata:
            updates['metadata'] = metadata
            
        if updates:
            success = update_customer_profile(phone, updates)
            if success:
                logger.info(f"CRM Updated for {phone}: {updates.get('name', 'N/A')}")
            else:
                logger.error(f"Failed to update CRM for {phone}")
                
    except Exception as e:
        logger.error(f"Error parsing extracted data: {e}")
        logger.debug(f"Raw Response: {ai_raw_response}")

if __name__ == "__main__":
    # Test block (manual run)
    pass

