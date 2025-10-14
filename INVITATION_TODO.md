# TDD Plan: Family Invitation System

**Target**: Enable ORGANIZERS to invite family members by email with role assignment

---

## 📊 PROGRESS TRACKER

**Completed:** 11/11 phases (100%) 🎉🎉🎉
**Tests Passing:** 128 invitation tests + 622 total backend tests
**Status:** PRODUCTION READY + DOCUMENTED!

### Phase Status:
- ✅ **Phase A**: Invitation Model - COMPLETE (21 tests)
- ✅ **Phase B**: Invitation Serializers - COMPLETE (16 tests)
- ✅ **Phase C**: Invitation Creation Endpoint - COMPLETE (11 tests)
- ✅ **Phase D**: Invitation Listing & Management - COMPLETE (16 tests)
- ✅ **Phase E**: Invitation Acceptance Flow - COMPLETE (18 tests)
- ✅ **Phase F**: Invitation Email & Celery Task - COMPLETE (16 tests)
- ✅ **Phase G**: Signup with Invitation Flow - COMPLETE (14 tests)
- ✅ **Phase H**: Invitation Expiration & Cleanup - COMPLETE (16 tests)
- ✅ **Phase I**: Permission & Authorization - COMPLETE (covered in phases C-E)
- ✅ **Phase J**: Edge Cases & Data Integrity - COMPLETE (covered throughout)
- ✅ **Phase K**: Documentation & E2E Tests - COMPLETE

**MISSION ACCOMPLISHED! 🚀**
All 11 phases complete, system is production-ready and fully documented!

---

#### Phase A: Invitation Model (users app) ✅ COMPLETE

- [x] **TEST**: Invitation model creation ✅ **21 tests passing!**
  - [x] Write test: Create invitation with inviter, invitee_email, family, role
  - [x] Implement: `apps/users/models.py` - Invitation model (inheriting BaseModel)
  - [x] Write test: Invitation has token field (UUID)
  - [x] Implement: UUIDField with default=uuid4 (used in invitation link/code)
  - [x] Write test: Invitation has status (PENDING, ACCEPTED, DECLINED, EXPIRED, CANCELLED)
  - [x] Implement: CharField with TextChoices for status
  - [x] Write test: Invitation has role field (PARENT, CHILD) - ORGANIZER excluded
  - [x] Implement: CharField with choices (no ORGANIZER option for security)
  - [x] Write test: Invitation expires after 7 days
  - [x] Implement: DateTimeField for expires_at (auto-set to timezone.now() + 7 days in save())
  - [x] Write test: Foreign key to inviter (User), family (Family)
  - [x] Implement: ForeignKey relationships with on_delete=CASCADE
  - [x] Write test: Unique constraint (family, invitee_email, status=PENDING)
  - [x] Implement: UniqueConstraint for preventing duplicate pending invites
  - [x] Write test: invitee_email validation (valid email format)
  - [x] Implement: EmailField with validators
  - [x] Write test: Cannot invite existing family members
  - [x] Implement: Custom model validation in clean() method
  - [x] Write test: Invitation model has is_expired property
  - [x] Implement: @property method checking expires_at < timezone.now()

**Files created/modified:**
- `backend/apps/users/models.py` (Invitation model - 246 lines total)
- `backend/apps/users/tests/test_models.py` (21 new tests)
- `backend/apps/users/migrations/0005_invitation.py` (migration applied ✅)

#### Phase B: Invitation Serializers (users app) ✅ COMPLETE

- [x] **TEST**: Invitation serializers ✅ **16 tests passing!**
  - [x] Write test: InvitationCreateSerializer validates email (required, valid format)
  - [x] Implement: `apps/users/api/serializers.py` - InvitationCreateSerializer
  - [x] Write test: InvitationCreateSerializer validates role (PARENT or CHILD only)
  - [x] Implement: ChoiceField excluding ORGANIZER
  - [x] Write test: InvitationCreateSerializer context-aware validation
  - [x] Implement: Accepts `family` in context for validation
  - [x] Write test: InvitationSerializer includes all fields (read-only)
  - [x] Implement: InvitationSerializer with inviter details, family name
  - [x] Write test: InvitationSerializer has is_expired computed field
  - [x] Implement: SerializerMethodField for is_expired
  - [x] Write test: Cannot invite user who is already a family member
  - [x] Implement: Custom validate() method checking FamilyMember.objects.filter()
  - [x] Write test: Cannot invite same email twice (pending invites)
  - [x] Implement: Custom validate() checking existing pending invitations
  - [x] Write test: Can re-invite after previous invitation accepted
  - [x] Implement: Validation only checks PENDING status

