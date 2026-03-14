import makeWASocket, { 
  useMultiFileAuthState, 
  DisconnectReason,
  fetchLatestBaileysVersion,
  downloadMediaMessage
} from '@whiskeysockets/baileys'
import express from 'express'
import { Boom } from '@hapi/boom'
import pino from 'pino'
import QRCode from 'qrcode'

const app = express()
app.use(express.json())

const PORT = process.env.PORT || 3000
const logger = pino({ level: 'info' })

let sock = null
let qrCodeData = null
let connectionStatus = 'disconnected'

// Default to Python Backend on 8000
let webhookUrl = process.env.WEBHOOK_URL || 'http://localhost:8000/webhook/whatsapp'

console.log(`[INIT] Webhook URL: ${webhookUrl}`)

// ============================================
// Webhook Configuration Endpoint
// ============================================
app.patch('/webhook/set', (req, res) => {
  const { url } = req.body
  if (url) {
    webhookUrl = url
    logger.info(`Webhook URL updated to: ${webhookUrl}`)
    res.json({ success: true, url: webhookUrl })
  } else {
    res.status(400).json({ success: false, message: 'URL is required' })
  }
})

// ============================================
// Baileys Setup
// ============================================

async function connectToWhatsApp() {
  const { state, saveCreds } = await useMultiFileAuthState('auth_info')
  const { version } = await fetchLatestBaileysVersion()

  logger.info(`Starting Baileys with version: ${version.join('.')}`)

  sock = makeWASocket({
    version,
    logger,
    printQRInTerminal: true,
    auth: state,
    getMessage: async () => undefined
  })
  
  sock.ev.on('creds.update', saveCreds)

  // ============================================
  // Resilient Message Queue (Pitfall 3: Graceful Degradation)
  // ============================================
  const MAX_RETRY_QUEUE = 100
  const retryQueue = []

  async function forwardToWebhook(payload, retryCount = 0) {
    const MAX_RETRIES = 3
    const RETRY_DELAY_MS = 2000
    try {
      const response = await fetch(webhookUrl, {
        method: 'POST',
        body: JSON.stringify(payload),
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(10000)
      })
      logger.info(`Webhook response: ${response.status}`)
      return response
    } catch (e) {
      if (retryCount < MAX_RETRIES) {
        logger.warn(`Webhook attempt ${retryCount + 1}/${MAX_RETRIES} failed: ${e.message}. Retrying...`)
        await new Promise(r => setTimeout(r, RETRY_DELAY_MS * (retryCount + 1)))
        return forwardToWebhook(payload, retryCount + 1)
      }
      logger.error(`Webhook unreachable after ${MAX_RETRIES} retries. Queuing message.`)
      if (retryQueue.length < MAX_RETRY_QUEUE) {
        retryQueue.push({ payload, timestamp: Date.now() })
      } else {
        logger.warn(`Retry queue full (${MAX_RETRY_QUEUE}). Dropping oldest message.`)
        retryQueue.shift()
        retryQueue.push({ payload, timestamp: Date.now() })
      }
      return null
    }
  }

  // Unified Message Listener & Forwarder
  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type !== 'notify') return

    for (const msg of messages) {
      if (!msg.message) continue
      if (msg.key.fromMe) {
          logger.info('Skipping own message')
          continue
      }

      logger.info(`New message from ${msg.key.remoteJid}: ${JSON.stringify(msg.message).substring(0, 100)}...`)
      
      try {
        const payload = {
            event: 'messages.upsert',
            instance: 'local',
            data: {
                message: msg.message,
                key: msg.key,
                pushName: msg.pushName || 'WhatsApp User',
                timestamp: msg.messageTimestamp,
                status: 'RECEIVED'
            }
        }

        logger.info(`Forwarding to Webhook: ${webhookUrl}`)
        const response = await forwardToWebhook(payload)

        if (response) {
          const responseData = await response.json().catch(() => ({}))
          if (responseData && responseData.reply) {
            logger.info(`Sending AI Reply from webhook response: ${responseData.reply}`)
            await sock.sendMessage(msg.key.remoteJid, { text: responseData.reply })
          }
        }
      } catch (e) {
        logger.error(`Message processing error: ${e.message}`)
      }
    }
  })


  sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect, qr } = update
    
    if (qr) {
      qrCodeData = qr
      logger.info('QR Code generated!')
    }

    if (connection === 'close') {
      connectionStatus = 'disconnected'
      
      const statusCode = lastDisconnect?.error?.output?.statusCode
      const wasLoggedOut = statusCode === DisconnectReason.loggedOut
      
      if (wasLoggedOut) {
        logger.info('⚠️ Logged out. Clearing session...')
        qrCodeData = null
        // Force cleanup will happen in reset endpoint
      } else {
        logger.info(`Connection closed (Reason: ${statusCode}). Reconnecting...`)
        setTimeout(connectToWhatsApp, 3000)
      }
    } else if (connection === 'open') {
      connectionStatus = 'connected'
      qrCodeData = null
      logger.info('✅ Connected to WhatsApp!')
    }
  })
}

