# FastAPI Backend Migration - TDD Implementation Plan

## Project Goal

Migrate family scheduler app backend from Supabase to FastAPI, removing offline-first architecture complexity. Focus on simple, online-first API with React Query for caching and optimistic updates. Deploy to Hetzner ($10/month) using existing FastAPI starter with JWT auth, Celery, SendGrid, Twilio, and Cloudflare R2.

## Technology Stack

### Backend (New Repository: `fam-api`)

- **FastAPI** - Async Python web framework
- **SQLAlchemy 2.0** - Async ORM for database operations
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database
- **Redis** - Caching and Celery broker
- **Celery** - Background task processing
- **JWT** - Authentication (from starter)
- **SendGrid** - Transactional emails
- **Twilio** - SMS notifications
- **Cloudflare R2** - Media and static asset storage
- **Docker** - Containerization
- **Pytest** - Testing framework

### Mobile App Changes (This Repository)

- **Remove**: Supabase client, offline-first data layer, sync queue, local storage
- **Add**: React Query for caching, optimistic updates, and server state management
- **Update**: All API services to use axios with FastAPI endpoints

## Migration Phases (TDD Approach)

---

## Phase 1: Backend Setup & Database Models

### 1.1 Repository Setup

- [ ] **SETUP**: Initialize backend repository
  - [ ] Clone FastAPI starter project
  - [ ] Rename to `fam-api`
  - [ ] Update `.env` with project-specific variables
  - [ ] Test starter auth endpoints (signup, login, JWT validation)
  - [ ] Verify Docker Compose setup (PostgreSQL, Redis, FastAPI)
  - [ ] Run starter test suite to ensure clean baseline

### 1.2 Database Models (SQLAlchemy 2.0)

- [ ] **TEST**: Family model
  - [ ] Write test: Create family with name
  - [ ] Implement: `app/models/family.py` (Family model)
  - [ ] Write test: Family relationships (members, todos, pets, etc.)
  - [ ] Implement: SQLAlchemy relationships
  - [ ] Write test: Timestamps (created_at, updated_at)
  - [ ] Implement: Timestamp columns with server defaults
  - [ ] Write test: Cascade deletes (delete family → delete all related data)
  - [ ] Implement: Cascade delete constraints

- [ ] **TEST**: FamilyMember model
  - [ ] Write test: Create family member with user and role
  - [ ] Implement: FamilyMember model (many-to-many relationship)
  - [ ] Write test: Unique constraint (family_id, user_id)
  - [ ] Implement: Unique constraint
  - [ ] Write test: Role enum ('admin', 'member')
  - [ ] Implement: Role validation

- [ ] **TEST**: Todo model
  - [ ] Write test: Create todo with required fields (family_id, title)
  - [ ] Implement: `app/models/todo.py`
  - [ ] Write test: Optional fields (description, assigned_to, due_date)
  - [ ] Implement: Nullable columns
  - [ ] Write test: Completion tracking (completed, completed_at, completed_by)
  - [ ] Implement: Completion fields
  - [ ] Write test: Foreign key relationships (family, assigned_to, created_by, completed_by)
  - [ ] Implement: Foreign key constraints

- [ ] **TEST**: ScheduleEvent model
  - [ ] Write test: Create event with required fields (family_id, title, start_time)
  - [ ] Implement: `app/models/schedule.py`
  - [ ] Write test: Optional fields (end_time, description, recurrence_rule)
  - [ ] Implement: Optional columns
  - [ ] Write test: All-day event flag
  - [ ] Implement: Boolean all_day column
  - [ ] Write test: Assigned_to relationship
  - [ ] Implement: Foreign key to user

- [ ] **TEST**: GroceryItem model
  - [ ] Write test: Create grocery item with required fields (family_id, name)
  - [ ] Implement: `app/models/grocery.py`
  - [ ] Write test: Optional fields (quantity, category)
  - [ ] Implement: Optional columns
  - [ ] Write test: Purchase tracking (purchased, purchased_at, purchased_by)
  - [ ] Implement: Purchase fields
  - [ ] Write test: Added_by relationship
  - [ ] Implement: Foreign key to user

- [ ] **TEST**: Pet model
  - [ ] Write test: Create pet with required fields (family_id, name, type)
  - [ ] Implement: `app/models/pet.py`
  - [ ] Write test: Optional fields (photo_url, feeding_schedule, walking_schedule)
  - [ ] Implement: Optional columns (JSONB for schedules)
  - [ ] Write test: Relationships (family, activities)
  - [ ] Implement: Foreign key and back_populates

- [ ] **TEST**: PetActivity model
  - [ ] Write test: Create activity with required fields (pet_id, activity_type)
  - [ ] Implement: PetActivity model
  - [ ] Write test: Optional fields (notes, logged_by)
  - [ ] Implement: Optional columns
  - [ ] Write test: Logged_at timestamp with default NOW()
  - [ ] Implement: Timestamp with server default
  - [ ] Write test: Foreign key to pet and user
  - [ ] Implement: Foreign key constraints

### 1.3 Alembic Migration

- [ ] **TEST**: Initial migration
  - [ ] Write test: Migration creates all tables
  - [ ] Implement: Alembic migration from models
  - [ ] Write test: Migration creates indexes
  - [ ] Implement: Index creation for foreign keys
  - [ ] Write test: Migration creates constraints
  - [ ] Implement: Foreign key and unique constraints
  - [ ] Write test: Migration is reversible (downgrade)
  - [ ] Implement: Downgrade functions
  - [ ] Run migration on test database
  - [ ] Verify schema matches models

---

## Phase 2: Pydantic Schemas & Validation

### 2.1 Family Schemas

