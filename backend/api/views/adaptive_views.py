"""
Adaptive Learning Pathway Views

This module provides views for the adaptive learning system that analyzes
learner quiz performance and adjusts learning flow accordingly.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Avg, Count, Q
from django.utils import timezone
from api.models import (
    LearnerDifficultyLevel, LearningRecommendation, RevisionActivity,
    QuizAttempt, LearningProgress, CurriculumCapsule, Subject, Grade
)
from api.serializers.adaptive_serializers import (
    LearnerDifficultyLevelSerializer, LearningRecommendationSerializer,
    RevisionActivitySerializer
)


class AdaptiveLearningViewSet(viewsets.ViewSet):
    """
    API endpoint for adaptive learning pathways.
    Analyzes learner performance and provides personalized recommendations.
    """
    permission_classes = [AllowAny]
    
    def _calculate_difficulty_adjustment(self, learner, subject):
        """
        Calculate if learner should move up/down difficulty levels
        based on recent quiz performance.
        """
        recent_attempts = QuizAttempt.objects.filter(
            learner=learner,
            quiz__capsule__subject=subject
        ).order_by('-completed_at')[:5]
        
        if not recent_attempts.exists():
            return 'beginner', 0, 0
        
        scores = [(a.score / a.max_score * 100) if a.max_score > 0 else 0 
                  for a in recent_attempts]
        avg_score = sum(scores) / len(scores)
        
        consecutive_passes = 0
        consecutive_fails = 0
        
        for attempt in recent_attempts:
            if attempt.passed:
                if consecutive_fails == 0:
                    consecutive_passes += 1
                else:
                    break
            else:
                if consecutive_passes == 0:
                    consecutive_fails += 1
                else:
                    break
        
        # Determine level
        if avg_score >= 85 and consecutive_passes >= 3:
            level = 'advanced'
        elif avg_score >= 60 and consecutive_passes >= 2:
            level = 'intermediate'
        elif avg_score < 50 or consecutive_fails >= 2:
            level = 'beginner'
        else:
            level = 'intermediate'
        
        return level, consecutive_passes, consecutive_fails
    
    def _generate_recommendations(self, learner, capsule, quiz_attempt):
        """
        Generate learning recommendations based on quiz performance.
        """
        recommendations = []
        score_percentage = (quiz_attempt.score / quiz_attempt.max_score * 100) if quiz_attempt.max_score > 0 else 0
        
        if score_percentage < 50:
            # Needs revision
            rec = LearningRecommendation.objects.create(
                learner=learner,
                capsule=capsule,
                recommendation_type='revision',
                reason=f'Your score of {score_percentage:.0f}% suggests you need to review this topic. '
                       f'Focus on the concepts you found challenging.',
                priority=1
            )
            
            # Find prerequisite or simpler capsules
            simpler_capsules = CurriculumCapsule.objects.filter(
                subject=capsule.subject,
                grade__level__lt=capsule.grade.level,
                is_published=True
            ).order_by('-grade__level')[:3]
            rec.suggested_capsules.set(simpler_capsules)
            recommendations.append(rec)
            
        elif score_percentage < 70:
            # Additional practice recommended
            rec = LearningRecommendation.objects.create(
                learner=learner,
                capsule=capsule,
                recommendation_type='practice',
                reason=f'Your score of {score_percentage:.0f}% shows good progress! '
                       f'Additional practice will help reinforce these concepts.',
                priority=3
            )
            
            # Find similar capsules for practice
            similar_capsules = CurriculumCapsule.objects.filter(
                subject=capsule.subject,
                grade=capsule.grade,
                is_published=True
            ).exclude(id=capsule.id)[:2]
            rec.suggested_capsules.set(similar_capsules)
            recommendations.append(rec)
            
        elif score_percentage >= 85:
            # Ready for next lesson
            rec = LearningRecommendation.objects.create(
                learner=learner,
                capsule=capsule,
                recommendation_type='next_lesson',
                reason=f'Excellent! Your score of {score_percentage:.0f}% shows mastery. '
                       f'You\'re ready for more challenging content.',
                priority=5
            )
            
            # Find next capsules
            next_capsules = CurriculumCapsule.objects.filter(
                subject=capsule.subject,
                order__gt=capsule.order,
                is_published=True
            ).order_by('order')[:2]
            
            if not next_capsules.exists():
                # Try next grade level
                next_capsules = CurriculumCapsule.objects.filter(
                    subject=capsule.subject,
                    grade__level__gt=capsule.grade.level,
                    is_published=True
                ).order_by('grade__level', 'order')[:2]
            
            rec.suggested_capsules.set(next_capsules)
            recommendations.append(rec)
            
            # May have achieved mastery
            if score_percentage >= 95:
                mastery_rec = LearningRecommendation.objects.create(
                    learner=learner,
                    capsule=capsule,
                    recommendation_type='mastery',
                    reason='Outstanding! You have mastered this concept!',
                    priority=10
                )
                recommendations.append(mastery_rec)
        else:
            # Between 70-85, ready for next
            rec = LearningRecommendation.objects.create(
                learner=learner,
                capsule=capsule,
                recommendation_type='next_lesson',
                reason=f'Good job! Your score of {score_percentage:.0f}% shows solid understanding.',
                priority=4
            )
            next_capsules = CurriculumCapsule.objects.filter(
                subject=capsule.subject,
                order__gt=capsule.order,
                is_published=True
            ).order_by('order')[:2]
            rec.suggested_capsules.set(next_capsules)
            recommendations.append(rec)
        
        return recommendations
    
    @action(detail=False, methods=['get'])
    def pathway(self, request):
        """
        Get personalized adaptive learning pathway for the current user.
        Returns recommendations, next lessons, and areas needing revision.
        """
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required for personalized pathway'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        learner = request.user
        subject_id = request.query_params.get('subject')
        
        # Get active recommendations
        recommendations = LearningRecommendation.objects.filter(
            learner=learner,
            is_active=True
        ).select_related('capsule', 'capsule__subject')
        
        if subject_id:
            recommendations = recommendations.filter(capsule__subject_id=subject_id)
        
        # Get performance summary
        quiz_stats = QuizAttempt.objects.filter(learner=learner)
        if subject_id:
            quiz_stats = quiz_stats.filter(quiz__capsule__subject_id=subject_id)
        
        quiz_summary = quiz_stats.aggregate(
            total_attempts=Count('id'),
            passed_attempts=Count('id', filter=Q(passed=True)),
            avg_score=Avg('score'),
            avg_max_score=Avg('max_score')
        )
        
        # Calculate pass rate
        pass_rate = 0
        avg_percentage = 0
        if quiz_summary['total_attempts'] and quiz_summary['total_attempts'] > 0:
            pass_rate = (quiz_summary['passed_attempts'] / quiz_summary['total_attempts']) * 100
            if quiz_summary['avg_max_score'] and quiz_summary['avg_max_score'] > 0:
                avg_percentage = (quiz_summary['avg_score'] / quiz_summary['avg_max_score']) * 100
        
        # Get difficulty levels per subject
        difficulty_levels = LearnerDifficultyLevel.objects.filter(learner=learner)
        if subject_id:
            difficulty_levels = difficulty_levels.filter(subject_id=subject_id)
        
        # Identify strengths and weaknesses
        subject_performance = QuizAttempt.objects.filter(
            learner=learner
        ).values(
            'quiz__capsule__subject__name'
        ).annotate(
            avg_score=Avg('score'),
            avg_max=Avg('max_score'),
            attempts=Count('id')
        )
        
        strengths = []
        weaknesses = []
        for perf in subject_performance:
            if perf['avg_max'] and perf['avg_max'] > 0:
                percentage = (perf['avg_score'] / perf['avg_max']) * 100
                subject_name = perf['quiz__capsule__subject__name']
                if percentage >= 75:
                    strengths.append({
                        'subject': subject_name,
                        'score': round(percentage, 1)
                    })
                elif percentage < 60:
                    weaknesses.append({
                        'subject': subject_name,
                        'score': round(percentage, 1)
                    })
        
        # Get suggested next lessons
        completed_capsule_ids = LearningProgress.objects.filter(
            learner=learner,
            is_completed=True
        ).values_list('capsule_id', flat=True)
        
        next_lessons = CurriculumCapsule.objects.filter(
            is_published=True
        ).exclude(
            id__in=completed_capsule_ids
        ).order_by('grade__level', 'subject', 'order')[:5]
        
        # Get capsules needing revision
        revision_needed_recs = recommendations.filter(
            recommendation_type__in=['revision', 'simplified']
        )
        
        return Response({
            'current_performance': {
                'total_quizzes_taken': quiz_summary['total_attempts'] or 0,
                'quizzes_passed': quiz_summary['passed_attempts'] or 0,
                'pass_rate': round(pass_rate, 1),
                'average_score': round(avg_percentage, 1)
            },
            'difficulty_levels': LearnerDifficultyLevelSerializer(difficulty_levels, many=True).data,
            'recommendations': LearningRecommendationSerializer(recommendations[:10], many=True).data,
            'next_lessons': [
                {
                    'id': c.id,
                    'title': c.title,
                    'subject': c.subject.name,
                    'grade': c.grade.name
                } for c in next_lessons
            ],
            'revision_needed': LearningRecommendationSerializer(revision_needed_recs, many=True).data,
            'strengths': strengths,
            'weaknesses': weaknesses
        })
    
    @action(detail=False, methods=['post'])
    def analyze_quiz(self, request):
        """
        Analyze a quiz attempt and generate recommendations.
        Called after quiz submission to update adaptive pathway.
        """
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        quiz_attempt_id = request.data.get('quiz_attempt_id')
        
        if not quiz_attempt_id:
            return Response(
                {'detail': 'quiz_attempt_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quiz_attempt = QuizAttempt.objects.select_related(
                'quiz', 'quiz__capsule', 'quiz__capsule__subject'
            ).get(id=quiz_attempt_id, learner=request.user)
        except QuizAttempt.DoesNotExist:
            return Response(
                {'detail': 'Quiz attempt not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        capsule = quiz_attempt.quiz.capsule
        subject = capsule.subject
        
        # Update difficulty level
        level, passes, fails = self._calculate_difficulty_adjustment(request.user, subject)
        
        difficulty_obj, created = LearnerDifficultyLevel.objects.get_or_create(
            learner=request.user,
            subject=subject,
            defaults={'current_level': level}
        )
        
        # Update stats
        score_pct = (quiz_attempt.score / quiz_attempt.max_score * 100) if quiz_attempt.max_score > 0 else 0
        total = difficulty_obj.total_attempts + 1
        difficulty_obj.average_score = (
            (difficulty_obj.average_score * difficulty_obj.total_attempts + score_pct) / total
        )
        difficulty_obj.total_attempts = total
        difficulty_obj.consecutive_passes = passes
        difficulty_obj.consecutive_fails = fails
        difficulty_obj.current_level = level
        difficulty_obj.save()
        
        # Deactivate old recommendations for this capsule
        LearningRecommendation.objects.filter(
            learner=request.user,
            capsule=capsule,
            is_active=True
        ).update(is_active=False)
        
        # Generate new recommendations
        recommendations = self._generate_recommendations(request.user, capsule, quiz_attempt)
        
        # Update revision activity
        revision, created = RevisionActivity.objects.get_or_create(
            learner=request.user,
            capsule=capsule,
            defaults={'quiz': quiz_attempt.quiz}
        )
        
        if not created:
            revision.revision_count += 1
            # Calculate improvement from first attempt
            first_attempt = QuizAttempt.objects.filter(
                learner=request.user,
                quiz__capsule=capsule
            ).order_by('completed_at').first()
            
            if first_attempt and first_attempt.max_score > 0:
                first_score = (first_attempt.score / first_attempt.max_score) * 100
                current_score = (quiz_attempt.score / quiz_attempt.max_score) * 100 if quiz_attempt.max_score > 0 else 0
                revision.improvement_score = current_score - first_score
            
            revision.save()
        
        return Response({
            'difficulty_level': LearnerDifficultyLevelSerializer(difficulty_obj).data,
            'recommendations': LearningRecommendationSerializer(recommendations, many=True).data,
            'revision_activity': RevisionActivitySerializer(revision).data
        })
    
    @action(detail=False, methods=['post'])
    def dismiss_recommendation(self, request):
        """Dismiss a recommendation"""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        rec_id = request.data.get('recommendation_id')
        
        try:
            rec = LearningRecommendation.objects.get(
                id=rec_id,
                learner=request.user
            )
            rec.is_active = False
            rec.dismissed_at = timezone.now()
            rec.save()
            return Response({'status': 'dismissed'})
        except LearningRecommendation.DoesNotExist:
            return Response(
                {'detail': 'Recommendation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def revision_history(self, request):
        """Get revision history for the current user"""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        revisions = RevisionActivity.objects.filter(
            learner=request.user
        ).select_related('capsule', 'quiz')
        
        subject_id = request.query_params.get('subject')
        if subject_id:
            revisions = revisions.filter(capsule__subject_id=subject_id)
        
        return Response(RevisionActivitySerializer(revisions, many=True).data)
