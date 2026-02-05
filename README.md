# Jinubia Learning Nexus Hub (JLN Hub)

An offline-first educational application designed to deliver South Sudan's national curriculum to primary and secondary school learners, regardless of internet availability or infrastructure constraints.

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
- Django 5.0.1
- Django REST Framework 3.14.0
- SQLite (offline-first database)
- Django CORS Headers

### Frontend
- Vanilla JavaScript (ES6+)
- HTML5
- CSS3 with CSS Grid & Flexbox
- Responsive Design

## Project Structure

```
JLN Hub/
├── backend/
│   ├── jln_hub/              # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── api/                  # REST API application
│   │   ├── models.py         # Database models
│   │   ├── serializers.py    # API serializers
│   │   ├── views.py          # API endpoints
│   │   ├── urls.py           # API routing
│   │   └── admin.py          # Admin interface
│   ├── manage.py
│   └── requirements.txt
└── frontend/
    ├── index.html            # Main HTML file
    └── src/
        ├── app.js            # Application logic
        └── styles.css        # Styling
```

## Setup Instructions

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
   python manage.py shell
   ```
   Then run the sample data script (to be created).

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Frontend: http://localhost:8000/
   - API: http://localhost:8000/api/
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

### Dashboard
- `GET /api/dashboard/stats/` - Get application statistics

## Features Implementation Status

- ✅ Basic project structure
- ✅ Database models for curriculum content
- ✅ REST API endpoints
- ✅ Frontend UI with responsive design
- ✅ Lesson viewing functionality
- ✅ Quiz system with instant feedback
- ✅ User authentication

## Development Guidelines

### Adding Sample Data

Use the Django admin panel (http://localhost:8000/admin/) to add:
1. Subjects (e.g., Mathematics, English, Science)
2. Grades (e.g., Primary 1-8, Secondary 1-4)
3. Curriculum Capsules (Lessons with content)
4. Quizzes and Questions

### Extending the Application

- **New API endpoints**: Add to `backend/api/views.py` and `backend/api/urls.py`
- **New models**: Define in `backend/api/models.py`, then run migrations
- **Frontend features**: Update `frontend/src/app.js` and `frontend/src/styles.css`

## Testing

Run Django tests:
```bash
python manage.py test
```

## Deployment Plan

### Local/Offline Deployment
1. Package the application with all dependencies
2. Use SQLite database (already configured)
3. Distribute as a standalone package
4. Consider using tools like PyInstaller for executable creation

### Cloud Deployment Options
- **Heroku**: Simple deployment with Django support
- **Railway**: Modern platform with easy setup
- **PythonAnywhere**: Free tier for development
- **AWS/Azure**: For production scale

### Offline-First Features (Coming Soon)
- Service Workers for caching
- IndexedDB for local data storage
- Background sync for progress updates
- Installable as Progressive Web App (PWA)

## Contributing

This is an educational project for assignment purposes. Suggestions and improvements are welcome!

## License

Educational Project - 2026

## Contact

For questions or support regarding this project, please contact the development team.

---

**Note**: This application is designed for offline-first use in areas with limited connectivity. Internet connection is only required for initial setup and content updates.
