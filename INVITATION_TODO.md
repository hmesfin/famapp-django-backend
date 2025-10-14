# TDD Plan: Family Invitation System

**Target**: Enable ORGANIZERS to invite family members by email with role assignment

---

## 📊 PROGRESS TRACKER

**Completed:** 6/11 phases (55%)
**Tests Passing:** 98 invitation tests (21 model + 16 serializer + 11 create + 16 list/cancel + 18 accept/decline + 16 email)
**Status:** Core invitation system complete, ready for signup integration!

### Phase Status:
- ✅ **Phase A**: Invitation Model - COMPLETE (21 tests)
- ✅ **Phase B**: Invitation Serializers - COMPLETE (16 tests)
- ✅ **Phase C**: Invitation Creation Endpoint - COMPLETE (11 tests)
- ✅ **Phase D**: Invitation Listing & Management - COMPLETE (16 tests)
- ✅ **Phase E**: Invitation Acceptance Flow - COMPLETE (18 tests)
- ✅ **Phase F**: Invitation Email & Celery Task - COMPLETE (16 tests)
- 🔄 **Phase G**: Signup with Invitation Flow - NEXT UP
- ⏳ **Phase H**: Invitation Expiration & Cleanup - PENDING
- ⏳ **Phase I**: Permission & Authorization - PENDING (mostly done!)
- ⏳ **Phase J**: Edge Cases & Data Integrity - PENDING (mostly done!)
- ⏳ **Phase K**: Documentation & E2E Tests - PENDING

**Next Steps:**
1. 🔄 Phase G: Integrate invitation token into registration/OTP flow (THE MONEY SHOT!)
2. Phase H: Celery periodic task for expiration cleanup
3. Phase I-K: Final polish, edge cases, E2E tests, docs

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

#### Phase G: Signup with Invitation Flow

- [ ] **TEST**: POST /api/auth/register/ with invitation_token
  - [ ] Write test: Register with invitation_token auto-joins family after verification
  - [ ] Implement: Optional invitation_token parameter in RegisterSerializer
  - [ ] Write test: Validates invitation token exists and is pending
  - [ ] Implement: Custom validate_invitation_token() method
  - [ ] Write test: Validates email matches invitation's invitee_email
  - [ ] Implement: Email validation in serializer
  - [ ] Write test: Validates invitation not expired
  - [ ] Implement: Expiration check in validation
  - [ ] Write test: After OTP verification, accepts invitation automatically
  - [ ] Implement: Call accept invitation logic in verify_otp view if invitation_token present
  - [ ] Write test: Returns family data in registration response
  - [ ] Implement: Include family info in verify-otp response
  - [ ] Write test: User can join multiple families via invitations
  - [ ] Verify: No conflicts with auto-created family (user has 2+ families)

#### Phase H: Invitation Expiration & Cleanup

- [ ] **TEST**: Invitation expiration handling
  - [ ] Write test: Expired invitations cannot be accepted
  - [ ] Verify: is_expired property prevents acceptance
  - [ ] Write test: Expired invitations marked as EXPIRED (cleanup task)
  - [ ] Implement: Celery periodic task to mark expired invitations
  - [ ] Write test: cleanup_expired_invitations task finds and marks expired
  - [ ] Implement: `apps/users/tasks.py` - cleanup_expired_invitations()
  - [ ] Write test: Cleanup task runs daily
  - [ ] Implement: Celery Beat schedule for cleanup task
  - [ ] Write test: Cleanup task logs number of invitations expired
  - [ ] Implement: Logging in cleanup task

#### Phase I: Permission & Authorization