- [ ] **TEST**: Family schemas
  - [ ] Write test: FamilyCreate schema validates name (required, 1-100 chars)
  - [ ] Implement: `app/schemas/family.py` (FamilyCreate)
  - [ ] Write test: FamilyUpdate schema allows partial updates
  - [ ] Implement: FamilyUpdate with all optional fields
  - [ ] Write test: FamilyResponse schema includes id, timestamps
  - [ ] Implement: FamilyResponse with computed fields
  - [ ] Write test: FamilyWithMembers includes member list
  - [ ] Implement: Nested member schema

- [ ] **TEST**: FamilyMember schemas
  - [ ] Write test: MemberResponse includes user info
  - [ ] Implement: MemberResponse with user relationship
  - [ ] Write test: InviteMember schema validates email
  - [ ] Implement: InviteMember with email validation
  - [ ] Write test: UpdateMemberRole validates role enum
  - [ ] Implement: Role enum validation

### 2.2 Todo Schemas

- [ ] **TEST**: Todo schemas
  - [ ] Write test: TodoCreate validates title (required, 1-500 chars)
  - [ ] Implement: `app/schemas/todo.py` (TodoCreate)
  - [ ] Write test: TodoCreate validates due_date (must be future)
  - [ ] Implement: Date validation with validator
  - [ ] Write test: TodoUpdate allows partial updates
  - [ ] Implement: TodoUpdate with all optional fields
  - [ ] Write test: TodoResponse includes computed fields (isOverdue)
  - [ ] Implement: Computed field with @computed_field
  - [ ] Write test: TodoToggleComplete schema
  - [ ] Implement: Simple boolean schema

### 2.3 Schedule Schemas

- [ ] **TEST**: Schedule schemas
  - [ ] Write test: EventCreate validates title and start_time (required)
  - [ ] Implement: `app/schemas/schedule.py` (EventCreate)
  - [ ] Write test: EventCreate validates end_time (must be after start_time)
  - [ ] Implement: Model validator for time range
  - [ ] Write test: EventUpdate allows partial updates
  - [ ] Implement: EventUpdate with all optional fields
  - [ ] Write test: EventResponse includes duration calculation
  - [ ] Implement: Computed duration field

### 2.4 Grocery Schemas

- [ ] **TEST**: Grocery schemas
  - [ ] Write test: GroceryCreate validates name (required, 1-200 chars)
  - [ ] Implement: `app/schemas/grocery.py` (GroceryCreate)
  - [ ] Write test: GroceryCreate validates category (optional enum)
  - [ ] Implement: Category enum with validation
  - [ ] Write test: GroceryUpdate allows partial updates
  - [ ] Implement: GroceryUpdate with all optional fields
  - [ ] Write test: GroceryResponse includes purchaser info
  - [ ] Implement: Nested user schema

### 2.5 Pet Schemas

- [ ] **TEST**: Pet schemas
  - [ ] Write test: PetCreate validates name and type (required)
  - [ ] Implement: `app/schemas/pet.py` (PetCreate)
  - [ ] Write test: PetCreate validates schedule format (list of time strings)
  - [ ] Implement: Schedule validation with regex
  - [ ] Write test: PetUpdate allows partial updates
  - [ ] Implement: PetUpdate with all optional fields
  - [ ] Write test: PetResponse includes last activity timestamps
  - [ ] Implement: Computed fields for last feeding/walking
  - [ ] Write test: PetActivityCreate validates activity_type enum
  - [ ] Implement: ActivityType enum validation
  - [ ] Write test: PetActivityResponse includes logger info
  - [ ] Implement: Nested user schema

---

## Phase 3: Authorization & Dependencies

### 3.1 Family Membership Dependency

- [ ] **TEST**: verify_family_access dependency
  - [ ] Write test: Allows access if user is family member
  - [ ] Implement: `app/api/v1/deps.py` (verify_family_access)
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: HTTP exception on unauthorized access
  - [ ] Write test: Returns Family object on success
  - [ ] Implement: Family query and return
  - [ ] Write test: Works with family_id from path parameter
  - [ ] Implement: Dependency injection from path

- [ ] **TEST**: require_family_admin dependency
  - [ ] Write test: Allows access if user is family admin
  - [ ] Implement: require_family_admin dependency
  - [ ] Write test: Returns 403 if user is member (not admin)
  - [ ] Implement: Role check in membership query
  - [ ] Write test: Returns 403 if user not a member at all
  - [ ] Implement: Combined membership and role check

### 3.2 Resource Authorization Helpers

- [ ] **TEST**: verify_todo_access helper
  - [ ] Write test: Allows access if todo belongs to user's family
  - [ ] Implement: Helper function in deps.py
  - [ ] Write test: Returns 404 if todo doesn't exist
  - [ ] Implement: Not found exception
  - [ ] Write test: Returns 403 if todo not in user's families
  - [ ] Implement: Family membership check

- [ ] **TEST**: Apply pattern to other resources
  - [ ] Implement: verify_event_access
  - [ ] Implement: verify_grocery_access
  - [ ] Implement: verify_pet_access
  - [ ] Write tests for each helper
  - [ ] Implement: Consistent error handling

---

## Phase 4: CRUD Endpoints (Family & Members)

### 4.1 Family Endpoints

- [ ] **TEST**: POST /api/v1/families
  - [ ] Write test: Creates family with authenticated user as admin
  - [ ] Implement: `app/api/v1/endpoints/families.py`
  - [ ] Write test: Returns 201 with family data
  - [ ] Implement: Create handler with status code
  - [ ] Write test: Validates family name (required)
  - [ ] Implement: Pydantic validation
  - [ ] Write test: Returns 401 if not authenticated
  - [ ] Implement: get_current_user dependency

- [ ] **TEST**: GET /api/v1/families
  - [ ] Write test: Returns all families user belongs to
  - [ ] Implement: List families endpoint
  - [ ] Write test: Includes member count for each family
  - [ ] Implement: Count aggregation in query
  - [ ] Write test: Returns empty list if user has no families
  - [ ] Implement: Handle empty result

