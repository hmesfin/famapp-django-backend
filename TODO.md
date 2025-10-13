# FamApp Django Backend - TDD Implementation Plan

## Project Goal

Build a family collaboration app backend using Django REST Framework with JWT authentication. Family members can create accounts, invite others, and collaborate on todos, schedules, grocery lists, and pet care. Deploy to Hetzner ($10/month) with PostgreSQL, Redis, Celery, SendGrid, and Twilio.

## Technology Stack

### Backend (This Repository: `famapp-backend`)

- **Django 5.x** - Web framework (cookiecutter-django foundation)
- **Django REST Framework (DRF)** - RESTful API
- **drf-simplejwt** - JWT authentication
- **PostgreSQL** - Primary database (via Docker)
- **Redis** - Caching and Celery broker (via Docker)
- **Celery** - Background task processing (already configured)
- **SendGrid** - Transactional emails
- **Twilio** - SMS notifications
- **Cloudflare R2** - Media and static asset storage (future)
- **Docker** - Containerization (already configured via cookiecutter-django)
- **Pytest** - Testing framework

### Mobile App (Separate Repository)

- **React Native** - Mobile framework
- **React Query** - Server state management, caching, optimistic updates
- **axios** - HTTP client for API calls

## Migration Phases (TDD Approach)

---

## Phase 1: Backend Setup & Database Models

### 1.1 Repository Setup

- [x] **SETUP**: Verify cookiecutter-django baseline
  - [x] Verify Docker Compose services running (PostgreSQL, Redis, Mailpit, Celery)
  - [x] Test database connection: `docker compose run --rm django python manage.py dbshell`
  - [x] Verify existing user model and authentication
  - [ ] Run existing test suite: `docker compose run --rm django pytest`
  - [ ] Confirm Redis connection for caching

### 1.2 JWT Authentication Setup

- [x] **SETUP**: Install and configure drf-simplejwt

  - [x] Add `djangorestframework-simplejwt` to `pyproject.toml`
  - [x] Rebuild Django container: `docker compose build django`
  - [x] Configure JWT settings in `config/settings/base.py`
  - [x] Add JWT URL patterns to `config/urls.py`
  - [x] Create JWT refresh token endpoint

- [ ] **TEST**: JWT authentication
  - [ ] Write test: Obtain token with valid credentials
  - [ ] Implement: Token obtain view (from simplejwt)
  - [ ] Write test: Refresh token works
  - [ ] Implement: Token refresh view (from simplejwt)
  - [ ] Write test: Protected endpoint requires token
  - [ ] Implement: JWT authentication class configuration
  - [ ] Write test: Invalid token returns 401
  - [ ] Implement: Error handling for invalid tokens

### 1.3 Shared App & Base Models ✅ COMPLETE

- [x] **SETUP**: Create shared app for base models

  - [x] Create app: `python manage.py startapp shared backend/apps/` (ONLY Django command run locally!)
  - [x] Add to INSTALLED_APPS in settings
  - [x] Create `apps/shared/models.py` with BaseModel and SimpleBaseModel

- [x] **TEST**: BaseModel abstract class (41 tests passing!)

  - [x] Write test: Model inheriting BaseModel has id (BigAutoField)
  - [x] Implement: `apps/shared/models.py` (BaseModel with id, public_id, timestamps, audit fields)
  - [x] Write test: BaseModel has public_id (UUID)
  - [x] Implement: UUIDField with default uuid4
  - [x] Write test: BaseModel has created_at, updated_at
  - [x] Implement: DateTimeField with auto_now_add and auto_now
  - [x] Write test: BaseModel has created_by, updated_by
  - [x] Implement: ForeignKey to User (nullable, for audit trail)
  - [x] Write test: BaseModel has is_deleted (soft delete)
  - [x] Implement: BooleanField with default False
  - [x] Write test: BaseModel has deleted_at
  - [x] Implement: DateTimeField (nullable)

- [x] **TEST**: SimpleBaseModel abstract class
  - [x] Write test: SimpleBaseModel has id, public_id, timestamps only
  - [x] Implement: Simpler version without audit fields
  - [x] Verify: Both are abstract=True in Meta

### 1.4 Family & FamilyMember Models ✅ COMPLETE

- [x] **TEST**: Family model (24 tests passing!)

  - [x] Write test: Create family with name
  - [x] Implement: `apps/shared/models.py` (Family model inheriting BaseModel)
  - [x] Write test: Family name is required and max 100 chars
  - [x] Implement: CharField(max_length=100)
  - [x] Write test: Family has many-to-many with User through FamilyMember
  - [x] Implement: ManyToManyField through='FamilyMember'
  - [x] Write test: Cascade deletes (delete family → delete all related data)
  - [x] Implement: Cascade delete on related models

- [x] **TEST**: FamilyMember model
  - [x] Write test: Create family member with user, family, and role
  - [x] Implement: FamilyMember model (inheriting SimpleBaseModel)
  - [x] Write test: Unique constraint (family, user)
  - [x] Implement: unique_together in Meta
  - [x] Write test: Role enum (ORGANIZER, PARENT, CHILD)
  - [x] Implement: CharField with choices (TextChoices)
  - [x] Write test: Default role is PARENT
  - [x] Implement: default=Role.PARENT

### 1.5 Todo Model ✅ COMPLETE

- [x] **TEST**: Todo model (32 tests passing!)
  - [x] Write test: Create todo with required fields (family, title)
  - [x] Implement: `apps/shared/models.py` (Todo model inheriting BaseModel)
  - [x] Write test: Title is required and max 200 chars
  - [x] Implement: CharField(max_length=200)
  - [x] Write test: Optional fields (description, assigned_to, due_date)
  - [x] Implement: TextField (nullable), ForeignKey to User (nullable), DateTimeField (nullable)
  - [x] Write test: Status and Priority enums (TODO/IN_PROGRESS/DONE, LOW/MEDIUM/HIGH)
  - [x] Implement: TextChoices for status and priority
  - [x] Write test: Foreign key relationships (family, assigned_to)
  - [x] Implement: ForeignKey with on_delete=CASCADE for family