**Files created/modified:**
- `backend/apps/users/api/serializers.py` (3 new serializers: InvitationCreateSerializer, InviterSerializer, InvitationSerializer)
- `backend/apps/users/tests/test_serializers.py` (16 new tests)

**Serializers implemented:**
1. `InvitationCreateSerializer` - Create invitations with email/role validation
2. `InviterSerializer` - Nested serializer for inviter details
3. `InvitationSerializer` - Read-only with computed fields (is_expired, family_name)

#### Phase C: Invitation Creation Endpoint ✅ COMPLETE

- [x] **TEST**: POST /api/v1/families/{public_id}/invitations/ ✅ **11 tests passing!**
  - [x] Write test: ORGANIZER can create invitation
  - [x] Implement: Custom @action on FamilyViewSet (invitations with POST method)
  - [x] Write test: Returns 201 with invitation data (token, email, role, expires_at)
  - [x] Implement: Create Invitation with auto-generated token and expires_at
  - [x] Write test: Sends invitation email to invitee
  - [x] Implement: Celery task for sending invitation email (send_invitation_email.delay())
  - [x] Write test: Returns 400 if invitee already in family
  - [x] Implement: Serializer validation prevents duplicate members
  - [x] Write test: Returns 400 if pending invitation already exists
  - [x] Implement: Serializer validation checks for pending invites
  - [x] Write test: Returns 403 if user not ORGANIZER
  - [x] Implement: Manual permission check for IsFamilyAdmin
  - [x] Write test: Returns 404 if family not found
  - [x] Implement: get_object_or_404 for family lookup
  - [x] Write test: Auto-sets expires_at to 7 days from now
  - [x] Implement: expires_at auto-set in model.save()

**Files created/modified:**
- `backend/apps/shared/views.py` - Added invitations() action to FamilyViewSet
- `backend/apps/users/tests/api/test_invitation_api.py` - 11 new tests for creation endpoint

#### Phase D: Invitation Listing & Management Endpoints ✅ COMPLETE

- [x] **TEST**: GET /api/v1/families/{public_id}/invitations/ ✅ **7 tests passing!**
  - [x] Write test: ORGANIZER can list all invitations for family
  - [x] Implement: Custom @action on FamilyViewSet (invitations with GET method)
  - [x] Write test: Returns pending, accepted, declined invitations
  - [x] Implement: Queryset filtering by family
  - [x] Write test: Includes is_expired status for each invitation
  - [x] Implement: Serializer includes is_expired computed field
  - [x] Write test: Returns 403 if user not ORGANIZER
  - [x] Implement: Manual permission check for IsFamilyAdmin
  - [x] Write test: Filters by status (query param: ?status=pending)
  - [x] Implement: Queryset filtering by status parameter

- [x] **TEST**: DELETE /api/v1/invitations/{token}/ ✅ **9 tests passing!**
  - [x] Write test: ORGANIZER can cancel pending invitation
  - [x] Implement: InvitationViewSet with destroy action (custom lookup_field='token')
  - [x] Write test: Sets status to CANCELLED (soft cancel)
  - [x] Implement: Update status instead of deleting
  - [x] Write test: Returns 400 if invitation already accepted/declined
  - [x] Implement: Status validation before cancellation
  - [x] Write test: Returns 403 if user not ORGANIZER of invitation's family
  - [x] Implement: Permission check for inviter's family membership
  - [x] Write test: Returns 404 if invitation token not found
  - [x] Implement: get_object_or_404 with token lookup

**Files created/modified:**
- `backend/apps/users/api/views.py` - Created InvitationViewSet with destroy action
- `backend/config/api_router.py` - Registered InvitationViewSet
- `backend/apps/users/tests/api/test_invitation_api.py` - 16 new tests for list/cancel endpoints

#### Phase E: Invitation Acceptance Flow (Public Endpoint) ✅ COMPLETE

