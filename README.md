# Jinubia Learning Nexus Hub (JLN Hub)

An offline-first educational application designed to deliver South Sudan's national curriculum to primary and secondary school learners, regardless of internet availability or infrastructure constraints.

## Deployed link: https://jln-hub-production-a5de.up.railway.app/

## Architecture

JLN Hub is built as a **Django monorepo** where both backend API and frontend are integrated into a single Django application. This architecture provides:
- Unified deployment (single service to deploy)
- Simplified static file handling with WhiteNoise
- Django template system for HTML pages
- Modular JavaScript with ES6 modules
- Component-based frontend architecture

## Project Description

JLN Hub is a full-stack learning platform that packages curriculum lessons, assessments, guided practice, and learning feedback into a single application. The platform features:

- **Offline Curriculum Capsules**: Self-contained learning units accessible without internet
- **Interactive Lessons**: Structured digital lessons with examples and practice activities
- **Embedded Quizzes**: Real-time assessment with instant feedback
- **Adaptive Learning Pathways**: Personalized learning based on performance
- **Progress Tracking**: Local tracking of learner progress and achievements
- **Teacher Dashboard**: Performance summaries and learning analytics

## Technology Stack

### Backend
- Django 5.0.6
- Django REST Framework 3.15.1
- SQLite (offline-first database)
- Django CORS Headers
- WhiteNoise (static file serving)
- PyPDF2 & pdfplumber (PDF processing)
- OpenAI/OpenRouter API (AI lesson generation)

### Frontend (Integrated with Django)
- Vanilla JavaScript (ES6+ modules)
- HTML5 templates served by Django
- CSS3 with CSS Grid & Flexbox
- Responsive Design
- Component-based architecture

## Project Structure

```
JLN Hub/
├── backend/
│   ├── jln_hub/              # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   ├── templates/        # HTML templates
│   │   │   ├── *.html        # Main pages
│   │   │   └── pages/        # Auth pages (login, register)
│   │   └── static/           # Frontend static files
│   │       ├── app.js
│   │       ├── index.js
│   │       ├── styles.css
│   │       ├── components/   # Reusable UI components
│   │       ├── pages/        # Page-specific JavaScript modules
│   │       └── utils/        # Utility functions (API, helpers)
│   ├── api/                  # REST API application
│   │   ├── models.py         # Database models
│   │   ├── serializers/      # API serializers (modular)
│   │   ├── views/            # API endpoints (modular)
│   │   ├── services/         # Business logic (AI, PDF processing)
│   │   ├── urls.py           # API routing
│   │   └── admin.py          # Admin interface
│   ├── manage.py
│   ├── requirements.txt
│   └── db.sqlite3            # SQLite database
├── doc/                      # Project documentation
├── assets/                   # Screenshots and media
└── railway.json              # Railway deployment config
```

**GitHub repo links**
   - Main repo: https://github.com/Latjor-Wuon/jlk-hub
   - Backend API: https://github.com/Latjor-Wuon/jlk-hub/tree/master/backend
   - Demo & Screenshots: https://github.com/Latjor-Wuon/jlk-hub/tree/master/assets

## File Organization

### Templates (HTML)
Located in `backend/jln_hub/templates/`:
- Main pages: `home.html`, `subjects.html`, `lessons.html`, `quizzes.html`, etc.
- Auth pages: `pages/login.html`, `pages/register.html`

### Static Files (CSS, JS)
Located in `backend/jln_hub/static/`:
- **Stylesheets**: `styles.css`
- **Page Modules**: `pages/HomePage.js`, `pages/SubjectsPage.js`, etc.
- **Components**: `components/auth.js`, `components/Navigation.js`, etc.
- **Utilities**: `utils/api.js`, `utils/common.js`, `utils/helpers.js`

### API Code
Located in `backend/api/`:
- **Models**: `models.py` (database schemas)
- **Views**: `views/` (API endpoints by feature)
- **Serializers**: `serializers/` (data transformation)
- **Services**: `services/` (business logic, AI processing)
   
## Setup Instructions

### Quick Start

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver

# Visit http://localhost:8000/
```

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "c:\Users\tharc\Desktop\JLN Hub"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   cd backend
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create your admin account.

7. **Load sample data (optional)**
   ```bash
   python manage.py populate_data
   python manage.py populate_simulations
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Homepage: http://localhost:8000/ (redirects to home.html)
   - Main App: http://localhost:8000/home.html
   - Login: http://localhost:8000/pages/login.html
   - Register: http://localhost:8000/pages/register.html
   - API Root: http://localhost:8000/api/
   - Admin Panel: http://localhost:8000/admin/
  