- [ ] **TEST**: GET /api/v1/families/{family_id}
  - [ ] Write test: Returns family details with members
  - [ ] Implement: Get family by ID endpoint
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: verify_family_access dependency
  - [ ] Write test: Includes member list with roles
  - [ ] Implement: Nested member query

- [ ] **TEST**: PATCH /api/v1/families/{family_id}
  - [ ] Write test: Updates family name (admin only)
  - [ ] Implement: Update family endpoint
  - [ ] Write test: Returns 403 if user not admin
  - [ ] Implement: require_family_admin dependency
  - [ ] Write test: Returns updated family data
  - [ ] Implement: Commit and refresh

- [ ] **TEST**: DELETE /api/v1/families/{family_id}
  - [ ] Write test: Deletes family (admin only)
  - [ ] Implement: Delete family endpoint
  - [ ] Write test: Returns 403 if user not admin
  - [ ] Implement: Admin authorization check
  - [ ] Write test: Cascades to all related data
  - [ ] Implement: Verify cascade deletes work

### 4.2 Family Member Endpoints

- [ ] **TEST**: POST /api/v1/families/{family_id}/members
  - [ ] Write test: Invites user by email (admin only)
  - [ ] Implement: Invite member endpoint
  - [ ] Write test: Creates family member with 'member' role
  - [ ] Implement: Add member with default role
  - [ ] Write test: Sends invitation email via SendGrid
  - [ ] Implement: SendGrid integration
  - [ ] Write test: Returns 400 if user already a member
  - [ ] Implement: Duplicate check
  - [ ] Write test: Returns 404 if user doesn't exist
  - [ ] Implement: User lookup validation

- [ ] **TEST**: GET /api/v1/families/{family_id}/members
  - [ ] Write test: Returns all family members
  - [ ] Implement: List members endpoint
  - [ ] Write test: Includes user info (name, email, avatar)
  - [ ] Implement: Join with users table
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: Family access check

- [ ] **TEST**: PATCH /api/v1/families/{family_id}/members/{user_id}
  - [ ] Write test: Updates member role (admin only)
  - [ ] Implement: Update member role endpoint
  - [ ] Write test: Returns 403 if user not admin
  - [ ] Implement: Admin authorization
  - [ ] Write test: Validates role enum
  - [ ] Implement: Role validation

- [ ] **TEST**: DELETE /api/v1/families/{family_id}/members/{user_id}
  - [ ] Write test: Removes member from family (admin or self)
  - [ ] Implement: Remove member endpoint
  - [ ] Write test: Admin can remove any member
  - [ ] Implement: Admin authorization
  - [ ] Write test: Member can remove themselves
  - [ ] Implement: Self-removal check
  - [ ] Write test: Returns 403 if member tries to remove others
  - [ ] Implement: Authorization logic

---

## Phase 5: CRUD Endpoints (Todos)

### 5.1 Todo Endpoints

- [ ] **TEST**: GET /api/v1/families/{family_id}/todos
  - [ ] Write test: Returns all todos for family
  - [ ] Implement: `app/api/v1/endpoints/todos.py`
  - [ ] Write test: Filters by status (query param: ?completed=true/false)
  - [ ] Implement: Optional status filter
  - [ ] Write test: Filters by assignee (query param: ?assigned_to=user_id)
  - [ ] Implement: Optional assignee filter
  - [ ] Write test: Sorts by due_date ascending
  - [ ] Implement: Default sorting
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: verify_family_access dependency

- [ ] **TEST**: POST /api/v1/families/{family_id}/todos
  - [ ] Write test: Creates todo with title only
  - [ ] Implement: Create todo endpoint
  - [ ] Write test: Creates todo with all fields
  - [ ] Implement: Full todo creation
  - [ ] Write test: Sets created_by to current user
  - [ ] Implement: Auto-populate created_by
  - [ ] Write test: Returns 201 with todo data
  - [ ] Implement: Status code and response
  - [ ] Write test: Validates title required
  - [ ] Implement: Pydantic validation

- [ ] **TEST**: GET /api/v1/todos/{todo_id}
  - [ ] Write test: Returns todo details
  - [ ] Implement: Get todo by ID endpoint
  - [ ] Write test: Returns 404 if todo doesn't exist
  - [ ] Implement: Not found handling
  - [ ] Write test: Returns 403 if todo not in user's families
  - [ ] Implement: verify_todo_access dependency

- [ ] **TEST**: PATCH /api/v1/todos/{todo_id}
  - [ ] Write test: Updates todo fields
  - [ ] Implement: Update todo endpoint
  - [ ] Write test: Allows partial updates
  - [ ] Implement: Optional field handling
  - [ ] Write test: Returns updated todo data
  - [ ] Implement: Commit and refresh
  - [ ] Write test: Returns 403 if todo not in user's families
  - [ ] Implement: Authorization check

- [ ] **TEST**: PATCH /api/v1/todos/{todo_id}/toggle
  - [ ] Write test: Marks incomplete todo as complete
  - [ ] Implement: Toggle completion endpoint
  - [ ] Write test: Sets completed_at and completed_by
  - [ ] Implement: Timestamp and user tracking
  - [ ] Write test: Marks complete todo as incomplete
  - [ ] Implement: Uncomplete logic (clear timestamps)
  - [ ] Write test: Returns updated todo
  - [ ] Implement: Response with updated data

- [ ] **TEST**: DELETE /api/v1/todos/{todo_id}
  - [ ] Write test: Deletes todo
  - [ ] Implement: Delete todo endpoint
  - [ ] Write test: Returns 204 No Content
  - [ ] Implement: Status code
  - [ ] Write test: Returns 403 if todo not in user's families
  - [ ] Implement: Authorization check

