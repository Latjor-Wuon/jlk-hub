from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User
from django.db.models import Count, Avg

from .models import (
    Subject, Grade, CurriculumCapsule, Quiz, Question,
    LearnerProfile, LearningProgress, QuizAttempt
)
from .serializers import (
    SubjectSerializer, GradeSerializer, CurriculumCapsuleSerializer,
    CurriculumCapsuleListSerializer, QuizSerializer, QuestionSerializer,
    LearnerProfileSerializer, LearningProgressSerializer, QuizAttemptSerializer,
    QuizSubmissionSerializer
)


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for subjects"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]


class GradeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for grades"""
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [AllowAny]


class CurriculumCapsuleViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for curriculum capsules"""
    queryset = CurriculumCapsule.objects.filter(is_published=True)
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CurriculumCapsuleListSerializer
        return CurriculumCapsuleSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        subject_id = self.request.query_params.get('subject')
        grade_id = self.request.query_params.get('grade')
        
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if grade_id:
            queryset = queryset.filter(grade_id=grade_id)
        
        return queryset.order_by('order')
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured lessons"""
        featured = self.get_queryset()[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)


class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for quizzes"""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit quiz answers and get results"""
        quiz = self.get_object()
        serializer = QuizSubmissionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        answers = serializer.validated_data['answers']
        questions = quiz.questions.all()
        
        score = 0
        max_score = 0
        results = []
        
        for question in questions:
            max_score += question.points
            user_answer = answers.get(str(question.id), '')
            is_correct = user_answer.strip().lower() == question.correct_answer.strip().lower()
            
            if is_correct:
                score += question.points
            
            results.append({
                'question_id': question.id,
                'question_text': question.question_text,
                'user_answer': user_answer,
                'correct_answer': question.correct_answer,
                'is_correct': is_correct,
                'explanation': question.explanation,
                'points_earned': question.points if is_correct else 0
            })
        
        passed = (score / max_score * 100) >= quiz.passing_score if max_score > 0 else False
        
        # Save attempt if user is authenticated
        if request.user.is_authenticated:
            QuizAttempt.objects.create(
                learner=request.user,
                quiz=quiz,
                score=score,
                max_score=max_score,
                passed=passed,
                answers=answers
            )
        
        return Response({
            'score': score,
            'max_score': max_score,
            'percentage': round((score / max_score * 100), 2) if max_score > 0 else 0,
            'passed': passed,
            'passing_score': quiz.passing_score,
            'results': results
        })


class LearningProgressViewSet(viewsets.ModelViewSet):
    """API endpoint for learning progress tracking"""
    queryset = LearningProgress.objects.all()
    serializer_class = LearningProgressSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        learner_id = self.request.query_params.get('learner')
        
        if learner_id:
            queryset = queryset.filter(learner_id=learner_id)
        elif self.request.user.is_authenticated:
            queryset = queryset.filter(learner=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get learning progress summary"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        progress = self.get_queryset().filter(learner=request.user)
        total_capsules = progress.count()
        completed = progress.filter(is_completed=True).count()
        avg_completion = progress.aggregate(Avg('completion_percentage'))['completion_percentage__avg'] or 0
        
        return Response({
            'total_capsules_started': total_capsules,
            'completed_capsules': completed,
            'average_completion': round(avg_completion, 2),
            'in_progress': total_capsules - completed
        })


class QuizAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for quiz attempts"""
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if self.request.user.is_authenticated:
            queryset = queryset.filter(learner=self.request.user)
        
        return queryset


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