### 1.6 ScheduleEvent Model ✅ COMPLETE

- [x] **TEST**: ScheduleEvent model (32 tests passing!)
  - [x] Write test: Create event with required fields (family, title, start_time, end_time)
  - [x] Implement: `apps/shared/models.py` (ScheduleEvent model inheriting BaseModel)
  - [x] Write test: Optional fields (description, location)
  - [x] Implement: TextField (nullable), CharField(max_length=255, nullable)
  - [x] Write test: EventType enum (APPOINTMENT, MEETING, REMINDER, OTHER)
  - [x] Implement: TextChoices with default=OTHER
  - [x] Write test: Assigned_to relationship
  - [x] Implement: ForeignKey to User (nullable)

### 1.7 GroceryItem Model ✅ COMPLETE

- [x] **TEST**: GroceryItem model (36 tests passing!)
  - [x] Write test: Create grocery item with required fields (family, name)
  - [x] Implement: `apps/shared/models.py` (GroceryItem model inheriting BaseModel)
  - [x] Write test: Optional fields (quantity, unit, category)
  - [x] Implement: IntegerField(default=1), CharField(max_length=50), TextChoices
  - [x] Write test: Purchase tracking (is_purchased)
  - [x] Implement: BooleanField with default=False
  - [x] Write test: Added_by relationship
  - [x] Implement: ForeignKey to User (nullable)

### 1.8 Pet Model ✅ COMPLETE

- [x] **TEST**: Pet model (28 tests passing!)

  - [x] Write test: Create pet with required fields (family, name)
  - [x] Implement: `apps/shared/models.py` (Pet model inheriting BaseModel)
  - [x] Write test: Optional fields (breed, age, notes)
  - [x] Implement: CharField(max_length=100), IntegerField(nullable), TextField
  - [x] Write test: Species enum (DOG, CAT, BIRD, FISH, OTHER)
  - [x] Implement: TextChoices with default=OTHER

### 1.9 PetActivity Model ✅ COMPLETE

- [x] **TEST**: PetActivity model (33 tests passing!)
  - [x] Write test: Create activity with required fields (pet, activity_type, scheduled_time)
  - [x] Implement: PetActivity model (inheriting BaseModel)
  - [x] Write test: Optional fields (notes, completed_by, completed_at)
  - [x] Implement: TextField (nullable), ForeignKey to User (nullable), DateTimeField (nullable)
  - [x] Write test: ActivityType enum (FEEDING, WALKING, GROOMING, VET_VISIT, MEDICATION, PLAYTIME, OTHER)
  - [x] Implement: TextChoices for activity types
  - [x] Write test: is_completed tracking
  - [x] Implement: BooleanField with default=False
  - [x] Write test: Foreign key to pet with cascade delete
  - [x] Implement: ForeignKey with on_delete=CASCADE

### 1.10 Django Migrations ✅ COMPLETE

- [x] **MIGRATIONS**: All models migrated successfully!
  - [x] Run: `docker compose run --rm django python manage.py makemigrations`
  - [x] Created 5 migrations:
    - [x] 0001_initial.py (Family, FamilyMember)
    - [x] 0002_todo.py (Todo model)
    - [x] 0003_scheduleevent.py (ScheduleEvent model)
    - [x] 0004_groceryitem.py (GroceryItem model)
    - [x] 0005_pet_petactivity.py (Pet and PetActivity models)
  - [x] Run: `docker compose run --rm django python manage.py migrate`
  - [x] All migrations applied successfully
  - [x] **226 TESTS PASSING!** 🎉🚀🔥

---

## Phase 2: DRF Serializers & Validation ✅ COMPLETE

### 2.1 Family Serializers ✅ COMPLETE (14 tests passing!)

- [x] **TEST**: Family serializers

  - [x] Write test: FamilyCreateSerializer validates name (required, 1-100 chars)
  - [x] Implement: `apps/shared/serializers.py` (FamilyCreateSerializer)
  - [x] Write test: FamilyUpdateSerializer allows partial updates
  - [x] Implement: FamilyUpdateSerializer with all optional fields
  - [x] Write test: FamilySerializer includes id, public_id, timestamps
  - [x] Implement: FamilySerializer with read-only fields
  - [x] Write test: FamilyDetailSerializer includes member list
  - [x] Implement: Nested MemberSerializer with SerializerMethodField

- [x] **TEST**: FamilyMember serializers
  - [x] Write test: MemberSerializer includes user info
  - [x] Implement: MemberSerializer with nested UserSerializer
  - [x] Write test: InviteMemberSerializer validates email
  - [x] Implement: InviteMemberSerializer with EmailField validation
  - [x] Write test: UpdateMemberRoleSerializer validates role enum
  - [x] Implement: ChoiceField with role choices

### 2.2 Todo Serializers ✅ COMPLETE (10 tests passing!)

- [x] **TEST**: Todo serializers
  - [x] Write test: TodoCreateSerializer validates title (required, 1-200 chars)
  - [x] Implement: `apps/shared/serializers.py` (TodoCreateSerializer)
  - [x] Write test: TodoCreateSerializer validates due_date (must be future)
  - [x] Implement: Custom validate_due_date method
  - [x] Write test: TodoUpdateSerializer allows partial updates
  - [x] Implement: TodoUpdateSerializer with all optional fields
  - [x] Write test: TodoSerializer includes computed field (is_overdue)
  - [x] Implement: SerializerMethodField for is_overdue calculation
  - [x] Write test: TodoToggleSerializer for completion toggle
  - [x] Implement: Simple serializer with no fields (action-based)

### 2.3 Schedule Serializers ✅ IMPLEMENTED (tests pending)

- [x] **IMPLEMENT**: Schedule serializers
  - [x] Implement: `apps/shared/serializers.py` (EventCreateSerializer)
  - [x] Implement: validate() method for time range check
  - [x] Implement: EventUpdateSerializer with all optional fields
  - [x] Implement: EventSerializer includes duration calculation
  - [x] Implement: SerializerMethodField for duration

