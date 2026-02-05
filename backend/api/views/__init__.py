# Views package initialization
from .subject_views import SubjectViewSet
from .grade_views import GradeViewSet
from .capsule_views import CurriculumCapsuleViewSet
from .quiz_views import QuizViewSet
from .progress_views import LearningProgressViewSet, QuizAttemptViewSet
from .dashboard_views import DashboardViewSet

__all__ = [
    'SubjectViewSet',
    'GradeViewSet',
    'CurriculumCapsuleViewSet',
    'QuizViewSet',
    'LearningProgressViewSet',
    'QuizAttemptViewSet',
    'DashboardViewSet',
]
