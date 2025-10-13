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

## Phase 3: Permissions & Authorization

### 3.1 Custom DRF Permissions

- [ ] **TEST**: IsFamilyMember permission

  - [ ] Write test: Allows access if user is family member
  - [ ] Implement: `apps/shared/permissions.py` (IsFamilyMember permission class)
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: has_permission() and has_object_permission() methods
  - [ ] Write test: Works with family_id from URL kwargs
  - [ ] Implement: Extract family from view kwargs

- [ ] **TEST**: IsFamilyAdmin permission
  - [ ] Write test: Allows access if user is family admin
  - [ ] Implement: IsFamilyAdmin permission class
  - [ ] Write test: Returns 403 if user is member (not admin)
  - [ ] Implement: Role check in FamilyMember query
  - [ ] Write test: Returns 403 if user not a member at all
  - [ ] Implement: Combined membership and role check

### 3.2 Authorization Mixins

- [ ] **TEST**: FamilyAccessMixin

  - [ ] Write test: Mixin verifies user is family member for object
  - [ ] Implement: `apps/shared/mixins.py` (FamilyAccessMixin)
  - [ ] Write test: Returns 404 if object doesn't exist
  - [ ] Implement: get_queryset() override with family membership filter
  - [ ] Write test: Returns 403 if object not in user's families
  - [ ] Implement: Filter by family\_\_members=request.user

- [ ] **TEST**: Apply to resource models
  - [ ] Implement: TodoAccessMixin
  - [ ] Implement: EventAccessMixin
  - [ ] Implement: GroceryAccessMixin
  - [ ] Implement: PetAccessMixin

---

## Phase 4: CRUD Endpoints (Family & Members)

### 4.1 Family Endpoints

- [ ] **TEST**: POST /api/v1/families/

  - [ ] Write test: Creates family with authenticated user as admin
  - [ ] Implement: `apps/shared/views.py` (FamilyViewSet with create action)
  - [ ] Write test: Returns 201 with family data
  - [ ] Implement: perform_create() to set created_by and create FamilyMember
  - [ ] Write test: Validates family name (required)
  - [ ] Implement: Use FamilyCreateSerializer
  - [ ] Write test: Returns 401 if not authenticated
  - [ ] Implement: IsAuthenticated permission class

- [ ] **TEST**: GET /api/v1/families/

  - [ ] Write test: Returns all families user belongs to
  - [ ] Implement: list() action with queryset filter
  - [ ] Write test: Includes member count for each family
  - [ ] Implement: annotate(member_count=Count('members'))
  - [ ] Write test: Returns empty list if user has no families
  - [ ] Implement: Filter by family\_\_members=request.user

- [ ] **TEST**: GET /api/v1/families/{public_id}/

  - [ ] Write test: Returns family details with members
  - [ ] Implement: retrieve() action with FamilyDetailSerializer
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: IsFamilyMember permission class
  - [ ] Write test: Includes member list with roles
  - [ ] Implement: Nested serialization with prefetch_related('members')

- [ ] **TEST**: PATCH /api/v1/families/{public_id}/

  - [ ] Write test: Updates family name (admin only)
  - [ ] Implement: update() action with FamilyUpdateSerializer
  - [ ] Write test: Returns 403 if user not admin
  - [ ] Implement: IsFamilyAdmin permission class
  - [ ] Write test: Returns updated family data
  - [ ] Implement: perform_update() to set updated_by

- [ ] **TEST**: DELETE /api/v1/families/{public_id}/
  - [ ] Write test: Soft deletes family (admin only)
  - [ ] Implement: destroy() action with soft delete (set is_deleted=True)
  - [ ] Write test: Returns 403 if user not admin
  - [ ] Implement: IsFamilyAdmin permission class
  - [ ] Write test: Cascades to all related data
  - [ ] Verify: Django cascade deletes work as expected

### 4.2 Family Member Endpoints

- [ ] **TEST**: POST /api/v1/families/{public_id}/members/

  - [ ] Write test: Invites user by email (admin only)
  - [ ] Implement: Custom @action on FamilyViewSet (invite_member)
  - [ ] Write test: Creates family member with 'member' role
  - [ ] Implement: Create FamilyMember with default role
  - [ ] Write test: Sends invitation email via SendGrid
  - [ ] Implement: Celery task for email sending
  - [ ] Write test: Returns 400 if user already a member
  - [ ] Implement: Duplicate check before creation
  - [ ] Write test: Returns 404 if user doesn't exist
  - [ ] Implement: User lookup validation

- [ ] **TEST**: GET /api/v1/families/{public_id}/members/

  - [ ] Write test: Returns all family members
  - [ ] Implement: Custom @action on FamilyViewSet (list_members)
  - [ ] Write test: Includes user info (name, email, avatar)
  - [ ] Implement: select_related('user') for efficiency
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: IsFamilyMember permission class