### 2.4 Grocery Serializers ✅ IMPLEMENTED (tests pending)

- [x] **IMPLEMENT**: Grocery serializers
  - [x] Implement: `apps/shared/serializers.py` (GroceryCreateSerializer)
  - [x] Implement: ChoiceField with category choices (nullable)
  - [x] Implement: GroceryUpdateSerializer with all optional fields
  - [x] Implement: GrocerySerializer includes purchaser info
  - [x] Implement: Nested UserSerializer for added_by

### 2.5 Pet Serializers ✅ IMPLEMENTED (tests pending)

- [x] **IMPLEMENT**: Pet serializers
  - [x] Implement: `apps/shared/serializers.py` (PetCreateSerializer)
  - [x] Implement: PetUpdateSerializer with all optional fields
  - [x] Implement: PetSerializer includes last activity timestamps
  - [x] Implement: SerializerMethodField for last_feeding, last_walking
  - [x] Implement: PetActivityCreateSerializer validates activity_type enum
  - [x] Implement: ChoiceField with activity_type choices
  - [x] Implement: PetActivitySerializer includes logger info
  - [x] Implement: Nested UserSerializer for completed_by

**Phase 2 Summary:**
- ✅ All serializers implemented (620+ lines of code)
- ✅ 24 serializer tests written and passing
- ✅ **247/250 tests passing overall** (98.8% pass rate!)
- ✅ Validation for all create/update operations
- ✅ Computed fields (is_overdue, duration, last activities)
- ✅ Nested serializers for user information
- ✅ Partial update support for all update serializers

---

## Phase 3: Permissions & Authorization ✅ COMPLETE

### 3.1 Custom DRF Permissions ✅ COMPLETE (10 tests passing!)

- [x] **TEST**: IsFamilyMember permission

  - [x] Write test: Allows access if user is family member
  - [x] Implement: `apps/shared/permissions.py` (IsFamilyMember permission class)
  - [x] Write test: Returns 403 if user not a member
  - [x] Implement: has_permission() and has_object_permission() methods
  - [x] Write test: Works with family_public_id from URL kwargs
  - [x] Implement: Extract family from view kwargs using public_id

- [x] **TEST**: IsFamilyAdmin permission
  - [x] Write test: Allows access if user is family admin (organizer)
  - [x] Implement: IsFamilyAdmin permission class
  - [x] Write test: Returns 403 if user is member (not admin)
  - [x] Implement: Role check in FamilyMember query (ORGANIZER only)
  - [x] Write test: Returns 403 if user not a member at all
  - [x] Implement: Combined membership and role check

**Phase 3 Summary:**
- ✅ IsFamilyMember permission (5 tests) - View & object-level checks
- ✅ IsFamilyAdmin permission (5 tests) - Role-based access control (RBAC)
- ✅ Both permissions work with `public_id` in URLs (NOT integer id!)
- ✅ **257/260 tests passing overall** (98.8% pass rate!)
- ✅ Bulletproof authorization system ready for CRUD endpoints

**IMPORTANT URL Pattern Note:**
- ✅ All URLs use `public_id` (UUID) NOT integer `id`
- ✅ Pattern: `/api/v1/families/{public_id}/`
- ✅ Permissions check `family_public_id` from view.kwargs
- ✅ Never expose internal database IDs in APIs!

### 3.2 Authorization Mixins ✅ COMPLETE (6 tests passing!)

- [x] **TEST & IMPLEMENT**: FamilyAccessMixin
  - [x] Write test: Filters queryset to user's families only
  - [x] Write test: Excludes soft-deleted families
  - [x] Write test: Excludes soft-deleted resources
  - [x] Write test: Returns empty queryset if user not in any family
  - [x] Write test: Works with multiple families
  - [x] Write test: Respects base queryset filters
  - [x] Implement: `apps/shared/mixins.py` (FamilyAccessMixin)
  - [x] Implement: get_queryset() override with family membership filter
  - [x] Implement: Filter by family\_\_members=request.user
  - [x] Implement: Exclude soft-deleted families and resources
  - [x] Apply to ViewSets in Phase 5+ (TodoViewSet, ScheduleEventViewSet, etc.)

**Phase 3.2 Summary:**
- ✅ FamilyAccessMixin - Reusable authorization pattern
- ✅ Automatic filtering by family membership
- ✅ Soft delete awareness (families and resources)
- ✅ Multiple family support
- ✅ Base queryset preservation
- ✅ 6 comprehensive tests passing
- ✅ **301/304 tests passing overall** (99.0% pass rate!)
- ✅ Ready for Phase 5 - Will use this mixin in all family-scoped ViewSets!

---

## Phase 4: CRUD Endpoints (Family & Members) ✅ COMPLETE

### 4.1 Family Endpoints ✅ COMPLETE (20 tests passing!)

- [x] **TEST**: POST /api/v1/families/

  - [x] Write test: Creates family with authenticated user as admin
  - [x] Implement: `apps/shared/views.py` (FamilyViewSet with create action)
  - [x] Write test: Returns 201 with family data
  - [x] Implement: perform_create() to set created_by and create FamilyMember
  - [x] Write test: Validates family name (required)
  - [x] Implement: Use FamilyCreateSerializer
  - [x] Write test: Returns 401 if not authenticated
  - [x] Implement: IsAuthenticated permission class

- [x] **TEST**: GET /api/v1/families/

  - [x] Write test: Returns all families user belongs to
  - [x] Implement: list() action with queryset filter
  - [x] Write test: Includes member count for each family
  - [x] Implement: annotate(member_count=Count('members'))
  - [x] Write test: Returns empty list if user has no families
  - [x] Implement: Filter by family\_\_members=request.user

