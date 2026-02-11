from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    SubjectViewSet, GradeViewSet, CurriculumCapsuleViewSet,
    QuizViewSet, LearningProgressViewSet, QuizAttemptViewSet,
    DashboardViewSet, AdaptiveLearningViewSet, SimulationViewSet,
    SimulationInteractionViewSet, TextbookChapterViewSet,
    GeneratedLessonViewSet, LessonSectionViewSet, GeneratedQuestionViewSet,
    ai_integration_status, system_health
)
from api.views.auth_views import (
    RegisterView, login_view, logout_view, current_user_view, UserProfileView, csrf_token_view
)

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'capsules', CurriculumCapsuleViewSet, basename='capsule')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'progress', LearningProgressViewSet, basename='progress')
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'adaptive', AdaptiveLearningViewSet, basename='adaptive')
router.register(r'simulations', SimulationViewSet, basename='simulation')
router.register(r'simulation-interactions', SimulationInteractionViewSet, basename='simulation-interaction')

# AI-Assisted Lesson Generation endpoints
router.register(r'chapters', TextbookChapterViewSet, basename='chapter')
router.register(r'generated-lessons', GeneratedLessonViewSet, basename='generated-lesson')
router.register(r'lesson-sections', LessonSectionViewSet, basename='lesson-section')
router.register(r'generated-questions', GeneratedQuestionViewSet, basename='generated-question')

urlpatterns = [
    path('', include(router.urls)),
    # Authentication endpoints
    path('auth/csrf/', csrf_token_view, name='csrf-token'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/user/', current_user_view, name='current-user'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
    # System status endpoints
    path('system/health/', system_health, name='system-health'),
    path('system/ai-status/', ai_integration_status, name='ai-integration-status'),
]
