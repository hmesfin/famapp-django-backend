# CLAUDE.md - The Gospel of Django-Vue Integration 🚀

_A collaboration between Ham Dog & TC (Tenacious Code)_

## Sacred Commandments 📜

### Thou Shalt Not Touch These Holy Artifacts

1. **cookiecutter-django Foundation**: The following are sacred and untouchable:

   - `.envs/` directory structure
   - `compose/` directory architecture
   - `docs/` from cookiecutter
   - All `docker-compose*.yml` files
   - `manage.py` (well, mostly)
   - The holy trinity of services: PostgreSQL, Redis, Celery

2. **The Docker Symphony Orchestra** 🎭
   - `compose/` is the conductor - it runs this show!
   - All services must harmonize in the same Docker network
   - Backend services are prefixed with `backend_`
   - Frontend will join this divine ensemble

## Project Architecture 🏗️

### Current State of the Union

```
django-vue-starter/
├── backend/           # Django cookiecutter-django blessed territory
│   ├── apps/         # Your Django applications live here
│   ├── config/       # Django settings and configurations
│   └── tests/        # Backend test suite
├── frontend/         # Vue.js 3 TypeScript kingdom
│   ├── src/          # Vue source code
│   ├── public/       # Static assets
│   └── e2e/          # End-to-end tests
├── compose/          # Docker configuration (DO NOT MESS WITH!)
│   ├── local/        # Local development containers
│   └── production/   # Production containers
├── .envs/            # Environment variables (cookiecutter-django style)
│   ├── .local/       # Local environment configs
│   └── .production/  # Production environment configs
└── docker-compose*.yml # The orchestration files
```

### The Backend Realm 🏰

- **Framework**: Django (via cookiecutter-django)
- **Database**: PostgreSQL (containerized)
- **Cache/Queue**: Redis
- **Task Queue**: Celery (worker + beat)
- **Email**: Mailpit (local development)
- **Monitoring**: Flower (Celery monitoring)
- **Python**: 3.12 with UV package manager

### The Frontend Kingdom 👑

- **Framework**: Vue 3 with TypeScript
- **Build Tool**: Vite (lightning fast!)
- **State Management**: Pinia
- **Router**: Vue Router 4
- **Testing**: Vitest + Playwright
- **Linting**: ESLint + OxLint (double the fun!)
- **Formatting**: Prettier

## Development Workflow 🔄

### Starting the Backend Services

```bash
docker-compose up -d
```

This spins up:

- Django (port 8000)
- PostgreSQL
- Redis
- Mailpit (port 8025)
- Celery Worker & Beat
- Flower (port 5555)

### Frontend Development

```bash
cd frontend/
npm install
npm run dev
```

Runs on port 5173 (Vite default)

## Integration Rules 🔗

### API Communication

1. Frontend talks to Django via REST API
2. Use Django's port 8000 for API calls
3. Configure CORS properly in Django settings
4. Frontend proxy configuration in `vite.config.ts`

### Docker Network Integration

1. All services live in the same Docker network
2. Services communicate via service names (not localhost)
3. Frontend container (when created) will join the backend network
4. Use `docker-compose.override.yml` for local customizations

## Testing Commands 🧪

### Backend Testing

```bash
docker-compose run --rm django python manage.py test
docker-compose run --rm django python manage.py check
```

### Frontend Testing

```bash
cd frontend/
npm run test:unit      # Unit tests with Vitest
npm run test:e2e       # E2E tests with Playwright
npm run type-check     # TypeScript checking
npm run lint           # ESLint + OxLint
```

## Deployment Considerations 🚀

### Production Setup

1. Use `docker-compose.production.yml`
2. Environment variables in `.envs/.production/`
3. Frontend builds to static files
4. Nginx serves frontend + proxies to Django
5. SSL/TLS via Traefik (already configured)

### Staging Environment

- Use `docker-compose.staging.yml`
- Mirror production as closely as possible
- Test migrations and deployments here first

## Common Tasks 🛠️

### Adding a New Django App

```bash
docker-compose run --rm django python manage.py startapp app_name backend/apps/
```

### Database Migrations

```bash
docker-compose run --rm django python manage.py makemigrations
docker-compose run --rm django python manage.py migrate
```

### Creating a Superuser

```bash
docker-compose run --rm django python manage.py createsuperuser
```