- [x] **TEST**: POST /api/v1/invitations/{token}/accept/ ✅ **11 tests passing!**
  - [x] Write test: Accept invitation creates FamilyMember
  - [x] Implement: Custom @action on InvitationViewSet (accept action)
  - [x] Write test: Accept invitation requires authentication
  - [x] Implement: IsAuthenticated permission
  - [x] Write test: Accept invitation creates membership with correct role
  - [x] Implement: FamilyMember.objects.create(user=request.user, family=invitation.family, role=invitation.role)
  - [x] Write test: Accept invitation sets status to ACCEPTED
  - [x] Implement: invitation.status = Invitation.Status.ACCEPTED
  - [x] Write test: Returns 400 if invitation expired
  - [x] Implement: Check invitation.is_expired before accepting
  - [x] Write test: Returns 400 if invitation already accepted
  - [x] Implement: Status validation (must be PENDING)
  - [x] Write test: Returns 400 if user email doesn't match invitee_email
  - [x] Implement: Email validation (request.user.email == invitation.invitee_email)
  - [x] Write test: Returns 400 if user already in family
  - [x] Implement: Check FamilyMember existence before creating
  - [x] Write test: Returns 200 with family data after acceptance
  - [x] Implement: Return family details using FamilySerializer

- [x] **TEST**: POST /api/v1/invitations/{token}/decline/ ✅ **7 tests passing!**
  - [x] Write test: Decline invitation sets status to DECLINED
  - [x] Implement: Custom @action on InvitationViewSet (decline action)
  - [x] Write test: Decline requires authentication
  - [x] Implement: IsAuthenticated permission
  - [x] Write test: Returns 400 if invitation expired
  - [x] Implement: Expiration check before declining
  - [x] Write test: Returns 400 if user email doesn't match invitee_email
  - [x] Implement: Email validation
  - [x] Write test: Returns 200 with message after declining
  - [x] Implement: Return success message

**Files created/modified:**
- `backend/apps/users/api/views.py` - Added accept/decline actions to InvitationViewSet
- `backend/apps/users/tests/api/test_invitation_api.py` - 18 new tests for accept/decline endpoints

#### Phase F: Invitation Email & Celery Task ✅ COMPLETE

- [x] **TEST**: Invitation email sending ✅ **16 tests passing!**
  - [x] Write test: send_invitation_email Celery task sends email
  - [x] Implement: `apps/users/tasks.py` - send_invitation_email(invitation_id)
  - [x] Write test: Email includes inviter name, family name, role
  - [x] Implement: Email template with invitation details
  - [x] Write test: Email includes invitation link/token
  - [x] Implement: Include invitation token in email body
  - [x] Write test: Email includes "Accept" and "Decline" buttons (links)
  - [x] Implement: HTML email with action buttons (gradient design!)
  - [x] Write test: Email includes expiration date (7 days)
  - [x] Implement: Template context with expires_at
  - [x] Write test: Task logs success/failure
  - [x] Implement: Logging in Celery task
  - [x] Write test: Task handles missing invitation gracefully
  - [x] Implement: Try-except around Invitation.objects.get()
  - [x] Write test: Task retries on failure (exponential backoff)
  - [x] Implement: @shared_task(bind=True, max_retries=3) with retry logic
  - [x] Write test: Email uses configurable FRONTEND_URL
  - [x] Implement: Settings-based frontend URL for accept/decline links

**Files created/modified:**
- `backend/apps/users/tasks.py` - Full implementation of send_invitation_email Celery task
- `backend/apps/templates/emails/invitation.html` - Beautiful HTML email template
- `backend/apps/templates/emails/invitation.txt` - Plain text fallback template
- `backend/config/settings/base.py` - Added FRONTEND_URL setting
- `backend/apps/users/tests/test_tasks.py` - 16 new tests for email task

#### Phase G: Signup with Invitation Flow ✅ COMPLETE

- [x] **TEST**: POST /api/auth/register/ with invitation_token ✅ **14 tests passing!**
  - [x] Write test: Register with invitation_token auto-joins family after verification
  - [x] Implement: Optional invitation_token parameter in UserCreateSerializer
  - [x] Write test: Validates invitation token exists and is pending
  - [x] Implement: Custom validate_invitation_token() method
  - [x] Write test: Validates email matches invitation's invitee_email (case-insensitive)
  - [x] Implement: Email validation in serializer
  - [x] Write test: Validates invitation not expired
  - [x] Implement: Expiration check in validation
  - [x] Write test: After OTP verification, accepts invitation automatically
  - [x] Implement: Modified OTP storage to include invitation_token (Redis dict)
  - [x] Write test: Returns family data in registration response
  - [x] Implement: Include both auto-created and invited families in verify-otp response
  - [x] Write test: User can join multiple families via invitations
  - [x] Verify: User has auto-created family (ORGANIZER) + invited family (role from invitation)