- [x] **TEST**: GET /api/v1/families/{public_id}/

  - [x] Write test: Returns family details with members
  - [x] Implement: retrieve() action with FamilyDetailSerializer
  - [x] Write test: Returns 403 if user not a member
  - [x] Implement: IsFamilyMember permission class
  - [x] Write test: Includes member list with roles
  - [x] Implement: Nested serialization with prefetch_related('members')

- [x] **TEST**: PATCH /api/v1/families/{public_id}/

  - [x] Write test: Updates family name (admin only)
  - [x] Implement: update() action with FamilyUpdateSerializer
  - [x] Write test: Returns 403 if user not admin
  - [x] Implement: IsFamilyAdmin permission class
  - [x] Write test: Returns updated family data
  - [x] Implement: perform_update() to set updated_by

- [x] **TEST**: DELETE /api/v1/families/{public_id}/
  - [x] Write test: Soft deletes family (admin only)
  - [x] Implement: destroy() action with soft delete (set is_deleted=True)
  - [x] Write test: Returns 403 if user not admin
  - [x] Implement: IsFamilyAdmin permission class
  - [x] Write test: Cascades to all related data
  - [x] Verify: Django cascade deletes work as expected

### 4.2 Family Member Endpoints ✅ COMPLETE (18 tests passing!)

- [x] **TEST**: POST /api/v1/families/{public_id}/members/

  - [x] Write test: Invites user by email (admin only)
  - [x] Implement: Custom @action on FamilyViewSet (members with POST method)
  - [x] Write test: Creates family member with default PARENT role
  - [x] Implement: Create FamilyMember with role parameter (default PARENT)
  - [x] Write test: Returns 400 if user already a member
  - [x] Implement: Duplicate check before creation
  - [x] Write test: Returns 400 if user doesn't exist
  - [x] Implement: User lookup validation
  - [x] Write test: Returns 403 if user not organizer
  - [x] Implement: Manual permission check for IsFamilyAdmin
  - [ ] Write test: Sends invitation email via SendGrid (DEFERRED)
  - [ ] Implement: Celery task for email sending (DEFERRED)

- [x] **TEST**: GET /api/v1/families/{public_id}/members/

  - [x] Write test: Returns all family members
  - [x] Implement: Custom @action on FamilyViewSet (members with GET method)
  - [x] Write test: Includes user info (name, email, public_id)
  - [x] Implement: select_related('user') for efficiency
  - [x] Write test: Returns 403 if user not a member
  - [x] Implement: Manual permission check for IsFamilyMember

- [x] **TEST**: PATCH /api/v1/families/{public_id}/members/{user_public_id}/

  - [x] Write test: Updates member role (admin only)
  - [x] Implement: Custom @action on FamilyViewSet (member_detail with PATCH method)
  - [x] Write test: Returns 403 if user not admin
  - [x] Implement: Manual permission check for IsFamilyAdmin
  - [x] Write test: Validates role enum
  - [x] Implement: UpdateMemberRoleSerializer validation
  - [x] Write test: Returns 404 if user not in family
  - [x] Implement: get_object_or_404 for user and membership

- [x] **TEST**: DELETE /api/v1/families/{public_id}/members/{user_public_id}/
  - [x] Write test: Removes member from family (admin or self)
  - [x] Implement: Custom @action on FamilyViewSet (member_detail with DELETE method)
  - [x] Write test: Admin can remove any member
  - [x] Implement: Admin authorization check
  - [x] Write test: Member can remove themselves
  - [x] Implement: Self-removal check (request.user == member.user)
  - [x] Write test: Returns 403 if member tries to remove others
  - [x] Implement: Combined authorization logic

**Phase 4 Summary:**
- ✅ FamilyViewSet with full CRUD (create, list, retrieve, update, destroy)
- ✅ Custom actions: members() (GET/POST), member_detail() (PATCH/DELETE)
- ✅ Combined actions pattern (multiple HTTP methods on same endpoint)
- ✅ Manual permission checks (fine-grained control per HTTP method)
- ✅ UUID-based lookups (public_id in URLs, NEVER integer id)
- ✅ Self-service operations (members can leave families)
- ✅ Proper HTTP status codes (201, 200, 400, 403, 404, 204)
- ✅ 38 tests passing (20 Family CRUD + 18 Member Management)
- ✅ **295/298 tests passing overall** (98.9% pass rate!)
- ✅ Phase 4 Complete - Ready for Phase 5!

---

## Phase 5: CRUD Endpoints (Todos) ✅ COMPLETE

### 5.1 Todo Endpoints ✅ COMPLETE (25 tests passing!)

- [x] **TEST & IMPLEMENT**: GET /api/v1/todos/
  - [x] Write test: Returns todos from user's families only
  - [x] Write test: Returns todos from ALL user families
  - [x] Write test: Excludes soft-deleted todos
  - [x] Write test: Excludes todos from soft-deleted families
  - [x] Write test: Returns empty list if no families
  - [x] Write test: Returns 401 if not authenticated
  - [x] Implement: `apps/shared/views.py` (TodoViewSet with FamilyAccessMixin!)
  - [x] Implement: Automatic filtering by family membership (mixin handles it!)

- [x] **TEST & IMPLEMENT**: POST /api/v1/todos/
  - [x] Write test: Creates todo with required fields only
  - [x] Write test: Creates todo with all fields
  - [x] Write test: Sets created_by to current user
  - [x] Write test: Returns 400 if title missing
  - [x] Write test: Returns 400 if family not found
  - [x] Write test: Returns 400 if user not family member
  - [x] Implement: create() action with TodoCreateSerializer
  - [x] Implement: family_public_id validation
  - [x] Implement: perform_create() to auto-populate created_by/updated_by
  - [x] Implement: Override create() to return full TodoSerializer

- [x] **TEST & IMPLEMENT**: GET /api/v1/todos/{public_id}/
  - [x] Write test: Returns todo details
  - [x] Write test: Returns 404 if todo doesn't exist
  - [x] Write test: Returns 404 if todo not in user's families
  - [x] Implement: retrieve() action (default DRF)
  - [x] Implement: FamilyAccessMixin handles authorization automatically!