---

## Phase 6: CRUD Endpoints (Schedule, Grocery, Pets)

### 6.1 Schedule Event Endpoints

- [ ] **TEST**: GET /api/v1/families/{family_id}/events
  - [ ] Write test: Returns all events for family
  - [ ] Implement: `app/api/v1/endpoints/schedule.py`
  - [ ] Write test: Filters by date range (query params: ?start_date, ?end_date)
  - [ ] Implement: Date range filtering
  - [ ] Write test: Sorts by start_time ascending
  - [ ] Implement: Default sorting
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: verify_family_access dependency

- [ ] **TEST**: POST /api/v1/families/{family_id}/events
  - [ ] Write test: Creates event with required fields
  - [ ] Implement: Create event endpoint
  - [ ] Write test: Validates start_time < end_time
  - [ ] Implement: Time validation
  - [ ] Write test: Sets created_by to current user
  - [ ] Implement: Auto-populate created_by
  - [ ] Write test: Returns 201 with event data
  - [ ] Implement: Status code and response

- [ ] **TEST**: GET /api/v1/events/{event_id}
  - [ ] Implement: Get event by ID
  - [ ] Write test: Authorization check
  - [ ] Implement: verify_event_access dependency

- [ ] **TEST**: PATCH /api/v1/events/{event_id}
  - [ ] Implement: Update event endpoint
  - [ ] Write test: Partial updates
  - [ ] Implement: Optional field handling

- [ ] **TEST**: DELETE /api/v1/events/{event_id}
  - [ ] Implement: Delete event endpoint
  - [ ] Write test: Returns 204
  - [ ] Implement: Status code

### 6.2 Grocery Item Endpoints

- [ ] **TEST**: GET /api/v1/families/{family_id}/groceries
  - [ ] Write test: Returns all grocery items for family
  - [ ] Implement: `app/api/v1/endpoints/groceries.py`
  - [ ] Write test: Filters by purchased status (query param: ?purchased=true/false)
  - [ ] Implement: Status filter
  - [ ] Write test: Filters by category (query param: ?category=produce)
  - [ ] Implement: Category filter
  - [ ] Write test: Groups by category (query param: ?group_by=category)
  - [ ] Implement: Category grouping logic

- [ ] **TEST**: POST /api/v1/families/{family_id}/groceries
  - [ ] Write test: Creates grocery item with name only
  - [ ] Implement: Create grocery endpoint
  - [ ] Write test: Creates with quantity and category
  - [ ] Implement: Full item creation
  - [ ] Write test: Sets added_by to current user
  - [ ] Implement: Auto-populate added_by

- [ ] **TEST**: PATCH /api/v1/groceries/{item_id}/toggle
  - [ ] Write test: Marks item as purchased
  - [ ] Implement: Toggle purchased endpoint
  - [ ] Write test: Sets purchased_at and purchased_by
  - [ ] Implement: Timestamp and user tracking
  - [ ] Write test: Unpurchase item (clear timestamps)
  - [ ] Implement: Unpurchase logic

- [ ] **TEST**: DELETE /api/v1/groceries/{item_id}
  - [ ] Implement: Delete grocery item endpoint

- [ ] **TEST**: DELETE /api/v1/families/{family_id}/groceries/purchased
  - [ ] Write test: Bulk deletes all purchased items
  - [ ] Implement: Clear purchased items endpoint
  - [ ] Write test: Returns count of deleted items
  - [ ] Implement: Count response

### 6.3 Pet & Activity Endpoints

- [ ] **TEST**: GET /api/v1/families/{family_id}/pets
  - [ ] Write test: Returns all pets for family
  - [ ] Implement: `app/api/v1/endpoints/pets.py`
  - [ ] Write test: Includes last activity timestamps
  - [ ] Implement: Subquery for last feeding/walking
  - [ ] Write test: Returns 403 if user not a member
  - [ ] Implement: verify_family_access dependency

- [ ] **TEST**: POST /api/v1/families/{family_id}/pets
  - [ ] Write test: Creates pet with name and type
  - [ ] Implement: Create pet endpoint
  - [ ] Write test: Creates with photo and schedules
  - [ ] Implement: Full pet creation with JSONB schedules
  - [ ] Write test: Returns 201 with pet data
  - [ ] Implement: Status code and response

- [ ] **TEST**: PATCH /api/v1/pets/{pet_id}
  - [ ] Implement: Update pet endpoint
  - [ ] Write test: Authorization check
  - [ ] Implement: verify_pet_access dependency

- [ ] **TEST**: DELETE /api/v1/pets/{pet_id}
  - [ ] Implement: Delete pet endpoint
  - [ ] Write test: Cascades to activities
  - [ ] Implement: Verify cascade works

- [ ] **TEST**: POST /api/v1/pets/{pet_id}/activities
  - [ ] Write test: Logs feeding activity
  - [ ] Implement: Log activity endpoint
  - [ ] Write test: Logs walking activity
  - [ ] Implement: Activity type handling
  - [ ] Write test: Sets logged_by to current user
  - [ ] Implement: Auto-populate logged_by
  - [ ] Write test: Sets logged_at to now
  - [ ] Implement: Default timestamp

- [ ] **TEST**: GET /api/v1/pets/{pet_id}/activities
  - [ ] Write test: Returns activities for pet
  - [ ] Implement: Get activities endpoint
  - [ ] Write test: Filters by activity_type (query param)
  - [ ] Implement: Type filter
  - [ ] Write test: Limits to recent N activities (query param: ?limit=20)
  - [ ] Implement: Limit and sorting

---

## Phase 7: Background Jobs (Celery)

### 7.1 Pet Care Reminders