- [ ] **TEST**: PATCH /api/v1/families/{public_id}/members/{user_public_id}/

  - [ ] Write test: Updates member role (admin only)
  - [ ] Implement: Custom @action on FamilyViewSet (update_member_role)
  - [ ] Write test: Returns 403 if user not admin
  - [ ] Implement: IsFamilyAdmin permission class
  - [ ] Write test: Validates role enum
  - [ ] Implement: UpdateMemberRoleSerializer validation

- [ ] **TEST**: DELETE /api/v1/families/{public_id}/members/{user_public_id}/
  - [ ] Write test: Removes member from family (admin or self)
  - [ ] Implement: Custom @action on FamilyViewSet (remove_member)
  - [ ] Write test: Admin can remove any member
  - [ ] Implement: Admin authorization check
  - [ ] Write test: Member can remove themselves
  - [ ] Implement: Self-removal check (request.user == member.user)
  - [ ] Write test: Returns 403 if member tries to remove others
  - [ ] Implement: Combined authorization logic

---

## Phase 5: CRUD Endpoints (Todos)

### 5.1 Todo Endpoints

- [ ] **TEST**: GET /api/v1/families/{public_id}/todos/

  - [ ] Write test: Returns all todos for family
  - [ ] Implement: `apps/shared/views.py` (TodoViewSet with nested route)
  - [ ] Write test: Filters by status (query param: ?completed=true/false)
  - [ ] Implement: django_filters integration or manual filtering
  - [ ] Write test: Filters by assignee (query param: ?assigned_to=user_public_id)
  - [ ] Implement: Filter by assigned_to\_\_public_id
  - [ ] Write test: Sorts by due_date ascending
  - [ ] Implement: ordering = ['due_date'] or query param
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: IsFamilyMember permission class

- [ ] **TEST**: POST /api/v1/families/{public_id}/todos/

  - [ ] Write test: Creates todo with title only
  - [ ] Implement: create() action with TodoCreateSerializer
  - [ ] Write test: Creates todo with all fields
  - [ ] Implement: Handle optional fields
  - [ ] Write test: Sets created_by to current user
  - [ ] Implement: perform_create() to auto-populate created_by
  - [ ] Write test: Returns 201 with todo data
  - [ ] Implement: Status code in Response
  - [ ] Write test: Validates title required
  - [ ] Implement: Serializer validation

- [ ] **TEST**: GET /api/v1/todos/{public_id}/

  - [ ] Write test: Returns todo details
  - [ ] Implement: retrieve() action with TodoSerializer
  - [ ] Write test: Returns 404 if todo doesn't exist
  - [ ] Implement: Default DRF 404 handling
  - [ ] Write test: Returns 403 if todo not in user's families
  - [ ] Implement: FamilyAccessMixin or custom permission

- [ ] **TEST**: PATCH /api/v1/todos/{public_id}/

  - [ ] Write test: Updates todo fields
  - [ ] Implement: update() action with TodoUpdateSerializer
  - [ ] Write test: Allows partial updates
  - [ ] Implement: partial=True in serializer
  - [ ] Write test: Returns updated todo data
  - [ ] Implement: perform_update() to set updated_by
  - [ ] Write test: Returns 403 if todo not in user's families
  - [ ] Implement: Authorization check

- [ ] **TEST**: PATCH /api/v1/todos/{public_id}/toggle/

  - [ ] Write test: Marks incomplete todo as complete
  - [ ] Implement: Custom @action (toggle_completion)
  - [ ] Write test: Sets completed_at and completed_by
  - [ ] Implement: Update fields with timezone.now() and request.user
  - [ ] Write test: Marks complete todo as incomplete
  - [ ] Implement: Clear completed_at and completed_by
  - [ ] Write test: Returns updated todo
  - [ ] Implement: Return TodoSerializer(instance)

- [ ] **TEST**: DELETE /api/v1/todos/{public_id}/
  - [ ] Write test: Soft deletes todo
  - [ ] Implement: destroy() action with soft delete
  - [ ] Write test: Returns 204 No Content
  - [ ] Implement: Default DRF response
  - [ ] Write test: Returns 403 if todo not in user's families
  - [ ] Implement: Authorization check

---

## Phase 6: CRUD Endpoints (Schedule, Grocery, Pets)

### 6.1 Schedule Event Endpoints

- [ ] **TEST**: GET /api/v1/families/{public_id}/events/

  - [ ] Write test: Returns all events for family
  - [ ] Implement: `apps/shared/views.py` (ScheduleEventViewSet)
  - [ ] Write test: Filters by date range (query params: ?start_date, ?end_date)
  - [ ] Implement: Date range filtering with Q objects
  - [ ] Write test: Sorts by start_time ascending
  - [ ] Implement: ordering = ['start_time']
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: IsFamilyMember permission class