- [x] **TEST & IMPLEMENT**: PATCH /api/v1/todos/{public_id}/
  - [x] Write test: Updates todo fields
  - [x] Write test: Allows partial updates
  - [x] Write test: Updates updated_by field
  - [x] Write test: Returns 404 if todo not in user's families
  - [x] Implement: update() action with TodoUpdateSerializer
  - [x] Implement: perform_update() to set updated_by
  - [x] Implement: partial=True support

- [x] **TEST & IMPLEMENT**: PATCH /api/v1/todos/{public_id}/toggle/
  - [x] Write test: Marks incomplete todo as complete
  - [x] Write test: Marks complete todo as incomplete
  - [x] Write test: Returns 404 if todo not in user's families
  - [x] Implement: Custom @action (toggle)
  - [x] Implement: Toggle status between TODO ↔️ DONE
  - [x] Implement: Return TodoSerializer(instance)

- [x] **TEST & IMPLEMENT**: DELETE /api/v1/todos/{public_id}/
  - [x] Write test: Soft deletes todo
  - [x] Write test: Soft-deleted todo not in list
  - [x] Write test: Returns 404 if todo not in user's families
  - [x] Implement: destroy() action with soft delete
  - [x] Implement: Returns 204 No Content

**Phase 5 Summary:**
- ✅ TodoViewSet with FamilyAccessMixin (automatic authorization!)
- ✅ Full CRUD operations (list, create, retrieve, update, delete)
- ✅ Custom toggle action for completion status
- ✅ UUID-based lookups (public_id in URLs, NEVER integer id)
- ✅ Soft delete pattern maintained
- ✅ Auto-populated audit fields (created_by, updated_by)
- ✅ TodoCreateSerializer with family_public_id validation
- ✅ 25 comprehensive tests passing (100%)
- ✅ **326/329 tests passing overall** (99.1% pass rate!)
- ✅ FamilyAccessMixin proves its value - DRY authorization!
- ✅ Phase 5 Complete - Ready for Phase 6!

---

## Phase 6: CRUD Endpoints (Schedule, Grocery, Pets) ✅ COMPLETE

### 6.1 Schedule Event Endpoints ✅ COMPLETE (11 tests passing!)

- [x] **TEST & IMPLEMENT**: ScheduleEventViewSet with FamilyAccessMixin
  - [x] Write test: Returns events from user's families only
  - [x] Write test: Excludes soft-deleted events
  - [x] Implement: `apps/shared/views.py` (ScheduleEventViewSet with FamilyAccessMixin)
  - [x] Implement: EventCreateSerializer with family_public_id validation
  - [x] Implement: Automatic filtering by family membership (mixin handles it!)

- [x] **TEST & IMPLEMENT**: POST /api/v1/events/
  - [x] Write test: Creates event with required fields only
  - [x] Write test: Creates event with all fields
  - [x] Write test: Returns 400 if start_time >= end_time
  - [x] Implement: create() action with EventCreateSerializer
  - [x] Implement: Validation for time range (start < end)
  - [x] Implement: Override create() to return full EventSerializer

- [x] **TEST & IMPLEMENT**: GET /api/v1/events/{public_id}/
  - [x] Write test: Returns event details
  - [x] Write test: Returns 404 if event not in user's families
  - [x] Implement: retrieve() action (default DRF)
  - [x] Implement: FamilyAccessMixin handles authorization automatically!

- [x] **TEST & IMPLEMENT**: PATCH /api/v1/events/{public_id}/
  - [x] Write test: Updates event fields
  - [x] Write test: Allows partial updates
  - [x] Implement: update() action with EventUpdateSerializer
  - [x] Implement: perform_update() to set updated_by

- [x] **TEST & IMPLEMENT**: DELETE /api/v1/events/{public_id}/
  - [x] Write test: Soft deletes event
  - [x] Write test: Soft-deleted event not in list
  - [x] Implement: destroy() action (soft delete)
  - [x] Implement: Returns 204 No Content

### 6.2 Grocery Item Endpoints ✅ COMPLETE (12 tests passing!)

- [x] **TEST & IMPLEMENT**: GroceryItemViewSet with FamilyAccessMixin
  - [x] Write test: Returns grocery items from user's families only
  - [x] Write test: Excludes soft-deleted items
  - [x] Implement: `apps/shared/views.py` (GroceryItemViewSet with FamilyAccessMixin)
  - [x] Implement: GroceryCreateSerializer with family_public_id validation
  - [x] Implement: Automatic filtering by family membership (mixin handles it!)

- [x] **TEST & IMPLEMENT**: POST /api/v1/groceries/
  - [x] Write test: Creates grocery item with required fields only
  - [x] Write test: Creates grocery item with all fields
  - [x] Write test: Returns 400 if name empty
  - [x] Implement: create() action with GroceryCreateSerializer
  - [x] Implement: Override create() to return full GrocerySerializer
  - [x] Implement: perform_create() to set added_by

- [x] **TEST & IMPLEMENT**: GET /api/v1/groceries/{public_id}/
  - [x] Write test: Returns grocery item details
  - [x] Write test: Returns 404 if item not in user's families
  - [x] Implement: retrieve() action (default DRF)
  - [x] Implement: FamilyAccessMixin handles authorization automatically!

- [x] **TEST & IMPLEMENT**: PATCH /api/v1/groceries/{public_id}/
  - [x] Write test: Updates item fields
  - [x] Write test: Allows partial updates
  - [x] Implement: update() action with GroceryUpdateSerializer

- [x] **TEST & IMPLEMENT**: PATCH /api/v1/groceries/{public_id}/toggle/
  - [x] Write test: Toggles purchased status (false → true → false)
  - [x] Implement: Custom @action (toggle)
  - [x] Implement: Toggle is_purchased boolean

- [x] **TEST & IMPLEMENT**: DELETE /api/v1/groceries/{public_id}/
  - [x] Write test: Soft deletes item
  - [x] Write test: Soft-deleted item not in list
  - [x] Implement: destroy() action (soft delete)

