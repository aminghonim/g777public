# Baileys WhatsApp Service

WhatsApp API service using Baileys library for G777 Project.

## Features

- ✅ QR Code connection
- ✅ Send/receive messages
- ✅ Auto-reconnect
- ✅ REST API
- ✅ Cloud Run ready

## API Endpoints

### GET /health
Check service health

### GET /qr
Get QR code for WhatsApp connection

### GET /status
Check connection status

### POST /send
Send WhatsApp message

**Body:**
```json
{
  "phone": "201234567890",
  "message": "Hello!"
}
```

### POST /disconnect
Logout from WhatsApp

## Local Development

```bash
npm install
npm start
```

## Deploy to Cloud Run

```bash
gcloud run deploy baileys-service \
  --source . \
  --region=europe-west1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --timeout=300
```

## Environment Variables

- `PORT` - Server port (default: 8080)