- [ ] **TEST**: schedule_pet_feeding_reminder task
  - [ ] Write test: Schedules daily SMS for pet feeding
  - [ ] Implement: `app/tasks/pet_reminders.py`
  - [ ] Write test: Uses Twilio to send SMS to family members
  - [ ] Implement: Twilio integration
  - [ ] Write test: Sends at configured feeding times
  - [ ] Implement: Schedule parsing from pet.feeding_schedule
  - [ ] Write test: Doesn't send if already fed today
  - [ ] Implement: Activity check before sending

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
  - [ ] Implement: `app/tasks/todo_reminders.py`
  - [ ] Write test: Uses SendGrid for email
  - [ ] Implement: SendGrid integration
  - [ ] Write test: Configurable lead time (e.g., 1 hour before)
  - [ ] Implement: Lead time parameter
  - [ ] Write test: Only sends if todo incomplete
  - [ ] Implement: Status check

- [ ] **TEST**: schedule_event_reminder task
  - [ ] Write test: Sends email reminder before event
  - [ ] Implement: `app/tasks/event_reminders.py`
  - [ ] Write test: Uses SendGrid for email
  - [ ] Implement: SendGrid integration
  - [ ] Write test: Configurable lead time (e.g., 15 minutes before)
  - [ ] Implement: Lead time parameter

### 7.3 Celery Beat Configuration

- [ ] **TEST**: Periodic task scheduling
  - [ ] Write test: Pet reminders run at configured times
  - [ ] Implement: Celery Beat schedule configuration
  - [ ] Write test: Daily digest email task
  - [ ] Implement: Family daily summary task
  - [ ] Write test: Cleanup old completed todos (30 days)
  - [ ] Implement: Cleanup task

---

## Phase 8: Mobile App - Remove Offline-First

### 8.1 Cleanup Offline-First Code

- [ ] **DELETE**: Offline-first infrastructure
  - [ ] Delete `src/services/data/` directory (todoDataService, groceryDataService, etc.)
  - [ ] Delete `src/services/storage/` directory (todoStorage, groceryStorage, etc.)
  - [ ] Delete `src/services/sync/` directory (syncQueue, networkStatus)
  - [ ] Delete `src/services/api/mappers/` directory
  - [ ] Delete `src/services/auth/supabaseAuth.ts`
  - [ ] Delete `src/services/api/supabaseClient.ts`
  - [ ] Uninstall `@supabase/supabase-js` from package.json
  - [ ] Remove Supabase-related tests

### 8.2 Install React Query

- [ ] **SETUP**: React Query installation
  - [ ] Install `@tanstack/react-query`
  - [ ] Wrap App.tsx with QueryClientProvider
  - [ ] Configure QueryClient (staleTime, cacheTime, retry logic)
  - [ ] Add React Query DevTools (optional, for debugging)

---

## Phase 9: Mobile App - Update API Client

### 9.1 API Client Configuration

- [ ] **TEST**: API client setup
  - [ ] Write test: Client uses correct base URL (dev vs production)
  - [ ] Implement: Update `src/services/api/client.ts` with FastAPI URL
  - [ ] Write test: Request interceptor adds JWT token
  - [ ] Implement: Token interceptor from AsyncStorage
  - [ ] Write test: Response interceptor handles 401 (logout)
  - [ ] Implement: 401 error handler
  - [ ] Write test: Response interceptor handles network errors
  - [ ] Implement: Global error handling

### 9.2 Auth Service

- [ ] **TEST**: AuthApi service
  - [ ] Write test: login() calls POST /api/v1/auth/login
  - [ ] Implement: `src/services/api/authApi.ts`
  - [ ] Write test: login() stores JWT in AsyncStorage
  - [ ] Implement: Token storage
  - [ ] Write test: signup() calls POST /api/v1/auth/signup
  - [ ] Implement: Signup method
  - [ ] Write test: signup() stores JWT in AsyncStorage
  - [ ] Implement: Token storage
  - [ ] Write test: logout() removes JWT from AsyncStorage
  - [ ] Implement: Logout method
  - [ ] Write test: getCurrentUser() calls GET /api/v1/auth/me
  - [ ] Implement: Current user method

- [ ] **TEST**: useAuth hook
  - [ ] Write test: useAuth returns login/signup/logout functions
  - [ ] Implement: Update `src/hooks/useAuth.ts` to use AuthApi
  - [ ] Write test: useAuth tracks authentication state
  - [ ] Implement: State management with React Query
  - [ ] Write test: useAuth refetches user on app foreground
  - [ ] Implement: Focus refetch

---

## Phase 10: Mobile App - Simplify API Services

### 10.1 Todo API Service

- [ ] **TEST**: TodoApi service
  - [ ] Write test: fetchTodos() calls GET /families/{id}/todos
  - [ ] Implement: Rewrite `src/services/api/todoApi.ts` (remove Supabase)
  - [ ] Write test: createTodo() calls POST /families/{id}/todos
  - [ ] Implement: Create method
  - [ ] Write test: updateTodo() calls PATCH /todos/{id}
  - [ ] Implement: Update method
  - [ ] Write test: toggleTodo() calls PATCH /todos/{id}/toggle
  - [ ] Implement: Toggle method
  - [ ] Write test: deleteTodo() calls DELETE /todos/{id}
  - [ ] Implement: Delete method

### 10.2 Grocery API Service

- [ ] **TEST**: GroceryApi service
  - [ ] Write test: fetchGroceries() calls GET /families/{id}/groceries
  - [ ] Implement: Rewrite `src/services/api/groceryApi.ts`
  - [ ] Write test: createGrocery() calls POST /families/{id}/groceries
  - [ ] Implement: Create method
  - [ ] Write test: updateGrocery() calls PATCH /groceries/{id}
  - [ ] Implement: Update method
  - [ ] Write test: toggleGrocery() calls PATCH /groceries/{id}/toggle
  - [ ] Implement: Toggle method
  - [ ] Write test: deleteGrocery() calls DELETE /groceries/{id}
  - [ ] Implement: Delete method
  - [ ] Write test: clearPurchased() calls DELETE /families/{id}/groceries/purchased
  - [ ] Implement: Bulk clear method