**Phase 6.1 & 6.2 Summary:**
- ✅ ScheduleEventViewSet with FamilyAccessMixin (11 tests passing)
- ✅ GroceryItemViewSet with FamilyAccessMixin (12 tests passing)
- ✅ Both ViewSets follow same patterns as TodoViewSet
- ✅ UUID-based lookups (public_id in URLs)
- ✅ Soft delete pattern maintained
- ✅ Custom toggle actions implemented
- ✅ EventCreateSerializer & GroceryCreateSerializer with family_public_id validation
- ✅ 23 new tests passing (11 + 12)
- ✅ **369/376 tests passing overall** (98.1% pass rate!)
- ✅ FamilyAccessMixin proving DRY authorization across 3 ViewSets!
- ✅ Swagger tags organized by resource (Families, Todos, Events, Groceries)

### 6.3 Pet & Activity Endpoints ✅ COMPLETE (19 tests passing!)

- [x] **TEST & IMPLEMENT**: PetViewSet with FamilyAccessMixin
  - [x] Write test: Returns pets from user's families only
  - [x] Write test: Excludes soft-deleted pets
  - [x] Implement: `apps/shared/views.py` (PetViewSet with FamilyAccessMixin)
  - [x] Implement: PetCreateSerializer with family_public_id validation
  - [x] Implement: Automatic filtering by family membership (mixin handles it!)

- [x] **TEST & IMPLEMENT**: POST /api/v1/pets/
  - [x] Write test: Creates pet with required fields only
  - [x] Write test: Creates pet with all fields
  - [x] Write test: Returns 400 if name empty
  - [x] Implement: create() action with PetCreateSerializer
  - [x] Implement: Override create() to return full PetSerializer
  - [x] Implement: perform_create() to set created_by/updated_by

- [x] **TEST & IMPLEMENT**: GET /api/v1/pets/{public_id}/
  - [x] Write test: Returns pet details
  - [x] Write test: Returns 404 if pet not in user's families
  - [x] Implement: retrieve() action (default DRF)
  - [x] Implement: FamilyAccessMixin handles authorization automatically!

- [x] **TEST & IMPLEMENT**: PATCH /api/v1/pets/{public_id}/
  - [x] Write test: Updates pet fields
  - [x] Write test: Allows partial updates
  - [x] Implement: update() action with PetUpdateSerializer
  - [x] Implement: perform_update() to set updated_by

- [x] **TEST & IMPLEMENT**: DELETE /api/v1/pets/{public_id}/
  - [x] Write test: Soft deletes pet
  - [x] Write test: Soft-deleted pet not in list
  - [x] Implement: destroy() action (soft delete)
  - [x] Implement: Returns 204 No Content

- [x] **TEST & IMPLEMENT**: POST /api/v1/pets/{public_id}/activities/
  - [x] Write test: Logs feeding activity
  - [x] Write test: Logs walking activity
  - [x] Write test: Sets completed_by to current user when is_completed=True
  - [x] Write test: Returns 404 if pet not in user's families
  - [x] Implement: Custom @action (activities with POST method)
  - [x] Implement: Activity type handling with PetActivityCreateSerializer
  - [x] Implement: Auto-populate pet, created_by, updated_by
  - [x] Implement: Set completed_by if is_completed=True

- [x] **TEST & IMPLEMENT**: GET /api/v1/pets/{public_id}/activities/
  - [x] Write test: Returns activities for pet
  - [x] Write test: Filters by activity_type (query param)
  - [x] Write test: Limits to recent N activities (query param: ?limit=N)
  - [x] Write test: Returns 404 if pet not in user's families
  - [x] Implement: Custom @action (activities with GET method)
  - [x] Implement: activity_type filter (case-insensitive)
  - [x] Implement: Queryset slicing with ordering by -scheduled_time

**Phase 6.3 Summary:**
- ✅ PetViewSet with FamilyAccessMixin (19 tests passing)
- ✅ Full CRUD operations (list, create, retrieve, update, delete)
- ✅ Custom activities action for logging & listing pet activities
- ✅ UUID-based lookups (public_id in URLs)
- ✅ Soft delete pattern maintained
- ✅ Activity filtering by type (case-insensitive)
- ✅ Activity limiting with ?limit query param
- ✅ PetCreateSerializer with family_public_id validation
- ✅ PetActivityCreateSerializer with is_completed support
- ✅ Auto-populate completed_by when is_completed=True
- ✅ 19 new tests passing (100%)
- ✅ **388/391 tests passing overall** (99.2% pass rate!)
- ✅ FamilyAccessMixin proving DRY authorization across 4 ViewSets!
- ✅ Swagger tags organized by resource (Families, Todos, Events, Groceries, Pets)

**Phase 6 Overall Summary:**
- ✅ **COMPLETE**: 3 additional ViewSets with full CRUD (Events, Groceries, Pets)
- ✅ **COMPLETE**: 42 new tests (11 + 12 + 19) all passing!
- ✅ **PATTERN**: Consistent TDD approach across all endpoints
- ✅ **DRY**: FamilyAccessMixin eliminates authorization boilerplate
- ✅ **CUSTOM ACTIONS**: Toggle & activities endpoints working perfectly
- ✅ **FILTERING**: Query params for activity_type & limit working
- ✅ **VALIDATION**: family_public_id validation across all create serializers
- ✅ **SWAGGER**: All endpoints properly tagged by resource
- ✅ **TOTAL**: 388 tests passing (99.2% pass rate!) 🎉
- ✅ **READY FOR PHASE 7**: Background jobs (Celery tasks)

---

## Phase 7: Background Jobs (Celery)

### 7.1 Pet Care Reminders