- [ ] **TEST**: Invitation authorization
  - [ ] Write test: Only ORGANIZER can create invitations
  - [ ] Implement: IsFamilyAdmin permission on invite endpoint
  - [ ] Write test: Only ORGANIZER can list invitations
  - [ ] Implement: Permission check on list endpoint
  - [ ] Write test: Only ORGANIZER can cancel invitations
  - [ ] Implement: Permission check on cancel endpoint
  - [ ] Write test: Invitee can accept/decline their own invitation
  - [ ] Implement: Email validation ensures only invitee can accept
  - [ ] Write test: Other users cannot accept invitations meant for someone else
  - [ ] Implement: Email validation in accept action

#### Phase J: Edge Cases & Data Integrity

- [ ] **TEST**: Edge case handling
  - [ ] Write test: Cannot invite user who is already a member
  - [ ] Implement: Validation in serializer checking FamilyMember existence
  - [ ] Write test: Cannot have multiple pending invitations for same email
  - [ ] Implement: Unique constraint on (family, invitee_email, status=PENDING)
  - [ ] Write test: Inviter leaves family → invitation still valid (or cancelled?)
  - [ ] Decide: Keep invitation valid or auto-cancel?
  - [ ] Write test: Family deleted → invitations cascade delete
  - [ ] Verify: on_delete=CASCADE on family FK
  - [ ] Write test: Accepting invitation when already member returns 400
  - [ ] Implement: Validation before creating duplicate FamilyMember
  - [ ] Write test: Token collision prevention (UUID uniqueness)
  - [ ] Verify: UUID field ensures uniqueness

#### Phase K: Documentation & E2E Tests

- [ ] **TEST**: E2E invitation flows
  - [ ] Write test: E2E - Invite user → Accept → Verify membership
  - [ ] Implement: Complete flow test in test_e2e_flows.py
  - [ ] Write test: E2E - Invite user → Decline → No membership
  - [ ] Implement: Decline flow test
  - [ ] Write test: E2E - Signup with token → Auto-join family
  - [ ] Implement: Signup with invitation test
  - [ ] Write test: E2E - Cancel invitation → Cannot accept
  - [ ] Implement: Cancel flow test
  - [ ] Write test: E2E - Expired invitation → Cannot accept
  - [ ] Implement: Expiration test
  - [ ] Update: OpenAPI schema with invitation endpoints
  - [ ] Implement: drf-spectacular decorators on InvitationViewSet
  - [ ] Update: TODO.md - Document invitation feature
  - [ ] Update: API docs - Add invitation flow examples

---

## 🎯 Enhancement 3 Summary

**Goal**: Enable ORGANIZERS to invite family members with email-based invitations

### What's Built So Far:
- ✅ **Invitation Model** - Full model with validation, constraints, properties (21 tests)
- ✅ **Invitation Serializers** - Create/read serializers with validations (16 tests)
- ✅ **Database Migration** - 0005_invitation.py applied
- ✅ **API Endpoints** - Create, list, cancel, accept, decline (45 tests)
- ✅ **Email Integration** - Celery task with beautiful HTML templates (16 tests)
- ✅ **98 invitation tests passing** - No regressions!
- ✅ **Verified in Mailpit** - Emails look gorgeous! 📧

### What's Next:
- 🔄 **Signup Integration** - Auto-join family on registration (Phase G) - THE MONEY SHOT!
- 🔄 **Maintenance** - Expiration cleanup task (Phase H)
- 🔄 **Polish** - Final edge cases, E2E tests, docs (Phases I-K)

### Technical Details:
- 📧 **Model**: Invitation (users app) - email, token, status, role, expiration
- 🔐 **Security**: Token-based, email validation, expiration (7 days), role restrictions (no ORGANIZER)
- 📱 **Mobile-First**: Email invite → signup → auto-join flow
- 🧪 **TDD Approach**: 80+ tests covering model, serializers, endpoints, flows
- 🚀 **Deliverables**: Invitation CRUD, accept/decline, email notifications, signup integration
- ⏱️ **Estimated Time**: 6-8 hours total (5 hours done, 1-3 hours remaining)
- 📊 **Impact**: Multi-user families, organic growth, actual collaboration feature!