**Files created/modified:**
- `backend/apps/users/otp.py` - Extended to store invitation_token with OTP
- `backend/apps/users/api/serializers.py` - Added invitation_token field to UserCreateSerializer
- `backend/apps/users/api/auth_views.py` - Modified verify_otp to auto-accept invitation
- `backend/apps/users/tests/test_invitation_signup.py` - 14 new tests for signup flow

**The Money Shot Implementation:**
1. User receives invitation email
2. Clicks link or enters token during signup
3. Token validated and stored with OTP in Redis
4. After OTP verification → User auto-joins invited family
5. Response includes BOTH families (auto-created + invited)

#### Phase H: Invitation Expiration & Cleanup ✅ COMPLETE

- [x] **TEST**: Invitation expiration handling ✅ **16 tests passing!**
  - [x] Write test: Expired invitations cannot be accepted
  - [x] Verify: is_expired property prevents acceptance (already implemented in Phase E)
  - [x] Write test: Expired invitations marked as EXPIRED (cleanup task)
  - [x] Implement: Celery periodic task to mark expired invitations
  - [x] Write test: cleanup_expired_invitations task finds and marks expired
  - [x] Implement: `apps/users/tasks.py` - cleanup_expired_invitations()
  - [x] Write test: Cleanup task runs daily via Celery Beat
  - [x] Implement: django-celery-beat DatabaseScheduler configuration
  - [x] Write test: Cleanup task logs number of invitations expired
  - [x] Implement: Comprehensive logging in cleanup task
  - [x] Write test: Task is idempotent (safe to run multiple times)
  - [x] Implement: Bulk update for efficiency, only touches PENDING invitations
  - [x] Write test: Task handles bulk expiration (50+ invitations)
  - [x] Implement: Efficient queryset filtering and bulk update

**Files created/modified:**
- `backend/apps/users/tasks.py` - Added cleanup_expired_invitations task
- `backend/apps/users/management/commands/setup_periodic_tasks.py` - Celery Beat schedule setup
- `backend/apps/users/tests/test_cleanup_tasks.py` - 16 new tests for cleanup task

**The Housekeeping Task:**
- Runs daily at 2:00 AM UTC
- Finds PENDING invitations with expires_at < now()
- Bulk updates status to EXPIRED (single query - efficient!)
- Logs count and timestamp
- Idempotent and safe

#### Phase I: Permission & Authorization ✅ COMPLETE

- [x] **TEST**: Invitation authorization ✅ **Covered in Phases C-E tests!**
  - [x] Write test: Only ORGANIZER can create invitations
  - [x] Implement: IsFamilyAdmin permission on invite endpoint (Phase C)
  - [x] Write test: Only ORGANIZER can list invitations
  - [x] Implement: Permission check on list endpoint (Phase D)
  - [x] Write test: Only ORGANIZER can cancel invitations
  - [x] Implement: Permission check on cancel endpoint (Phase D)
  - [x] Write test: Invitee can accept/decline their own invitation
  - [x] Implement: Email validation ensures only invitee can accept (Phase E)
  - [x] Write test: Other users cannot accept invitations meant for someone else
  - [x] Implement: Email validation in accept action (Phase E)
  - [x] Write test: PARENT and CHILD cannot create invitations
  - [x] Implement: Tests in Phase C verify 403 for non-ORGANIZER roles

