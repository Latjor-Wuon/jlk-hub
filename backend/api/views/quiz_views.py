from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from api.models import Quiz, QuizAttempt
from api.serializers import QuizSerializer, QuizSubmissionSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session auth without CSRF enforcement for quiz submissions"""
    def enforce_csrf(self, request):
        return  # Skip CSRF check


@method_decorator(csrf_exempt, name='dispatch')
class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for quizzes"""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication, CsrfExemptSessionAuthentication]
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit quiz answers and get results"""
        quiz = self.get_object()
        
        # Debug logging
        print(f"Quiz submission - User: {request.user}, Authenticated: {request.user.is_authenticated}")
        
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
            attempt = QuizAttempt.objects.create(
                learner=request.user,
                quiz=quiz,
                score=score,
                max_score=max_score,
                passed=passed,
                answers=answers
            )
            print(f"Quiz attempt saved: ID={attempt.id}, User={request.user.username}, Score={score}/{max_score}, Passed={passed}")
        else:
            print("Quiz attempt NOT saved - user not authenticated")
        
        return Response({
            'score': score,
            'max_score': max_score,
            'percentage': round((score / max_score * 100), 2) if max_score > 0 else 0,
            'passed': passed,
            'passing_score': quiz.passing_score,
            'results': results
        })
