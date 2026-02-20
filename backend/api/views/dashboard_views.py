from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Sum, Q
from api.models import Subject, Grade, CurriculumCapsule, Quiz, LearningProgress, QuizAttempt


class DashboardViewSet(viewsets.ViewSet):
    """API endpoint for dashboard statistics"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get overall statistics"""
        stats = {
            'total_subjects': Subject.objects.count(),
            'total_grades': Grade.objects.count(),
            'total_capsules': CurriculumCapsule.objects.filter(is_published=True).count(),
            'total_quizzes': Quiz.objects.count(),
        }
        
        if request.user.is_authenticated:
            user_stats = {
                'capsules_started': LearningProgress.objects.filter(learner=request.user).count(),
                'capsules_completed': LearningProgress.objects.filter(
                    learner=request.user, is_completed=True
                ).count(),
                'quizzes_taken': QuizAttempt.objects.filter(learner=request.user).count(),
                'quizzes_passed': QuizAttempt.objects.filter(
                    learner=request.user, passed=True
                ).count(),
            }
            stats.update(user_stats)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def admin_stats(self, request):
        """Get admin dashboard statistics"""
        # Basic counts
        stats = {
            'total_users': User.objects.count(),
            'total_students': User.objects.filter(is_staff=False).count(),
            'total_admins': User.objects.filter(is_staff=True).count(),
            'total_subjects': Subject.objects.count(),
            'total_grades': Grade.objects.count(),
            'total_capsules': CurriculumCapsule.objects.count(),
            'published_capsules': CurriculumCapsule.objects.filter(is_published=True).count(),
            'total_quizzes': Quiz.objects.count(),
            'total_quiz_attempts': QuizAttempt.objects.count(),
            'total_learning_progress': LearningProgress.objects.count(),
        }
        
        # Engagement stats
        stats['completed_capsules'] = LearningProgress.objects.filter(is_completed=True).count()
        stats['average_completion_rate'] = LearningProgress.objects.aggregate(
            avg_completion=Avg('completion_percentage')
        )['avg_completion'] or 0
        
        # Quiz performance
        quiz_stats = QuizAttempt.objects.aggregate(
            avg_score=Avg('score'),
            total_attempts=Count('id'),
            passed_attempts=Count('id', filter=Q(passed=True))
        )
        stats['average_quiz_score'] = quiz_stats['avg_score'] or 0
        stats['quiz_pass_rate'] = (
            (quiz_stats['passed_attempts'] / quiz_stats['total_attempts'] * 100) 
            if quiz_stats['total_attempts'] > 0 else 0
        )
        
        # Subject distribution
        subject_distribution = Subject.objects.annotate(
            capsule_count=Count('capsules')
        ).values('name', 'capsule_count')
        stats['subject_distribution'] = list(subject_distribution)
        
        # Grade distribution
        grade_distribution = Grade.objects.annotate(
            capsule_count=Count('capsules')
        ).values('name', 'capsule_count').order_by('level')
        stats['grade_distribution'] = list(grade_distribution)
        
        # Recent activity
        recent_attempts = QuizAttempt.objects.select_related(
            'learner', 'quiz'
        ).order_by('-completed_at')[:10].values(
            'learner__username', 'quiz__title', 'score', 'max_score', 'completed_at', 'passed'
        )
        stats['recent_quiz_attempts'] = list(recent_attempts)
        
        # User progress summary
        user_progress = User.objects.filter(is_staff=False).annotate(
            capsules_completed=Count('progress', filter=Q(progress__is_completed=True)),
            total_attempts=Count('quiz_attempts'),
            avg_score=Avg('quiz_attempts__score')
        ).values('id', 'username', 'email', 'date_joined', 'capsules_completed', 'total_attempts', 'avg_score')
        stats['user_progress'] = list(user_progress)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def users(self, request):
        """Get all users with their statistics"""
        users = User.objects.all().annotate(
            capsules_started=Count('progress'),
            capsules_completed=Count('progress', filter=Q(progress__is_completed=True)),
            quizzes_taken=Count('quiz_attempts'),
            quizzes_passed=Count('quiz_attempts', filter=Q(quiz_attempts__passed=True)),
            avg_score=Avg('quiz_attempts__score'),
            total_time_spent=Sum('progress__time_spent')
        ).values(
            'id', 'username', 'email', 'first_name', 'last_name', 
            'is_staff', 'is_active', 'date_joined', 'last_login',
            'capsules_started', 'capsules_completed', 
            'quizzes_taken', 'quizzes_passed', 'avg_score', 'total_time_spent'
        ).order_by('-date_joined')
        
        return Response({
            'count': User.objects.count(),
            'users': list(users)
        })