## API Endpoints

### Subjects
- `GET /api/subjects/` - List all subjects

### Grades
- `GET /api/grades/` - List all grade levels

### Curriculum Capsules (Lessons)
- `GET /api/capsules/` - List all published lessons
- `GET /api/capsules/{id}/` - Get lesson details
- `GET /api/capsules/featured/` - Get featured lessons
- Query Parameters: `?subject={id}&grade={id}`

### Quizzes
- `GET /api/quizzes/` - List all quizzes
- `GET /api/quizzes/{id}/` - Get quiz details
- `POST /api/quizzes/{id}/submit/` - Submit quiz answers

### Learning Progress
- `GET /api/progress/` - Get user progress
- `POST /api/progress/` - Create/update progress
- `GET /api/progress/summary/` - Get progress summary

### Adaptive Learning
- `GET /api/adaptive/pathway/` - Get personalized learning pathway
- `POST /api/adaptive/analyze_quiz/` - Analyze quiz for recommendations
- `POST /api/adaptive/dismiss_recommendation/` - Dismiss a recommendation
- `GET /api/adaptive/revision_history/` - Get revision history

### AI-Assisted Lesson Generation (New!)
- `GET /api/chapters/` - List all textbook chapters
- `POST /api/chapters/` - Upload a new textbook chapter
- `POST /api/chapters/{id}/generate_lesson/` - Generate lesson from chapter
- `POST /api/chapters/batch_generate/` - Batch generate lessons
- `GET /api/chapters/statistics/` - Get chapter processing statistics
- `GET /api/generated-lessons/` - List generated lessons
- `GET /api/generated-lessons/{id}/` - Get lesson details
- `POST /api/generated-lessons/{id}/review/` - Review and approve/reject lesson
- `POST /api/generated-lessons/{id}/publish/` - Publish lesson to curriculum
- `POST /api/generated-lessons/{id}/regenerate_questions/` - Regenerate questions
- `GET /api/generated-lessons/pending_review/` - Get lessons pending review
- `GET /api/generated-lessons/statistics/` - Get lesson generation statistics

### Simulations
- `GET /api/simulations/` - List all simulations
- `GET /api/simulations/{id}/` - Get simulation details
- `POST /api/simulations/{id}/start/` - Start a simulation
- `POST /api/simulations/{id}/complete/` - Complete a simulation
- `GET /api/simulations/{id}/hints/` - Get simulation hints
- `GET /api/simulations/types/` - Get simulation types
- `GET /api/simulations/by_capsule/?capsule_id={id}` - Get simulations for a capsule

### Dashboard
- `GET /api/dashboard/stats/` - Get application statistics
- `GET /api/dashboard/admin_stats/` - Get admin dashboard statistics

## Features Implementation Status

### Core Features
- ✅ Basic project structure
- ✅ Database models for curriculum content
- ✅ REST API endpoints
- ✅ Frontend UI with responsive design
- ✅ User authentication system

### Feature 1: Offline Curriculum Capsules
- ✅ Self-contained learning units
- ✅ Lesson explanations and examples
- ✅ Grade-level objectives alignment
- ✅ SQLite database for offline storage

### Feature 2: AI-Assisted Interactive Lesson Generation
- ✅ Textbook chapter upload and management
- ✅ AI-powered content transformation (OpenAI API & rule-based)
- ✅ Structured lesson format with multiple sections
- ✅ Automatic learning objectives extraction
- ✅ Key concepts identification
- ✅ Embedded practice questions generation
- ✅ Review and approval workflow
- ✅ Batch processing support
- ✅ Management command for offline generation
- ✅ Publishing to CurriculumCapsules
- ✅ Admin interface with status tracking
- ✅ Locally stored lessons for offline access

### Feature 3: Embedded Quizzes and Instant Feedback
- ✅ Multiple question types (multiple choice, true/false)
- ✅ Automatic grading
- ✅ Instant feedback with explanations
- ✅ Score tracking and pass/fail indicators

### Feature 4: Adaptive Learning Pathways
- ✅ Performance analysis based on quiz scores
- ✅ Personalized recommendations for revision or advancement
- ✅ Difficulty level tracking per subject
- ✅ Suggested next lessons based on progress
- ✅ Revision activity tracking with improvement scores