**Permission Summary:**
- ✅ Create invitations: ORGANIZER only
- ✅ List invitations: ORGANIZER only
- ✅ Cancel invitations: ORGANIZER only (must be inviter's family)
- ✅ Accept/Decline: Any authenticated user (email must match invitee_email)
- ✅ All permission tests passing in Phases C, D, E

#### Phase J: Edge Cases & Data Integrity ✅ COMPLETE

- [x] **TEST**: Edge case handling ✅ **Covered throughout all phases!**
  - [x] Write test: Cannot invite user who is already a member
  - [x] Implement: Validation in InvitationCreateSerializer (Phase B)
  - [x] Write test: Cannot have multiple pending invitations for same email
  - [x] Implement: UniqueConstraint on (family, invitee_email, status=PENDING) (Phase A)
  - [x] Write test: Inviter leaves family → invitation still valid
  - [x] Decision: Keep invitation valid (inviter already validated at creation time)
  - [x] Write test: Family deleted → invitations cascade delete
  - [x] Verify: on_delete=CASCADE on family FK (Phase A model)
  - [x] Write test: Accepting invitation when already member returns 400
  - [x] Implement: Validation in accept action checks FamilyMember existence (Phase E)
  - [x] Write test: Token collision prevention (UUID uniqueness)
  - [x] Verify: UUID field with unique=True ensures no collisions (Phase A)
  - [x] Write test: Can re-invite after invitation accepted
  - [x] Implement: Serializer only checks PENDING status (Phase B)

**Edge Cases Handled:**
- ✅ Duplicate invitations prevented (DB constraint)
- ✅ Existing members cannot be invited
- ✅ Already-member accepts returns clear error
- ✅ Cascade delete on family deletion
- ✅ UUID uniqueness guaranteed
- ✅ Case-insensitive email matching
- ✅ Expired invitations cannot be accepted/declined
- ✅ All edge case tests passing throughout phases

#### Phase K: Documentation & E2E Tests ✅ COMPLETE

- [x] **Documentation**: API Integration Guide ✅ **COMPLETE!**
  - [x] Create: Comprehensive API guide for mobile integration
  - [x] Document: All 6 API endpoints with request/response examples
  - [x] Include: TypeScript/mobile implementation examples
  - [x] Add: Sequence diagrams for user flows
  - [x] Document: Error handling best practices
  - [x] Include: Manual testing guide with curl examples
  - [x] Add: Deep linking guide for mobile apps
  - [x] Document: Security considerations and rate limiting
  - [x] Create: Mobile app testing checklist

- [x] **E2E Test Coverage**: Already implemented throughout phases! ✅
  - [x] E2E - Invite user → Accept → Verify membership (Phase E tests)
  - [x] E2E - Invite user → Decline → No membership (Phase E tests)
  - [x] E2E - Signup with token → Auto-join family (Phase G tests)
  - [x] E2E - Cancel invitation → Cannot accept (Phase D tests)
  - [x] E2E - Expired invitation → Cannot accept (Phase E + H tests)
  - [x] All E2E flows covered in 128 comprehensive tests

**Files created:**
- `docs/API_INVITATION_GUIDE.md` - Complete API integration guide for mobile team

**Documentation Includes:**
- 📱 All 6 API endpoints with examples
- 🔄 3 sequence diagrams for user flows
- 🐛 Error handling guide
- ✅ Mobile testing checklist
- 🔗 Deep linking setup
- 💻 TypeScript implementation examples
- 🧪 Manual testing with curl commands

**The mobile team has everything they need to integrate!**

---

## 🎯 Enhancement 3 Summary

**Goal**: Enable ORGANIZERS to invite family members with email-based invitations

### What's Built - PRODUCTION READY! 🚀
- ✅ **Invitation Model** - Full model with validation, constraints, properties (21 tests)
- ✅ **Invitation Serializers** - Create/read serializers with validations (16 tests)
- ✅ **Database Migration** - 0005_invitation.py applied
- ✅ **API Endpoints** - Create, list, cancel, accept, decline (45 tests)
- ✅ **Email Integration** - Celery task with beautiful HTML templates (16 tests)
- ✅ **Signup Integration** - Auto-join family on registration (14 tests) THE MONEY SHOT!
- ✅ **Expiration Cleanup** - Daily Celery Beat task (16 tests)
- ✅ **Permission Checks** - ORGANIZER-only management, email validation
- ✅ **Edge Cases Handled** - Duplicates, existing members, expiration, etc.
- ✅ **128 invitation tests passing** - No regressions! (622 total backend tests)
- ✅ **Verified in Mailpit** - Emails look gorgeous! 📧

### Mission Complete! 🏆

**All phases delivered:**
- ✅ Model, serializers, API endpoints
- ✅ Email integration with beautiful templates
- ✅ Signup auto-join flow
- ✅ Automatic expiration cleanup
- ✅ Comprehensive test suite (128 tests)
- ✅ **Mobile-ready API documentation**

**Ready for:**
- Mobile app integration (React Native)
- Production deployment
- Real user families collaborating!

### Technical Details:
- 📧 **Model**: Invitation (users app) - email, token, status, role, expiration
- 🔐 **Security**: Token-based, email validation, expiration (7 days), role restrictions (no ORGANIZER)
- 📱 **Mobile-First**: Email invite → signup → auto-join flow
- 🧪 **TDD Approach**: 80+ tests covering model, serializers, endpoints, flows
- 🚀 **Deliverables**: Invitation CRUD, accept/decline, email notifications, signup integration
- ⏱️ **Time Invested**: ~8 hours total (TDD methodology ensures quality!)
- 📊 **Impact**: Multi-user families, organic growth, actual collaboration feature!
