from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    SubjectViewSet, GradeViewSet, CurriculumCapsuleViewSet,
    QuizViewSet, LearningProgressViewSet, QuizAttemptViewSet,
    DashboardViewSet
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

urlpatterns = [
    path('', include(router.urls)),
    # Authentication endpoints
    path('auth/csrf/', csrf_token_view, name='csrf-token'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/user/', current_user_view, name='current-user'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
]