- [ ] **TEST**: POST /api/v1/families/{public_id}/events/

  - [ ] Write test: Creates event with required fields
  - [ ] Implement: create() action with EventCreateSerializer
  - [ ] Write test: Validates start_time < end_time
  - [ ] Implement: Serializer validation
  - [ ] Write test: Sets created_by to current user
  - [ ] Implement: perform_create()
  - [ ] Write test: Returns 201 with event data
  - [ ] Implement: Status code

- [ ] **TEST**: GET /api/v1/events/{public_id}/

  - [ ] Implement: retrieve() action
  - [ ] Write test: Authorization check
  - [ ] Implement: FamilyAccessMixin

- [ ] **TEST**: PATCH /api/v1/events/{public_id}/

  - [ ] Implement: update() action
  - [ ] Write test: Partial updates
  - [ ] Implement: partial=True

- [ ] **TEST**: DELETE /api/v1/events/{public_id}/
  - [ ] Implement: destroy() action (soft delete)
  - [ ] Write test: Returns 204
  - [ ] Implement: Default response

### 6.2 Grocery Item Endpoints

- [ ] **TEST**: GET /api/v1/families/{public_id}/groceries/

  - [ ] Write test: Returns all grocery items for family
  - [ ] Implement: `apps/shared/views.py` (GroceryItemViewSet)
  - [ ] Write test: Filters by purchased status (query param: ?purchased=true/false)
  - [ ] Implement: Boolean filter
  - [ ] Write test: Filters by category (query param: ?category=produce)
  - [ ] Implement: Category filter
  - [ ] Write test: Groups by category (query param: ?group_by=category)
  - [ ] Implement: Custom queryset grouping or serializer method

- [ ] **TEST**: POST /api/v1/families/{public_id}/groceries/

  - [ ] Write test: Creates grocery item with name only
  - [ ] Implement: create() action
  - [ ] Write test: Creates with quantity and category
  - [ ] Implement: Handle optional fields
  - [ ] Write test: Sets added_by to current user
  - [ ] Implement: perform_create()

- [ ] **TEST**: PATCH /api/v1/groceries/{public_id}/toggle/

  - [ ] Write test: Marks item as purchased
  - [ ] Implement: Custom @action (toggle_purchased)
  - [ ] Write test: Sets purchased_at and purchased_by
  - [ ] Implement: Update timestamp and user
  - [ ] Write test: Unpurchase item (clear timestamps)
  - [ ] Implement: Clear purchased_at and purchased_by

- [ ] **TEST**: DELETE /api/v1/groceries/{public_id}/

  - [ ] Implement: destroy() action (soft delete)

- [ ] **TEST**: DELETE /api/v1/families/{public_id}/groceries/purchased/
  - [ ] Write test: Bulk soft deletes all purchased items
  - [ ] Implement: Custom @action (clear_purchased)
  - [ ] Write test: Returns count of deleted items
  - [ ] Implement: Return Response({'count': deleted_count})

### 6.3 Pet & Activity Endpoints

- [ ] **TEST**: GET /api/v1/families/{public_id}/pets/

  - [ ] Write test: Returns all pets for family
  - [ ] Implement: `apps/shared/views.py` (PetViewSet)
  - [ ] Write test: Includes last activity timestamps
  - [ ] Implement: Subquery or annotation for last feeding/walking
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: IsFamilyMember permission class

- [ ] **TEST**: POST /api/v1/families/{public_id}/pets/

  - [ ] Write test: Creates pet with name and type
  - [ ] Implement: create() action
  - [ ] Write test: Creates with photo and schedules (JSONField)
  - [ ] Implement: Handle JSONField data
  - [ ] Write test: Returns 201 with pet data
  - [ ] Implement: Status code

- [ ] **TEST**: PATCH /api/v1/pets/{public_id}/

  - [ ] Implement: update() action
  - [ ] Write test: Authorization check
  - [ ] Implement: FamilyAccessMixin

- [ ] **TEST**: DELETE /api/v1/pets/{public_id}/

  - [ ] Implement: destroy() action (soft delete)
  - [ ] Write test: Cascades to activities
  - [ ] Verify: Django cascade deletes

- [ ] **TEST**: POST /api/v1/pets/{public_id}/activities/

  - [ ] Write test: Logs feeding activity
  - [ ] Implement: Custom @action (log_activity)
  - [ ] Write test: Logs walking activity
  - [ ] Implement: Activity type handling
  - [ ] Write test: Sets logged_by to current user
  - [ ] Implement: Auto-populate logged_by
  - [ ] Write test: Sets logged_at to now
  - [ ] Implement: auto_now_add=True on model field

- [ ] **TEST**: GET /api/v1/pets/{public_id}/activities/
  - [ ] Write test: Returns activities for pet
  - [ ] Implement: Custom @action (list_activities)
  - [ ] Write test: Filters by activity_type (query param)
  - [ ] Implement: Type filter
  - [ ] Write test: Limits to recent N activities (query param: ?limit=20)
  - [ ] Implement: Queryset slicing with ordering

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
