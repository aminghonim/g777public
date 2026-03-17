# Knowledge Item: WhatsApp Media Decryption & Handling

> **Purpose:** Document the definitive patterns for handling WhatsApp media messages (images, videos, documents) via Baileys. Required by GEMINI.md Rule #14.

## Metadata

- **KI-ID:** `KI-WHATSAPP-MEDIA-001`
- **Component:** Baileys Bridge (Node.js) / Backend Integration
- **Date Added:** 2026-03-15
- **Associated Skill:** `baileys-service/server.js`

---

## Architecture Overview

WhatsApp media handling in G777 follows a **Bridge Pattern**:
1. **Baileys Bridge** (`baileys-service/server.js`) handles raw WhatsApp connection
2. **Python Backend** processes media via `/download` endpoint
3. **Media Decryption** happens at the Baileys level using `downloadMediaMessage()`

---

## Pattern 1: Media Message Detection

### The Pattern
Detect media messages by checking message types in the `messages.upsert` event.

### Implementation (Baileys)
```javascript
sock.ev.on('messages.upsert', async ({ messages, type }) => {
  if (type !== 'notify') return
  
  for (const msg of messages) {
    if (!msg.message) continue
    if (msg.key.fromMe) continue  // Skip own messages
    
    // Detect media message types
    const hasMedia = msg.message.imageMessage || 
                     msg.message.videoMessage || 
                     msg.message.documentMessage ||
                     msg.message.audioMessage ||
                     msg.message.stickerMessage
    
    if (hasMedia) {
      logger.info(`Media message received from ${msg.key.remoteJid}`)
      // Forward to webhook with media flag
    }
  }
})
```

### Media Message Types
| Type | Property | Notes |
|------|----------|-------|
| Image | `message.imageMessage` | JPEG/PNG |
| Video | `message.videoMessage` | MP4 |
| Document | `message.documentMessage` | PDF, DOC, etc. |
| Audio | `message.audioMessage` | OGG, MP3 |
| Sticker | `message.stickerMessage` | WEBP |

---

## Pattern 2: Media Download Endpoint

### The Pattern
Expose a `/download` endpoint that receives message key and returns Base64-encoded media.

### Implementation
```javascript
app.post('/download', async (req, res) => {
  try {
    const { key, message } = req.body;
    if (!message || !key) {
      return res.status(400).json({ 
        success: false, 
        error: 'Both key and message are required' 
      });
    }

    // Smart Extraction: Handle quoted messages (replies)
    let targetMessage = message;
    if (message.extendedTextMessage?.contextInfo?.quotedMessage) {
      targetMessage = message.extendedTextMessage.contextInfo.quotedMessage;
      logger.info('Extracting media from quotedMessage (Reply detected)');
    }

    const msg = { key, message: targetMessage };
    const buffer = await downloadMediaMessage(
      msg,
      'buffer',           // Return type: 'buffer' | 'stream'
      { },                // Options
      { logger }          // Logger for debugging
    );
    
    if (!buffer) {
      return res.status(404).json({ 
        success: false, 
        error: 'Could not download media' 
      });
    }

    const base64 = buffer.toString('base64');
    res.json({ success: true, base64 });
    
  } catch (error) {
    logger.error(`Media download error: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
})
```

### Key Points
- **Smart Extraction:** Automatically detect and extract media from quoted messages
- **Buffer Mode:** Returns complete buffer (not stream) for easier Base64 encoding
- **Error Handling:** Return 404 if media unavailable, 500 for errors

---

## Pattern 3: Python Backend Integration

### The Pattern
Python backend calls the Baileys `/download` endpoint to retrieve media content.

### Implementation (Python)
```python
import requests
import base64

class WhatsAppMediaHandler:
    def __init__(self, baileys_url: str = "http://localhost:3000"):
        self.baileys_url = baileys_url
        
    def download_media(self, message_key: dict, message_data: dict) -> bytes:
        """
        Download media from WhatsApp via Baileys bridge.
        
        Args:
            message_key: WhatsApp message key (remoteJid, id, etc.)
            message_data: Full message object containing media
            
        Returns:
            Decrypted media as bytes
        """
        response = requests.post(
            f"{self.baileys_url}/download",
            json={
                "key": message_key,
                "message": message_data
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return base64.b64decode(data["base64"])
        
        raise MediaDownloadError(f"Failed to download: {response.text}")
```

---

## Pattern 4: Quoted Message Handling

### The Problem
Users often reply to media messages with text. The media is in the `quotedMessage`, not the main message.

### The Solution (Smart Extraction)
```javascript
// Check if message is a reply containing quoted media
if (message.extendedTextMessage?.contextInfo?.quotedMessage) {
  const quoted = message.extendedTextMessage.contextInfo.quotedMessage;
  
  // Check if quoted message has media
  if (quoted.imageMessage || quoted.videoMessage || quoted.documentMessage) {
    targetMessage = quoted;  // Use quoted message for media extraction
    logger.info('Media found in quoted message');
  }
}
```

---

## Error Handling Patterns

### Common Errors
| Error | Cause | Solution |
|-------|-------|----------|
| `Could not download media` | Media expired or deleted | Return 404, log for analysis |
| `Bad MAC` | Decryption failed | Retry once, then fail |
| `Message not found` | Invalid key | Validate key format first |

### Retry Logic
```javascript
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 2000;

async function downloadWithRetry(msg, retryCount = 0) {
  try {
    return await downloadMediaMessage(msg, 'buffer', {}, { logger });
  } catch (e) {
    if (retryCount < MAX_RETRIES && e.message.includes('Bad MAC')) {
      await new Promise(r => setTimeout(r, RETRY_DELAY_MS));
      return downloadWithRetry(msg, retryCount + 1);
    }
    throw e;
  }
}
```

---

## Integration Checklist

- [ ] Baileys bridge exposes `/download` endpoint
- [ ] Python backend can call Baileys endpoint
- [ ] Media detection in `messages.upsert` handler
- [ ] Quoted message extraction implemented
- [ ] Base64 encoding for binary transport
- [ ] Error handling for expired media
- [ ] Timeout configuration (30s recommended)

---

## References

- `baileys-service/server.js` - Baileys implementation
- `@whiskeysockets/baileys` - Official Baileys docs
- `backend/wa_gateway.py` - Python WhatsApp integration
- `backend/message_processor.py` - Message handling logic