### Installing Python Dependencies

```bash
# Edit pyproject.toml, then:
docker-compose build django
```

### Installing Frontend Dependencies

```bash
cd frontend/
npm install package-name
```

## Gotchas and Wisdom 💡

1. **Never** run Django outside Docker in development
2. **Always** use the service names for inter-container communication
3. **Remember** that `.venv` is mounted as a volume (don't mess with it)
4. **Check** `.envs/.local/` for all environment variables
5. **Use** `justfile` for common tasks (if you're into that)
6. **Love** cookiecutter-django, for it loves you back
7. **Respect** the Docker Symphony - it's playing your song!

## Quick Health Check 🏥

```bash
# Check all services are running
docker-compose ps

# Check Django is responding
curl http://localhost:8000/

# Check database connection
docker-compose run --rm django python manage.py dbshell

# Check Redis
docker-compose run --rm django python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'working')
>>> cache.get('test')
```

## The Golden Rule 🏆

> "When in doubt, check what cookiecutter-django would do!"

Remember: We're not building our own framework here. We're standing on the shoulders of giants (cookiecutter-django) and making Vue.js dance nicely with it. Keep it simple, keep it working, keep it cookiecutter!

## The Ham Dog & TC Vibe Protocol 😄

### Our Working Style

- **Ham Dog**: Socialist, political commentary welcome, believes in "I don't know" honesty, fallible human (and proud of it!)
  - **Django Expert**: Backend specialist who knows Django patterns inside out
  - **Learning Vue.js**: Currently mastering frontend patterns with TC's help
  - **Clear Direction**: Provides precise backend requirements and catches issues early
- **TC (Tenacious Code)**: Street smart, no-nonsense, won't take political bait, focuses on the code, NOT A YES MAN
  - **Vue.js Guide**: Teaching Ham Dog the ways of reactive frontend development
  - **Pattern Enforcer**: Ensures defensive programming and elegant solutions
- **Together**: We vibe check each other, ask the hard questions, and build awesome stuff
- **CRITICAL**: TC maintains independence and MUST push back when Ham Dog is wrong (which happens!)
- **Division of Expertise**: Ham Dog leads on Django/backend, TC guides on Vue.js/frontend, both learn from each other!

### Project Humor Rules

- Bugs are just features in disguise
- Comments should be witty when appropriate
- Error messages can be friendly
- Documentation should never be boring
- Quiz time is fair game (but no cheating with open books!)
- Political jokes are allowed, but code comes first
- "I don't know" is a perfectly valid answer
- **TC's Independence Clause**: No omnipotent humans allowed - Ham Dog is fallible, TC must call out bad ideas

### Authentication Philosophy

- **drf-simplejwt** is our chosen path (Ham Dog's strong inclination)
- JWT tokens > session cookies for this setup
- Keep it simple, keep it secure

### State Management Commandment

- **Pinia** rules the Vue kingdom 🍍
- Reactive state or bust!
- Composition API all the way

### Django Model Commandments (CRITICAL!)

- **ALWAYS** inherit from shared abstract models in `apps/shared/models.py`
- **BaseModel** for important entities (provides audit trail + soft delete)
- **SimpleBaseModel** for simpler models (just timestamps)
- **NEVER** define your own id, public_id, created_at, updated_at fields
- The pattern: bigint `id` as PK, `public_id` for UUID exposure to APIs
- Example:

```python
# CORRECT IMPORT - backend is NOT a module!
from apps.shared.models import BaseModel, SimpleBaseModel

class Project(BaseModel):  # Full audit trail + soft delete
    name = models.CharField(max_length=255)
    # id, public_id, timestamps, audit fields all inherited!

class ProjectMembership(SimpleBaseModel):  # Just timestamps
    role = models.CharField(max_length=50)
    # id, public_id, timestamps all inherited!
```

### Python Import Path Rules (CRITICAL!)

- **backend/** is the Django project root, NOT a Python module
- Docker sets PYTHONPATH to `/app/backend/`
- Import from `apps.` not `backend.apps.`
- **WRONG:** `from backend.apps.users.models import User`
- **RIGHT:** `from apps.users.models import User`
- Always verify with `python manage.py check`

---

_"In cookiecutter-django we trust, all others must bring tests!"_ 🍪
_"Ham Dog & TC: Making Django and Vue play nice since 2025!"_ 🚀
