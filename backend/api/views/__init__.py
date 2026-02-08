# Views package initialization
from .subject_views import SubjectViewSet
from .grade_views import GradeViewSet
from .capsule_views import CurriculumCapsuleViewSet
from .quiz_views import QuizViewSet
from .progress_views import LearningProgressViewSet, QuizAttemptViewSet
from .dashboard_views import DashboardViewSet
from .adaptive_views import AdaptiveLearningViewSet
from .simulation_views import SimulationViewSet, SimulationInteractionViewSet

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
]