// ============================================
// API Endpoints
// ============================================

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    connection: connectionStatus,
    timestamp: new Date().toISOString()
  })
})

app.get('/qr', async (req, res) => {
  if (!qrCodeData) {
    return res.status(404).json({ 
      success: false, 
      message: 'No QR code available. Already connected or not initialized.' 
    })
  }

  try {
    const qrImage = await QRCode.toDataURL(qrCodeData)
    res.json({
      success: true,
      qr: qrCodeData,
      qrImage: qrImage,
      message: 'Scan this QR code with WhatsApp'
    })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

app.get('/status', (req, res) => {
  res.json({
    connected: connectionStatus === 'connected',
    status: connectionStatus,
    user: sock?.user || null
  })
})

app.post('/send', async (req, res) => {
  try {
    const { phone, message } = req.body

    if (!phone || !message) {
      return res.status(400).json({ success: false, message: 'Phone and message are required' })
    }

    const jid = phone.includes('@') ? phone : `${phone}@s.whatsapp.net`
    await sock.sendMessage(jid, { text: message })

    res.json({ success: true, message: 'Message sent successfully' })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

app.post('/download', async (req, res) => {
  try {
    const { key, message } = req.body;
    if (!message || !key) {
      return res.status(400).json({ success: false, error: 'Both key and message are required' });
    }

    // Smart Extraction: If original message is a reply containing a quoted media message,
    // we automatically target the quoted message for decryption.
    let targetMessage = message;
    if (message.extendedTextMessage?.contextInfo?.quotedMessage) {
      targetMessage = message.extendedTextMessage.contextInfo.quotedMessage;
      logger.info('Extracting media from quotedMessage (Reply detected)');
    }

    const msg = { key, message: targetMessage };
    const buffer = await downloadMediaMessage(
      msg,
      'buffer',
      { },
      { logger }
    );
    
    if (!buffer) {
      return res.status(404).json({ success: false, error: 'Could not download media' });
    }

    const base64 = buffer.toString('base64');
    res.json({ success: true, base64 });
  } catch (error) {
    logger.error(`Media download error: ${error.message}`);
    res.status(500).json({ success: false, error: error.message });
  }
})

app.post('/logout', async (req, res) => {
  try {
    if (sock) await sock.logout()
    res.json({ success: true })
  } catch (e) {
    res.status(500).json({ error: e.message })
  }
})

app.post('/reset', async (req, res) => {
  try {
    if (sock) {
       try { await sock.logout() } catch(e) {}
    }
    
    const fs = await import('fs')
    const path = await import('path')
    const authPath = path.join(process.cwd(), 'auth_info')
    
    if (fs.existsSync(authPath)) {
      const files = fs.readdirSync(authPath);
      for (const file of files) {
        fs.rmSync(path.join(authPath, file), { recursive: true, force: true });
      }
    }
    
    connectionStatus = 'disconnected'
    qrCodeData = null
    sock = null
    
    setTimeout(connectToWhatsApp, 2000)
    
    res.json({ success: true, message: 'Session reset' })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

app.post('/pairing-code', async (req, res) => {
  try {
    const { phone } = req.body
    if (!phone || !sock) return res.status(400).json({ message: 'Phone or Socket missing' })

    const code = await sock.requestPairingCode(phone.replace(/[^0-9]/g, ''))
    res.json({ success: true, code: code?.toUpperCase() })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

app.listen(PORT, () => {
  logger.info(`🚀 Baileys Bridge running on port ${PORT}`)
  connectToWhatsApp().catch(err => logger.error('Startup failed:', err))
})
