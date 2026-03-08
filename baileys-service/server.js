import makeWASocket, { 
  useMultiFileAuthState, 
  DisconnectReason,
  fetchLatestBaileysVersion
} from '@whiskeysockets/baileys'
import express from 'express'
import { Boom } from '@hapi/boom'
import qrcode from 'qrcode-terminal'
import pino from 'pino'

const app = express()
app.use(express.json())

const PORT = process.env.PORT || 3000 // Changed default to 3000 to match setup
const logger = pino({ level: 'info' })

let sock = null
let qrCodeData = null
let connectionStatus = 'disconnected'
let webhookUrl = process.env.WEBHOOK_URL || 'http://localhost:8080/webhook/whatsapp'

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

// Store disabled - optional feature

async function connectToWhatsApp() {
  const { state, saveCreds } = await useMultiFileAuthState('auth_info')
  const { version } = await fetchLatestBaileysVersion()

  sock = makeWASocket({
    version,
    logger,
    printQRInTerminal: true,
    auth: state,
    getMessage: async () => undefined
  })
  
  // store.bind(sock.ev) - disabled

  sock.ev.on('creds.update', saveCreds)

  // Message Listener & Forwarder
  sock.ev.on('messages.upsert', async ({ messages, type }) => {
    if (type === 'notify') {
      for (const msg of messages) {
        if (!msg.message) continue
        
        try {
          // Forward to Main Server (CRM)
          const response = await fetch(webhookUrl, {
            method: 'POST',
            body: JSON.stringify({ data: { message: msg.message, key: msg.key } }),
            headers: { 'Content-Type': 'application/json' }
          })
          
          // HANDLE REPLY FROM SERVER (NEW)
          const responseData = await response.json()
          if (responseData && responseData.reply) {
             logger.info(`🤖 Sending AI Reply: ${responseData.reply}`)
             await sock.sendMessage(msg.key.remoteJid, { text: responseData.reply })
          }
          
          logger.info(`Webhook sent: ${response.status}`)
        } catch (e) {
          logger.error(`Webhook forward failed: ${e.message}`)
        }
      }
    }
  })

  sock.ev.on('connection.update', async (update) => {
    // ... existing connection logic ...
    const { connection, lastDisconnect, qr } = update
    
    if (qr) {
      qrCodeData = qr
      logger.info('QR Code generated!')
    }

    if (connection === 'close') {
      connectionStatus = 'disconnected'
      
      // Check if it was a logout
      const wasLoggedOut = (lastDisconnect?.error instanceof Boom) 
        && lastDisconnect.error.output.statusCode === DisconnectReason.loggedOut
      
      if (wasLoggedOut) {
        logger.info('⚠️ Logged out. Clearing session and generating new QR code...')
        qrCodeData = null  // Clear old QR
        
        // Delete old session files to force fresh start
        try {
          const fs = await import('fs')
          const path = await import('path')
          const authPath = path.join(process.cwd(), 'auth_info')
          
          if (fs.existsSync(authPath)) {
            const files = fs.readdirSync(authPath)
            for (const file of files) {
              fs.unlinkSync(path.join(authPath, file))
            }
            logger.info('✅ Old session files deleted')
          }
        } catch (err) {
          logger.error('Failed to delete session files:', err.message)
        }
      } else {
        logger.info('Connection closed. Reconnecting...')
      }
      
      // Always reconnect to generate new QR or restore connection
      await connectToWhatsApp()
      
    } else if (connection === 'open') {
      connectionStatus = 'connected'
      qrCodeData = null  // Clear QR when connected
      logger.info('✅ Connected to WhatsApp!')
    }
  })

  sock.ev.on('messages.upsert', async ({ messages }) => {
    const msg = messages[0]
    if (!msg.message || msg.key.fromMe) return

    logger.info('New message received:', msg)
    
    // Check if contact exists in store
    const remoteJid = msg.key.remoteJid
    const contact = store.contacts[remoteJid] || {}
    const isSavedContact = !!contact.name || !!contact.notify  // Basic check, 'name' usually set if in phonebook

    // Prepare Payload
    const payload = {
        data: {
            message: msg.message,
            key: msg.key,
            pushName: msg.pushName,
            isContact: isSavedContact // <--- HERE IS THE CRITICAL FLAG
        }
    }
    
    // Send to Python Webhook
    try {
        const axios = (await import('axios')).default
        const WEBHOOK_URL = process.env.WEBHOOK_URL || 'http://localhost:8080/webhook/whatsapp'
        await axios.post(WEBHOOK_URL, payload)
    } catch (e) {
        logger.error('Webhook failed:', e.message)
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
    // Generate QR code as data URL (base64 image)
    const QRCode = (await import('qrcode')).default
    const qrImage = await QRCode.toDataURL(qrCodeData)
    
    res.json({
      success: true,
      qr: qrCodeData,
      qrImage: qrImage,
      message: 'Scan this QR code with WhatsApp'
    })
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: error.message 
    })
  }
})