### Feature 5: Practical Learning Simulations
- ✅ Math visualizations (fractions, arrays, place value)
- ✅ Science experiments (water cycle, plant growth)
- ✅ Interactive diagrams (circuit builder)
- ✅ AI-generated hints for guided learning
- ✅ Progress tracking for simulation interactions

### Feature 6: Teacher and Administrator Dashboard
- ✅ Learner activity summaries
- ✅ Quiz outcome analytics
- ✅ Learning gap identification
- ✅ Performance visualization with charts
- ✅ User management view

### Feature 7: Learning Progress Tracking
- ✅ Local progress storage
- ✅ Lesson completion rates
- ✅ Quiz attempt history
- ✅ Time spent tracking
- ✅ Continuity across sessions

## Development Guidelines

### Adding Sample Data

```bash
# Load curriculum data
python manage.py populate_data

# Load simulation data
python manage.py populate_simulations
```

Or use the Django admin panel (http://localhost:8000/admin/) to add:
1. Subjects (e.g., Mathematics, English, Science)
2. Grades (e.g., Primary 1-8, Secondary 1-4)
3. Curriculum Capsules (Lessons with content)
4. Quizzes and Questions
5. Learning Simulations

### Management Commands

#### Generate Lessons from Textbook Content

Transform uploaded textbook chapters into interactive lessons:

```bash
# Generate all uploaded chapters
python manage.py generate_lessons --all

# Generate specific chapter
python manage.py generate_lessons --chapter-id 5

# Generate for specific subject and grade
python manage.py generate_lessons --subject "Mathematics" --grade "Primary 5"

# Use OpenAI API for higher quality (requires API key)
python manage.py generate_lessons --all --use-openai

# Auto-publish generated lessons
python manage.py generate_lessons --all --auto-publish

# Batch process with limit
python manage.py generate_lessons --all --max-chapters 10
```

**Options:**
- `--all`: Process all unprocessed chapters
- `--chapter-id ID`: Generate for specific chapter
- `--subject NAME`: Filter by subject
- `--grade NAME`: Filter by grade
- `--use-openai`: Use AI API (requires OPENROUTER_API_KEY or OPENAI_API_KEY)
- `--validate-only`: Validate without generating
- `--auto-publish`: Automatically publish generated lessons
- `--max-chapters N`: Limit number of chapters to process

### Extending the Application

- **New API endpoints**: Add views in `backend/api/views/` and update `backend/api/urls.py`
- **New models**: Define in `backend/api/models.py`, then run migrations
- **New serializers**: Create in `backend/api/serializers/`
- **Frontend pages**: Add HTML in `backend/jln_hub/templates/` and JavaScript modules in `backend/jln_hub/static/pages/`
- **UI components**: Create reusable components in `backend/jln_hub/static/components/`
- **Static assets**: Add CSS, images, and JS utilities in `backend/jln_hub/static/`

## Testing

Run Django tests:
```bash
python manage.py test
```

## Deployment

### Production Deployment (Railway)

The application is configured for Railway deployment with:
- `railway.json` for deployment configuration
- WhiteNoise for static file serving
- Environment-based settings for DEBUG, SECRET_KEY
- Health check endpoint at `/api/system/health/`

**Deploy to Railway:**
1. Connect your GitHub repository to Railway
2. Set environment variables:
   - `DEBUG=False`
   - `SECRET_KEY=<your-secret-key>`
   - `OPENROUTER_API_KEY=<optional-for-ai-features>`
3. Railway will automatically detect Django and deploy

### Local/Offline Deployment
1. Package the application with all dependencies
2. Use SQLite database (already configured)
3. Distribute as a standalone package
4. Consider using tools like PyInstaller for executable creation

### Other Cloud Deployment Options
- **Heroku**: Simple deployment with Django support
- **Render**: Free tier with automatic deploys
- **PythonAnywhere**: Free tier for development
- **AWS/Azure**: For production scale

### Offline-First Features
- SQLite database for local data storage
- Django templates cached by browser
- Static files served efficiently with WhiteNoise
- No external dependencies required once installed

## Contributing

This is an educational project for assignment purposes. Suggestions and improvements are welcome!

## License

Educational Project - 2026

## Contact

For questions or support regarding this project, please contact the development team.

---

**Recent Updates (February 2026)**:
- Restructured project as Django monorepo for simplified deployment
- Moved all frontend files into Django's template and static structure
- Integrated WhiteNoise for efficient static file serving
- Configured for one-click Railway deployment
- Maintained offline-first architecture with SQLite

---

**Note**: This application is designed for offline-first use in areas with limited connectivity. Internet connection is only required for initial setup and content updates.