### 10.3 Pet API Service

- [ ] **TEST**: PetApi service
  - [ ] Write test: fetchPets() calls GET /families/{id}/pets
  - [ ] Implement: Rewrite `src/services/api/petApi.ts`
  - [ ] Write test: createPet() calls POST /families/{id}/pets
  - [ ] Implement: Create method
  - [ ] Write test: updatePet() calls PATCH /pets/{id}
  - [ ] Implement: Update method
  - [ ] Write test: deletePet() calls DELETE /pets/{id}
  - [ ] Implement: Delete method
  - [ ] Write test: logActivity() calls POST /pets/{id}/activities
  - [ ] Implement: Log activity method
  - [ ] Write test: fetchActivities() calls GET /pets/{id}/activities
  - [ ] Implement: Fetch activities method

### 10.4 Schedule API Service

- [ ] **TEST**: ScheduleApi service
  - [ ] Write test: fetchEvents() calls GET /families/{id}/events
  - [ ] Implement: Rewrite `src/services/api/scheduleApi.ts`
  - [ ] Write test: createEvent() calls POST /families/{id}/events
  - [ ] Implement: Create method
  - [ ] Write test: updateEvent() calls PATCH /events/{id}
  - [ ] Implement: Update method
  - [ ] Write test: deleteEvent() calls DELETE /events/{id}
  - [ ] Implement: Delete method

### 10.5 Family API Service

- [ ] **TEST**: FamilyApi service (NEW)
  - [ ] Write test: fetchFamilies() calls GET /families
  - [ ] Implement: Create `src/services/api/familyApi.ts`
  - [ ] Write test: fetchFamily() calls GET /families/{id}
  - [ ] Implement: Get by ID method
  - [ ] Write test: createFamily() calls POST /families
  - [ ] Implement: Create method
  - [ ] Write test: updateFamily() calls PATCH /families/{id}
  - [ ] Implement: Update method
  - [ ] Write test: deleteFamily() calls DELETE /families/{id}
  - [ ] Implement: Delete method
  - [ ] Write test: inviteMember() calls POST /families/{id}/members
  - [ ] Implement: Invite method
  - [ ] Write test: removeMember() calls DELETE /families/{id}/members/{userId}
  - [ ] Implement: Remove method

---

## Phase 11: Mobile App - React Query Hooks

### 11.1 Todo Hooks

- [ ] **TEST**: useTodos hook
  - [ ] Write test: Fetches todos with useQuery
  - [ ] Implement: `src/hooks/useTodos.ts`
  - [ ] Write test: Caches for 30 seconds
  - [ ] Implement: staleTime configuration
  - [ ] Write test: createTodo mutation with optimistic update
  - [ ] Implement: useMutation with onMutate
  - [ ] Write test: Rollback on error
  - [ ] Implement: onError with context restore
  - [ ] Write test: Refetch after mutation settles
  - [ ] Implement: onSettled with invalidateQueries
  - [ ] Write test: updateTodo mutation
  - [ ] Implement: Update mutation
  - [ ] Write test: deleteTodo mutation
  - [ ] Implement: Delete mutation

### 11.2 Grocery Hooks

- [ ] **TEST**: useGroceries hook
  - [ ] Write test: Fetches groceries with useQuery
  - [ ] Implement: `src/hooks/useGroceries.ts`
  - [ ] Write test: createGrocery mutation with optimistic update
  - [ ] Implement: Optimistic create
  - [ ] Write test: toggleGrocery mutation
  - [ ] Implement: Toggle mutation
  - [ ] Write test: deleteGrocery mutation
  - [ ] Implement: Delete mutation
  - [ ] Write test: clearPurchased mutation
  - [ ] Implement: Bulk clear mutation

### 11.3 Pet Hooks

- [ ] **TEST**: usePets hook
  - [ ] Write test: Fetches pets with useQuery
  - [ ] Implement: `src/hooks/usePets.ts`
  - [ ] Write test: createPet mutation with optimistic update
  - [ ] Implement: Optimistic create
  - [ ] Write test: updatePet mutation
  - [ ] Implement: Update mutation
  - [ ] Write test: deletePet mutation
  - [ ] Implement: Delete mutation

- [ ] **TEST**: usePetActivities hook
  - [ ] Write test: Fetches activities for pet
  - [ ] Implement: `src/hooks/usePetActivities.ts`
  - [ ] Write test: logActivity mutation with optimistic update
  - [ ] Implement: Optimistic log
  - [ ] Write test: Invalidates pet query after logging (refresh last activity)
  - [ ] Implement: Query invalidation

### 11.4 Schedule Hooks

- [ ] **TEST**: useSchedule hook
  - [ ] Write test: Fetches events with date range filter
  - [ ] Implement: `src/hooks/useSchedule.ts`
  - [ ] Write test: createEvent mutation with optimistic update
  - [ ] Implement: Optimistic create
  - [ ] Write test: updateEvent mutation
  - [ ] Implement: Update mutation
  - [ ] Write test: deleteEvent mutation
  - [ ] Implement: Delete mutation

### 11.5 Family Hooks

- [ ] **TEST**: useFamilies hook
  - [ ] Write test: Fetches user's families
  - [ ] Implement: `src/hooks/useFamilies.ts`
  - [ ] Write test: createFamily mutation
  - [ ] Implement: Create mutation

- [ ] **TEST**: useFamily hook
  - [ ] Write test: Fetches single family with members
  - [ ] Implement: `src/hooks/useFamily.ts`
  - [ ] Write test: updateFamily mutation
  - [ ] Implement: Update mutation
  - [ ] Write test: inviteMember mutation
  - [ ] Implement: Invite mutation
  - [ ] Write test: removeMember mutation
  - [ ] Implement: Remove mutation