app.get('/qr-image', async (req, res) => {
  if (!qrCodeData) {
    return res.send('<h1>No QR Code available</h1><p>Already connected or not initialized.</p>')
  }

  try {
    const QRCode = (await import('qrcode')).default
    const qrImage = await QRCode.toDataURL(qrCodeData)
    
    res.send(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>WhatsApp QR Code</title>
          <style>
            body {
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              min-height: 100vh;
              margin: 0;
              font-family: Arial, sans-serif;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
              background: white;
              padding: 40px;
              border-radius: 20px;
              box-shadow: 0 20px 60px rgba(0,0,0,0.3);
              text-align: center;
            }
            h1 {
              color: #333;
              margin-bottom: 20px;
            }
            img {
              max-width: 300px;
              border: 10px solid #25D366;
              border-radius: 10px;
            }
            p {
              color: #666;
              margin-top: 20px;
            }
          </style>
        </head>
        <body>
          <div class="container">
            <h1>📱 Scan QR Code</h1>
            <img src="${qrImage}" alt="WhatsApp QR Code">
            <p>Open WhatsApp > Settings > Linked Devices > Link a Device</p>
          </div>
        </body>
      </html>
    `)
  } catch (error) {
    res.status(500).send(`<h1>Error: ${error.message}</h1>`)
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
      return res.status(400).json({ 
        success: false, 
        message: 'Phone and message are required' 
      })
    }

    if (connectionStatus !== 'connected') {
      return res.status(503).json({ 
        success: false, 
        message: 'WhatsApp not connected' 
      })
    }

    const jid = phone.includes('@') ? phone : `${phone}@s.whatsapp.net`
    await sock.sendMessage(jid, { text: message })

    res.json({ 
      success: true, 
      message: 'Message sent successfully',
      to: phone 
    })
  } catch (error) {
    logger.error('Send message error:', error)
    res.status(500).json({ 
      success: false, 
      message: error.message 
    })
  }
})

app.post('/disconnect', async (req, res) => {
  try {
    if (sock) {
      await sock.logout()
      connectionStatus = 'disconnected'
      qrCodeData = null
    }
    res.json({ success: true, message: 'Disconnected successfully' })
  } catch (error) {
    res.status(500).json({ success: false, message: error.message })
  }
})

app.post('/reset', async (req, res) => {
  try {
    // Logout first
    if (sock) {
      try {
        await sock.logout()
      } catch (e) {
        logger.warn('Logout failed, continuing with reset:', e.message)
      }
    }
    
    // Delete session files
    const fs = await import('fs')
    const path = await import('path')
    const authPath = path.join(process.cwd(), 'auth_info')
    
    if (fs.existsSync(authPath)) {
      const files = fs.readdirSync(authPath)
      for (const file of files) {
        fs.unlinkSync(path.join(authPath, file))
      }
      logger.info('✅ Session files deleted')
    }
    
    // Reset state
    connectionStatus = 'disconnected'
    qrCodeData = null
    sock = null
    
    // Reconnect to generate new QR
    await connectToWhatsApp()
    
    res.json({ 
      success: true, 
      message: 'Session reset. New QR code will be generated shortly.' 
    })
  } catch (error) {
    logger.error('Reset error:', error)
    res.status(500).json({ success: false, message: error.message })
  }
})

// ============================================
// Pairing Code Logic
// ============================================

app.post('/pairing-code', async (req, res) => {
  try {
    const { phone } = req.body

    if (!phone) {
      return res.status(400).json({ 
        success: false, 
        message: 'Phone number is required' 
      })
    }

    if (connectionStatus === 'connected') {
      return res.status(400).json({ 
        success: false, 
        message: 'Already connected' 
      })
    }
    
    if (!sock) {
         return res.status(503).json({ 
        success: false, 
        message: 'Socket not initialized' 
      })
    }

    // Ensure phone number format (remove non-digits)
    const formattedPhone = phone.replace(/[^0-9]/g, '')

    // Request pairing code from Baileys
    const code = await sock.requestPairingCode(formattedPhone)

    res.json({ 
      success: true, 
      code: code?.toUpperCase(),
      message: 'Pairing code generated successfully'
    })

  } catch (error) {
    logger.error('Pairing code error:', error)
    res.status(500).json({ 
      success: false, 
      message: error.message || 'Failed to generate pairing code'
    })
  }
})

// ============================================
// Start Server
// ============================================

app.listen(PORT, async () => {
  logger.info(`🚀 Server running on port ${PORT}`)
  await connectToWhatsApp()
})