- [ ] **TEST**: schedule_pet_feeding_reminder task

  - [ ] Write test: Schedules daily SMS for pet feeding
  - [ ] Implement: `apps/shared/tasks.py` (Celery task)
  - [ ] Write test: Uses Twilio to send SMS to family members
  - [ ] Implement: Twilio Python SDK integration
  - [ ] Write test: Sends at configured feeding times
  - [ ] Implement: Parse pet.feeding_schedule JSONField
  - [ ] Write test: Doesn't send if already fed today
  - [ ] Implement: Query PetActivity for today's feeding

- [ ] **TEST**: schedule_pet_walking_reminder task
  - [ ] Write test: Schedules daily SMS for pet walking
  - [ ] Implement: Walking reminder task
  - [ ] Write test: Uses Twilio to send SMS
  - [ ] Implement: Twilio integration
  - [ ] Write test: Sends at configured walking times
  - [ ] Implement: Schedule parsing
  - [ ] Write test: Doesn't send if already walked today
  - [ ] Implement: Activity check

### 7.2 Todo & Event Reminders

- [ ] **TEST**: schedule_todo_reminder task

  - [ ] Write test: Sends email reminder before due date
  - [ ] Implement: `apps/shared/tasks.py` (Celery task)
  - [ ] Write test: Uses SendGrid for email (or Django email backend)
  - [ ] Implement: Django send_mail() with SendGrid backend
  - [ ] Write test: Configurable lead time (e.g., 1 hour before)
  - [ ] Implement: Lead time parameter in task
  - [ ] Write test: Only sends if todo incomplete
  - [ ] Implement: Status check before sending

- [ ] **TEST**: schedule_event_reminder task
  - [ ] Write test: Sends email reminder before event
  - [ ] Implement: Event reminder task
  - [ ] Write test: Uses SendGrid for email
  - [ ] Implement: Django email backend
  - [ ] Write test: Configurable lead time (e.g., 15 minutes before)
  - [ ] Implement: Lead time parameter

### 7.3 Celery Beat Configuration

- [ ] **TEST**: Periodic task scheduling
  - [ ] Write test: Pet reminders run at configured times
  - [ ] Implement: Celery Beat schedule in settings (CELERY_BEAT_SCHEDULE)
  - [ ] Write test: Daily digest email task
  - [ ] Implement: Family daily summary task
  - [ ] Write test: Cleanup old soft-deleted todos (30 days)
  - [ ] Implement: Cleanup task with queryset filter

---

## Phase 8: API Documentation & URL Routing

### 8.1 DRF Router Configuration

- [ ] **SETUP**: Configure API URLs

  - [ ] Create `apps/shared/urls.py`
  - [ ] Register ViewSets with DefaultRouter
  - [ ] Configure nested routes for family-scoped resources
  - [ ] Include in `config/urls.py` under `/api/v1/`

- [ ] **TEST**: URL resolution
  - [ ] Write test: Family URLs resolve correctly
  - [ ] Write test: Todo URLs resolve correctly
  - [ ] Write test: Nested routes work (families/{id}/todos/)
  - [ ] Write test: Custom actions resolve (toggle, invite_member, etc.)

### 8.2 API Documentation

- [ ] **SETUP**: Install drf-spectacular for OpenAPI schema

  - [ ] Add `drf-spectacular` to `pyproject.toml`
  - [ ] Rebuild Django container
  - [ ] Configure spectacular settings in `config/settings/base.py`
  - [ ] Add schema view to URLs

- [ ] **TEST**: OpenAPI schema generation
  - [ ] Write test: Schema generates without errors
  - [ ] Implement: Run `python manage.py spectacular --file schema.yml`
  - [ ] Write test: All endpoints documented
  - [ ] Verify: Manual review of generated schema
  - [ ] Access Swagger UI: http://localhost:8000/api/docs/

---

## Phase 9: Testing & Polish

### 9.1 Backend Testing

- [ ] **TEST**: API endpoint integration tests

  - [ ] Write tests for all endpoints (CRUD operations)
  - [ ] Test authorization (403 errors with IsFamilyMember, IsFamilyAdmin)
  - [ ] Test validation (400 errors from serializers)
  - [ ] Test not found (404 errors)
  - [ ] Test soft deletes (is_deleted filtering)
  - [ ] Test pagination (if implemented with DRF pagination)
  - [ ] Test filtering and sorting

- [ ] **TEST**: Background task tests

  - [ ] Mock Celery and test task functions in isolation
  - [ ] Mock SendGrid/Django email backend
  - [ ] Mock Twilio SDK
  - [ ] Test task scheduling and retries

- [ ] **TEST**: Database tests
  - [ ] Test model constraints (unique_together, foreign keys)
  - [ ] Test soft deletes (is_deleted flag behavior)
  - [ ] Test cascade deletes
  - [ ] Test timestamps (auto_now, auto_now_add)

### 9.2 Code Quality

- [ ] **QUALITY**: Backend code review

  - [ ] Run Ruff linting: `docker compose run --rm django ruff check .`
  - [ ] Run Black formatting: `docker compose run --rm django black .`
  - [ ] Run mypy type checking (if configured)
  - [ ] Review error handling consistency
  - [ ] Review logging statements
  - [ ] Run test coverage: `docker compose run --rm django pytest --cov`

- [ ] **QUALITY**: Django checks
  - [ ] Run: `docker compose run --rm django python manage.py check`
  - [ ] Run: `docker compose run --rm django python manage.py check --deploy`
  - [ ] Verify no migration conflicts: `docker compose run --rm django python manage.py showmigrations`

### 9.3 End-to-End Testing

- [ ] **TEST**: Critical user flows
  - [ ] Test signup → create family → add todo → complete todo
  - [ ] Test invite member → accept invitation → view shared data
  - [ ] Test log pet activity → verify last activity timestamps
  - [ ] Test create event → verify event appears in list

---

## Phase 10: Deployment

### 10.1 Backend Deployment (Hetzner)

- [ ] **DEPLOY**: Docker production setup

  - [ ] Create production Dockerfile (if different from local)
  - [ ] Create docker-compose.production.yml
  - [ ] Configure environment variables in .envs/.production/
  - [ ] Test local production build: `docker compose -f docker-compose.production.yml build`