---

## Phase 12: Mobile App - Update Screens

### 12.1 Authentication Screens

- [ ] **TEST**: LoginScreen
  - [ ] Write test: Calls AuthApi.login() on submit
  - [ ] Implement: Update `src/screens/auth/LoginScreen.tsx`
  - [ ] Write test: Navigates to home on success
  - [ ] Implement: Navigation with useAuth
  - [ ] Write test: Shows error on failure
  - [ ] Implement: Error display
  - [ ] Write test: Loading state
  - [ ] Implement: Disable button during login

- [ ] **TEST**: SignupScreen
  - [ ] Write test: Calls AuthApi.signup() on submit
  - [ ] Implement: Update `src/screens/auth/SignupScreen.tsx`
  - [ ] Write test: Auto-creates family after signup
  - [ ] Implement: Family creation in signup flow
  - [ ] Write test: Navigates to home on success
  - [ ] Implement: Navigation
  - [ ] Write test: Shows error on failure
  - [ ] Implement: Error display

### 12.2 Todo Screens

- [ ] **TEST**: TodoListScreen
  - [ ] Write test: Uses useTodos hook
  - [ ] Implement: Update `src/screens/TodoListScreen.tsx`
  - [ ] Write test: Shows loading state
  - [ ] Implement: isLoading from useQuery
  - [ ] Write test: Shows error state
  - [ ] Implement: error from useQuery
  - [ ] Write test: Toggle todo calls mutation
  - [ ] Implement: toggleTodo from useTodos
  - [ ] Write test: Delete todo calls mutation
  - [ ] Implement: deleteTodo from useTodos
  - [ ] Write test: Pull-to-refresh refetches
  - [ ] Implement: refetch from useQuery

- [ ] **TEST**: AddTodoScreen
  - [ ] Write test: Calls createTodo mutation on submit
  - [ ] Implement: Update `src/screens/AddTodoScreen.tsx`
  - [ ] Write test: Navigates back on success
  - [ ] Implement: Navigation in onSuccess
  - [ ] Write test: Shows error on failure
  - [ ] Implement: Error display

### 12.3 Grocery Screen

- [ ] **TEST**: GroceryScreen
  - [ ] Write test: Uses useGroceries hook
  - [ ] Implement: Update `src/screens/GroceryScreen.tsx`
  - [ ] Write test: Toggle grocery calls mutation
  - [ ] Implement: toggleGrocery from useGroceries
  - [ ] Write test: Clear purchased calls mutation
  - [ ] Implement: clearPurchased from useGroceries
  - [ ] Write test: Add grocery modal integration
  - [ ] Implement: Modal with createGrocery mutation

### 12.4 Pets Screen

- [ ] **TEST**: PetsScreen
  - [ ] Write test: Uses usePets hook
  - [ ] Implement: Update `src/screens/PetsScreen.tsx`
  - [ ] Write test: Log feeding calls logActivity mutation
  - [ ] Implement: Feed button with usePetActivities
  - [ ] Write test: Log walking calls logActivity mutation
  - [ ] Implement: Walk button with usePetActivities
  - [ ] Write test: Add pet modal integration
  - [ ] Implement: Modal with createPet mutation

### 12.5 Schedule Screen

- [ ] **TEST**: ScheduleScreen
  - [ ] Write test: Uses useSchedule hook with date range
  - [ ] Implement: Update `src/screens/ScheduleScreen.tsx` (if exists)
  - [ ] Write test: Add event calls createEvent mutation
  - [ ] Implement: Create event flow
  - [ ] Write test: Update event calls updateEvent mutation
  - [ ] Implement: Update event flow
  - [ ] Write test: Delete event calls deleteEvent mutation
  - [ ] Implement: Delete event flow

### 12.6 Family Screen

- [ ] **TEST**: FamilyScreen
  - [ ] Write test: Uses useFamily hook
  - [ ] Implement: Update `src/screens/FamilyScreen.tsx`
  - [ ] Write test: Invite member calls inviteMember mutation
  - [ ] Implement: Invite flow with email input
  - [ ] Write test: Remove member calls removeMember mutation
  - [ ] Implement: Remove member flow
  - [ ] Write test: Update family name calls updateFamily mutation
  - [ ] Implement: Edit family name flow

### 12.7 Dashboard Screen

- [ ] **TEST**: DashboardScreen
  - [ ] Write test: Fetches summary data (todos, events, pets)
  - [ ] Implement: Update `src/screens/DashboardScreen.tsx`
  - [ ] Write test: Shows overdue todos count
  - [ ] Implement: Filtered count with useTodos
  - [ ] Write test: Shows today's events
  - [ ] Implement: Filtered events with useSchedule
  - [ ] Write test: Shows pet care status
  - [ ] Implement: Pet status with usePets

---

## Phase 13: Testing & Polish

### 13.1 Backend Testing

- [ ] **TEST**: API endpoint integration tests
  - [ ] Write tests for all endpoints (CRUD operations)
  - [ ] Test authorization (403 errors)
  - [ ] Test validation (400 errors)
  - [ ] Test not found (404 errors)
  - [ ] Test cascading deletes
  - [ ] Test pagination (if implemented)
  - [ ] Test filtering and sorting

- [ ] **TEST**: Background task tests
  - [ ] Mock Celery and test task functions
  - [ ] Mock SendGrid and test email sending
  - [ ] Mock Twilio and test SMS sending
  - [ ] Test task scheduling and retries

- [ ] **TEST**: Database tests
  - [ ] Test model constraints (unique, foreign keys)
  - [ ] Test cascading deletes
  - [ ] Test timestamps (created_at, updated_at)

### 13.2 Mobile Testing

