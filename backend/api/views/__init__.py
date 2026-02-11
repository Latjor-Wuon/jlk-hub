# Views package initialization
from .subject_views import SubjectViewSet
from .grade_views import GradeViewSet
from .capsule_views import CurriculumCapsuleViewSet
from .quiz_views import QuizViewSet
from .progress_views import LearningProgressViewSet, QuizAttemptViewSet
from .dashboard_views import DashboardViewSet
from .adaptive_views import AdaptiveLearningViewSet
from .simulation_views import SimulationViewSet, SimulationInteractionViewSet
from .lesson_generation_views import (
    TextbookChapterViewSet,
    GeneratedLessonViewSet,
    LessonSectionViewSet,
    GeneratedQuestionViewSet
)
from .system_views import ai_integration_status, system_health

__all__ = [
    'SubjectViewSet',
    'GradeViewSet',
    'CurriculumCapsuleViewSet',
    'QuizViewSet',
    'LearningProgressViewSet',
    'QuizAttemptViewSet',
    'DashboardViewSet',
    'AdaptiveLearningViewSet',
    'SimulationViewSet',
    'SimulationInteractionViewSet',
    'TextbookChapterViewSet',
    'GeneratedLessonViewSet',
    'LessonSectionViewSet',
    'GeneratedQuestionViewSet',
    'ai_integration_status',
    'system_health',
]