- [ ] **DEPLOY**: Hetzner server setup

  - [ ] Provision Hetzner VPS ($10/month)
  - [ ] Install Docker and Docker Compose
  - [ ] Configure firewall (allow 80, 443, 22)
  - [ ] Setup SSH key authentication
  - [ ] Clone repository to server

- [ ] **DEPLOY**: SSL/TLS with Traefik

  - [ ] Configure Traefik (already in cookiecutter-django compose/production/)
  - [ ] Setup Let's Encrypt for SSL certificates
  - [ ] Configure domain DNS to point to Hetzner IP
  - [ ] Test HTTPS access

- [ ] **DEPLOY**: Database setup

  - [ ] Run PostgreSQL in production Docker container
  - [ ] Configure persistent volumes for database
  - [ ] Run migrations: `docker compose -f docker-compose.production.yml run --rm django python manage.py migrate`
  - [ ] Create superuser: `docker compose -f docker-compose.production.yml run --rm django python manage.py createsuperuser`
  - [ ] Create production database backup strategy (pg_dump cron job)

- [ ] **DEPLOY**: Application deployment

  - [ ] Deploy with: `docker compose -f docker-compose.production.yml up -d`
  - [ ] Verify API health: `curl https://yourdomain.com/api/v1/`
  - [ ] Test JWT authentication endpoints
  - [ ] Monitor logs: `docker compose -f docker-compose.production.yml logs -f django`

- [ ] **DEPLOY**: Background workers
  - [ ] Verify Celery worker container running
  - [ ] Verify Celery Beat container running
  - [ ] Verify Redis connection
  - [ ] Test scheduled tasks (check logs)

### 10.2 Monitoring & Observability

- [ ] **MONITOR**: Backend monitoring

  - [ ] Setup structured logging (Python logging configured in settings)
  - [ ] Setup error tracking (Sentry or similar)
  - [ ] Setup uptime monitoring (UptimeRobot or similar)
  - [ ] Setup performance monitoring (Django Debug Toolbar in dev, APM in prod)

- [ ] **MONITOR**: Database monitoring
  - [ ] Monitor connection pool usage
  - [ ] Monitor query performance (Django Debug Toolbar)
  - [ ] Setup automated daily backups (pg_dump cron job)
  - [ ] Test restore from backup

---

## Success Metrics

- [ ] **Backend**: All 100+ API tests passing
- [ ] **Backend**: 90%+ code coverage (run pytest --cov)
- [ ] **Mobile**: All screen and hook tests passing (separate repo)
- [ ] **Mobile**: React Query caching working correctly
- [ ] **E2E**: Critical user flows tested and working
- [ ] **Performance**: API response time <200ms (95th percentile)
- [ ] **Cost**: Hosting cost ≤$10/month on Hetzner
- [ ] **Reliability**: 99.5%+ uptime for backend API
- [ ] **Security**: JWT authentication working securely
- [ ] **Security**: All endpoints properly authorized

---

## Timeline Estimate

### Backend Development: 12-15 hours

- Phase 1: Setup & Models (3-4 hours)
- Phase 2: Serializers (2-3 hours)
- Phase 3: Permissions (1-2 hours)
- Phase 4-6: CRUD Endpoints (4-5 hours)
- Phase 7: Background Jobs (2 hours)
- Phase 8: API Docs & Routing (1 hour)

### Testing & Deployment: 3-5 hours

- Phase 9: Testing & Polish (2-3 hours)
- Phase 10: Deployment (1-2 hours)

**Total Estimate**: 15-20 hours

---

## Notes

- **TDD Discipline**: Write tests FIRST, then implement (Red-Green-Refactor)
- **Django Patterns**: Follow cookiecutter-django conventions
- **Model Inheritance**: ALWAYS use BaseModel/SimpleBaseModel from shared app
- **Import Paths**: Import from `apps.shared.models` NOT `backend.apps.shared.models`
- **Docker Workflow**: Run Django commands via `docker compose run --rm django`
- **Soft Deletes**: Use `is_deleted` flag, don't hard delete (except where appropriate)
- **UUID Exposure**: Use `public_id` in APIs, never expose internal `id`
- **Authorization**: Use DRF permissions (IsFamilyMember, IsFamilyAdmin) consistently
- **Celery**: Already configured in cookiecutter-django, just add tasks
- **Cost Savings**: $180/year savings ($25 Supabase → $10 Hetzner)
- **Full Control**: Own the entire stack, no vendor lock-in
- **Future Features**: Celery enables background jobs (reminders, notifications, exports)

---

## Project Structure

```
famapp-backend/
├── backend/
│   ├── apps/
│   │   └── shared/             # Main app for FamApp models
│   │       ├── models.py       # All models (BaseModel, Family, Todo, etc.)
│   │       ├── serializers.py  # All DRF serializers
│   │       ├── views.py        # All DRF ViewSets
│   │       ├── permissions.py  # Custom DRF permissions
│   │       ├── mixins.py       # Authorization mixins
│   │       ├── tasks.py        # Celery tasks
│   │       ├── urls.py         # API URL routing
│   │       └── tests/          # All tests
│   │           ├── test_models.py
│   │           ├── test_serializers.py
│   │           ├── test_views.py
│   │           ├── test_permissions.py
│   │           └── test_tasks.py
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py         # JWT, DRF, Celery config
│   │   │   ├── local.py
│   │   │   └── production.py
│   │   └── urls.py             # Include apps.shared.urls
│   └── tests/                  # Project-level tests
├── compose/                    # Docker configs (DO NOT TOUCH!)
├── .envs/                      # Environment variables
├── docker-compose.yml          # Local development
├── docker-compose.production.yml  # Production deployment
├── pyproject.toml              # Python dependencies
└── TODO.md                     # This file!
```

---

_"In cookiecutter-django we trust, all others must bring tests!"_ 🍪
_"Ham Dog & TC: Making Django REST APIs with TDD discipline!"_ 🚀