- [ ] **TEST**: Update mock files
  - [ ] Remove Supabase mocks
  - [ ] Add axios mocks for FastAPI endpoints
  - [ ] Mock React Query in tests

- [ ] **TEST**: Screen tests
  - [ ] Update all screen tests to use new API services
  - [ ] Test loading states
  - [ ] Test error states
  - [ ] Test optimistic updates
  - [ ] Test refetching behavior

- [ ] **TEST**: Hook tests
  - [ ] Test each React Query hook in isolation
  - [ ] Test optimistic update behavior
  - [ ] Test error rollback behavior
  - [ ] Test cache invalidation

### 13.3 End-to-End Testing

- [ ] **TEST**: Critical user flows
  - [ ] Test signup → create family → add todo → complete todo
  - [ ] Test invite member → accept invitation → view shared data
  - [ ] Test log pet activity → receive reminder (mocked)
  - [ ] Test create event → receive reminder (mocked)

### 13.4 Code Quality

- [ ] **QUALITY**: Backend code review
  - [ ] Run Ruff linting
  - [ ] Run Black formatting
  - [ ] Check type hints (mypy)
  - [ ] Review error handling consistency
  - [ ] Review logging statements

- [ ] **QUALITY**: Mobile code review
  - [ ] Run ESLint
  - [ ] Run Prettier
  - [ ] Run TypeScript type checking
  - [ ] Review error handling consistency
  - [ ] Review loading state patterns

---

## Phase 14: Deployment

### 14.1 Backend Deployment (Hetzner)

- [ ] **DEPLOY**: Docker setup
  - [ ] Build Docker image for FastAPI
  - [ ] Create docker-compose.yml (FastAPI, PostgreSQL, Redis, Celery worker)
  - [ ] Configure environment variables (.env)
  - [ ] Test local Docker Compose deployment

- [ ] **DEPLOY**: Hetzner server setup
  - [ ] Provision Hetzner VPS ($10/month)
  - [ ] Install Docker and Docker Compose
  - [ ] Configure firewall (allow 80, 443, 22)
  - [ ] Setup SSL with Let's Encrypt (Traefik or Certbot)

- [ ] **DEPLOY**: Database setup
  - [ ] Run PostgreSQL in Docker container
  - [ ] Configure persistent volumes
  - [ ] Run Alembic migrations
  - [ ] Create production database backup strategy

- [ ] **DEPLOY**: Application deployment
  - [ ] Deploy FastAPI via docker-compose up -d
  - [ ] Verify API health endpoint (GET /health)
  - [ ] Test authentication endpoints
  - [ ] Monitor logs for errors

- [ ] **DEPLOY**: Background workers
  - [ ] Deploy Celery worker container
  - [ ] Deploy Celery Beat scheduler container
  - [ ] Verify Redis connection
  - [ ] Test scheduled tasks

### 14.2 Mobile App Configuration

- [ ] **CONFIG**: Update API base URL
  - [ ] Set production URL in app.config.js
  - [ ] Test API connection from mobile app
  - [ ] Verify authentication flow
  - [ ] Test CRUD operations

- [ ] **CONFIG**: Build and test
  - [ ] Build Android APK (expo build:android)
  - [ ] Build iOS IPA (expo build:ios)
  - [ ] Test on physical devices
  - [ ] Verify push notifications (if applicable)

### 14.3 Monitoring & Observability

- [ ] **MONITOR**: Backend monitoring
  - [ ] Setup logging (structured logs with loguru or Python logging)
  - [ ] Setup error tracking (Sentry or similar)
  - [ ] Setup uptime monitoring (UptimeRobot or similar)
  - [ ] Setup performance monitoring (FastAPI middleware)

- [ ] **MONITOR**: Database monitoring
  - [ ] Monitor connection pool usage
  - [ ] Monitor query performance
  - [ ] Setup automated backups (daily)
  - [ ] Test restore from backup

---

## Success Metrics

- [ ] **Backend**: All 100+ API tests passing
- [ ] **Backend**: 90%+ code coverage
- [ ] **Mobile**: All screen and hook tests passing
- [ ] **Mobile**: No Supabase dependencies remaining
- [ ] **Mobile**: React Query caching working correctly
- [ ] **E2E**: Critical user flows tested and working
- [ ] **Performance**: API response time <200ms (95th percentile)
- [ ] **Performance**: Mobile app startup <2s
- [ ] **Cost**: Hosting cost ≤$10/month on Hetzner
- [ ] **Reliability**: 99.5%+ uptime for backend API

---

## Migration Timeline Estimate

### Backend Development: 10-12 hours
- Phase 1: Setup & Models (2-3 hours)
- Phase 2: Schemas (1-2 hours)
- Phase 3: Authorization (1 hour)
- Phase 4-6: CRUD Endpoints (4-5 hours)
- Phase 7: Background Jobs (2 hours)

### Mobile Development: 6-8 hours
- Phase 8: Cleanup (1 hour)
- Phase 9: API Client (1 hour)
- Phase 10: API Services (2 hours)
- Phase 11: React Query Hooks (2-3 hours)
- Phase 12: Update Screens (1-2 hours)

### Testing & Deployment: 2-4 hours
- Phase 13: Testing (1-2 hours)
- Phase 14: Deployment (1-2 hours)

**Total Estimate**: 18-24 hours

---

## Notes

- **TDD Discipline**: Write tests FIRST, then implement (Red-Green-Refactor)
- **No Real-time**: Polling with React Query refetchInterval is sufficient
- **Simplicity**: Remove unnecessary complexity from offline-first architecture
- **Cost Savings**: $180/year savings ($25 Supabase → $10 Hetzner)
- **Full Control**: Own the entire stack, no vendor lock-in
- **Future Features**: Celery enables background jobs (reminders, notifications, data exports)
