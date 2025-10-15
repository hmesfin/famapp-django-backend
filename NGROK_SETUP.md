# Ngrok Setup for Django + Mailpit

## Current Configuration

### Django Backend (Port 8000)
- **Local Access**: `http://localhost:8000`
- **Ngrok Tunnel**: `https://intersticed-latently-bertie.ngrok-free.dev`
- **Mobile App**: Uses ngrok URL for API calls and deep links

### Nginx Reverse Proxy (Port 8000)
- **Routes**: Proxies both Django and Mailpit through single port
- **Django**: `http://localhost:8000/` → Django backend
- **Mailpit**: `http://localhost:8000/mailpit/` → Mailpit web UI

### Mailpit (Email Testing)
- **Access via Nginx**: `http://localhost:8000/mailpit/`
- **Access via Ngrok**: `https://intersticed-latently-bertie.ngrok-free.dev/mailpit/`
- **Purpose**: View invitation emails sent by Django

## How It Works

1. **Django backend** runs in Docker on internal port 8000
2. **Mailpit** runs in Docker on internal port 8025
3. **Nginx** reverse proxy runs on port 8000 (exposed), routes traffic:
   - `/` → Django backend
   - `/mailpit/` → Mailpit web UI
4. **Ngrok** tunnels port 8000 to `https://intersticed-latently-bertie.ngrok-free.dev`
5. **Mobile app** connects to ngrok URL (configured in `famapp-mobile/src/config/constants.ts`)
6. **You can access Mailpit** from your mobile device at `https://intersticed-latently-bertie.ngrok-free.dev/mailpit/`

## Starting the Services

### 1. Rebuild Docker Services (First Time Only)
```bash
cd /home/hmesfin/dev/active/famapp-backend
docker compose down
docker compose build
docker compose up
```

### 2. Start Ngrok Tunnel
```bash
ngrok http 8000
```

**Note**: Make sure the ngrok URL matches `BACKEND_URL` in `.envs/.local/.django`

### 3. Verify Services Are Running
- Django API: `http://localhost:8000/api/v1/`
- Mailpit: `http://localhost:8000/mailpit/`
- Via Ngrok: `https://intersticed-latently-bertie.ngrok-free.dev/mailpit/`

## Accessing Services

| Service | Local URL | Ngrok URL (Mobile Access) | Purpose |
|---------|-----------|---------------------------|---------|
| Django Backend | `http://localhost:8000` | `https://intersticed-latently-bertie.ngrok-free.dev` | API for mobile app |
| Django Admin | `http://localhost:8000/admin` | `https://intersticed-latently-bertie.ngrok-free.dev/admin` | User management |
| Mailpit Web UI | `http://localhost:8000/mailpit/` | `https://intersticed-latently-bertie.ngrok-free.dev/mailpit/` | View test emails **FROM MOBILE!** |
| Flower (Celery) | `http://localhost:5555` | N/A | Monitor background tasks |
| Frontend (Vue) | `http://localhost:5173` | N/A | Web UI (optional) |

## Testing Invitation Emails

### Send an Invitation
1. Log into mobile app as organizer
2. Go to Family screen
3. Click "Invite Member"
4. Enter email and select role
5. Click "Send Invitation"

### View the Email (FROM YOUR MOBILE DEVICE!)
1. **On your mobile device**, open browser to:
   ```
   https://intersticed-latently-bertie.ngrok-free.dev/mailpit/
   ```
2. Click on the invitation email
3. The "Accept Invitation" button should link to:
   ```
   famapp://signup/{invitation-token}
   ```

### Test Deep Link (Direct from Mobile!)
1. **On your mobile device in Mailpit**, click the "Accept Invitation" button
2. Your device should prompt: "Open in FamApp?"
3. Click "Open" → App should open SignupScreen with invitation code pre-filled
4. No more copying UUIDs! 🎉

## Architecture Diagram

```
Mobile Device → Ngrok Tunnel → Nginx (Port 8000) → Django (Internal :8000)
                                                  → Mailpit (Internal :8025)

All via single ngrok URL!
```

## Environment Variables

The following environment variable is set in `.envs/.local/.django`:

```bash
BACKEND_URL=https://intersticed-latently-bertie.ngrok-free.dev
```

This is used by the invitation email task to generate the decline URL.

## Troubleshooting

### Ngrok URL Changed
If your ngrok URL changes, update these locations:

1. **Mobile app**: `famapp-mobile/src/config/constants.ts`
   ```typescript
   const NGROK_URL = 'https://your-new-url.ngrok-free.dev';
   ```

2. **Django settings**: `famapp-backend/backend/config/settings/local.py`
   ```python
   ALLOWED_HOSTS = [..., "your-new-url.ngrok-free.dev"]
   ```

3. **Django env**: `famapp-backend/.envs/.local/.django`
   ```bash
   BACKEND_URL=https://your-new-url.ngrok-free.dev
   ```

### Mobile App Can't Connect
- Verify ngrok tunnel is running: `ngrok http 8000`
- Check mobile app is using correct ngrok URL
- Check Django `ALLOWED_HOSTS` includes ngrok domain

### Emails Not Showing in Mailpit
- Verify Mailpit is running: `docker compose ps`
- Check Django email settings point to `mailpit` container
- View Django logs: `docker compose logs -f django`
