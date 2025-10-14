# FamApp API Endpoints - Quick Reference

**Backend:** Django REST Framework + JWT Auth
**Base URL:** `http://localhost:8000/api/v1/`
**Auth:** JWT Bearer tokens

---

## Authentication & User Management

### Register New User
```http
POST /api/auth/register/
```
**Body:** `{ email, first_name, last_name, password, password_confirm, invitation_token? }`
**Response:** OTP sent to email
**Note:** Optional `invitation_token` for auto-join family on verification

### Verify OTP
```http
POST /api/auth/verify-otp/
```
**Body:** `{ email, otp }`
**Response:** JWT tokens + user data + families
**Note:** Creates user's own family + accepts invitation if token provided

### Login
```http
POST /api/auth/login/
```
**Body:** `{ email, password }`
**Response:** JWT tokens + user data

### Refresh Token
```http
POST /api/auth/token/refresh/
```
**Body:** `{ refresh }`
**Response:** New access token

### Current User
```http
GET /api/v1/users/me/
```
**Auth:** Required
**Response:** Current user details

---

## Family Management

### List User's Families
```http
GET /api/v1/families/
```
**Auth:** Required
**Response:** All families user belongs to

### Get Family Details
```http
GET /api/v1/families/{public_id}/
```
**Auth:** Required (must be family member)
**Response:** Family details + members

### Update Family
```http
PATCH /api/v1/families/{public_id}/
```
**Auth:** Required (ORGANIZER only)
**Body:** `{ name?, description? }`
**Response:** Updated family

### Delete Family
```http
DELETE /api/v1/families/{public_id}/
```
**Auth:** Required (ORGANIZER only)
**Response:** 204 No Content

---

## Family Members

### List Family Members
```http
GET /api/v1/families/{public_id}/members/
```
**Auth:** Required (must be family member)
**Response:** Array of family members with roles

### Update Member Role
```http
PATCH /api/v1/families/{public_id}/members/{member_id}/
```
**Auth:** Required (ORGANIZER only)
**Body:** `{ role: "parent" | "child" }`
**Response:** Updated member
**Note:** Cannot change ORGANIZER role

### Remove Member
```http
DELETE /api/v1/families/{public_id}/members/{member_id}/
```
**Auth:** Required (ORGANIZER only)
**Response:** 204 No Content
**Note:** Cannot remove ORGANIZER

---

## Family Invitations

### Create Invitation
```http
POST /api/v1/families/{public_id}/invitations/
```
**Auth:** Required (ORGANIZER only)
**Body:** `{ invitee_email, role: "parent" | "child" }`
**Response:** Invitation details + sends email
**Note:** Cannot invite ORGANIZER role

### List Family Invitations
```http
GET /api/v1/families/{public_id}/invitations/?status={pending|accepted|declined|expired}
```
**Auth:** Required (ORGANIZER only)
**Response:** Array of invitations

### Cancel Invitation
```http
DELETE /api/v1/invitations/{token}/
```
**Auth:** Required (ORGANIZER only)
**Response:** 204 No Content

### Accept Invitation (Existing User)
```http
POST /api/v1/invitations/{token}/accept/
```
**Auth:** Required (email must match invitee)
**Response:** Family details + membership

### Decline Invitation
```http
POST /api/v1/invitations/{token}/decline/
```
**Auth:** Required (email must match invitee)
**Response:** Success message

---

## Quick Migration Notes

### Supabase → Django Mapping

| Supabase Feature | Django Equivalent |
|------------------|-------------------|
| `supabase.auth.signUp()` | `POST /api/auth/register/` + `POST /api/auth/verify-otp/` |
| `supabase.auth.signIn()` | `POST /api/auth/login/` |
| `supabase.auth.getUser()` | `GET /api/v1/users/me/` |
| `supabase.auth.refreshSession()` | `POST /api/auth/token/refresh/` |
| `supabase.from('families')` | `/api/v1/families/` |
| `supabase.from('family_members')` | `/api/v1/families/{id}/members/` |

### Key Differences

1. **Authentication:**
   - Supabase: Automatic session management
   - Django: Manual JWT token storage & refresh

2. **OTP Verification:**
   - Supabase: Magic links
   - Django: 6-digit OTP codes (better for mobile!)

3. **Family Creation:**
   - Automatically created on user registration
   - User becomes ORGANIZER of their own family

4. **Invitations:**
   - Email-based with beautiful HTML templates
   - Token-based acceptance
   - Can accept during signup (auto-join)

### Response Format

All responses use consistent format:

**Success:**
```json
{
  "id": 123,
  "public_id": "uuid-here",
  ...data
}
```

**Error:**
```json
{
  "detail": "Error message"
}
```

Or field-specific:
```json
{
  "field_name": ["Error message"]
}
```

### JWT Token Usage

**Store tokens securely:**
```typescript
// After login/register
const { access, refresh } = response.data;
await SecureStore.setItemAsync('access_token', access);
await SecureStore.setItemAsync('refresh_token', refresh);
```

**Add to requests:**
```typescript
axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
```

**Refresh when expired:**
```typescript
if (error.response?.status === 401) {
  const newAccess = await refreshToken();
  // Retry original request
}
```

---

## Complete Endpoint List

### Authentication (No Auth Required)
- `POST /api/auth/register/`
- `POST /api/auth/verify-otp/`
- `POST /api/auth/login/`
- `POST /api/auth/token/refresh/`

### Users (Auth Required)
- `GET /api/v1/users/me/`
- `PATCH /api/v1/users/me/`

### Families (Auth Required)
- `GET /api/v1/families/`
- `GET /api/v1/families/{id}/`
- `PATCH /api/v1/families/{id}/`
- `DELETE /api/v1/families/{id}/`

### Family Members (Auth Required)
- `GET /api/v1/families/{id}/members/`
- `PATCH /api/v1/families/{id}/members/{member_id}/`
- `DELETE /api/v1/families/{id}/members/{member_id}/`

### Invitations
- `POST /api/v1/families/{id}/invitations/` (ORGANIZER)
- `GET /api/v1/families/{id}/invitations/` (ORGANIZER)
- `DELETE /api/v1/invitations/{token}/` (ORGANIZER)
- `POST /api/v1/invitations/{token}/accept/` (Auth)
- `POST /api/v1/invitations/{token}/decline/` (Auth)

---

## Testing Endpoints

**Local Development:**
- Backend: `http://localhost:8000`
- Mailpit (emails): `http://localhost:8025`

**Postman Collection:** (Coming soon)

**Quick Test:**
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","first_name":"Test","last_name":"User","password":"Test123!","password_confirm":"Test123!"}'

# Check email in Mailpit for OTP
# http://localhost:8025

# Verify OTP
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","otp":"123456"}'
```

---

## Migration Checklist

- [ ] Replace Supabase client with axios/fetch
- [ ] Implement JWT token storage (SecureStore)
- [ ] Implement token refresh logic
- [ ] Update auth flow (2-step: register → OTP)
- [ ] Update family queries to use public_id
- [ ] Add invitation acceptance flow
- [ ] Update error handling for Django format
- [ ] Test all CRUD operations
- [ ] Verify member management works
- [ ] Test invitation system end-to-end

---

## Need More Details?

- **Full Invitation API:** `docs/API_INVITATION_GUIDE.md`
- **Database Schema:** Check Django models
- **All Tests:** `backend/apps/users/tests/` and `backend/apps/families/tests/`

**System is production-ready! Let's migrate that mobile app!** 🚀
