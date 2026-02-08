from django.db import models
from django.contrib.auth.models import User


class Subject(models.Model):
    """Represents a subject like Mathematics, English, Science"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Grade(models.Model):
    """Represents grade levels (Primary 1-8, Secondary 1-4)"""
    name = models.CharField(max_length=50)
    level = models.IntegerField()
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['level']
    
    def __str__(self):
        return self.name


class CurriculumCapsule(models.Model):
    """Offline curriculum content packages"""
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='capsules')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='capsules')
    description = models.TextField()
    content = models.TextField()
    objectives = models.JSONField(default=list)
    order = models.IntegerField(default=0)
    estimated_duration = models.IntegerField(help_text="Estimated time in minutes")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['subject', 'grade', 'order']
    
    def __str__(self):
        return f"{self.subject.name} - {self.grade.name}: {self.title}"


class Quiz(models.Model):
    """Embedded quizzes for each lesson"""
    capsule = models.ForeignKey(CurriculumCapsule, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    passing_score = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Quiz: {self.title}"


class Question(models.Model):
    """Quiz questions with multiple choice answers"""
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    options = models.JSONField(default=list, help_text="List of answer options")
    correct_answer = models.CharField(max_length=200)
    explanation = models.TextField(blank=True)
    points = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['quiz', 'order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class LearnerProfile(models.Model):
    """Extended user profile for learners"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner_profile')
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    school_name = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.grade}"


class LearningProgress(models.Model):
    """Tracks learner progress through lessons"""
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    capsule = models.ForeignKey(CurriculumCapsule, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0, help_text="Time spent in minutes")
    last_accessed = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['learner', 'capsule']
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"{self.learner.username} - {self.capsule.title} ({self.completion_percentage}%)"


class QuizAttempt(models.Model):
    """Records of quiz attempts with scores"""
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    max_score = models.IntegerField()
    passed = models.BooleanField(default=False)
    answers = models.JSONField(default=dict)
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.learner.username} - {self.quiz.title}: {self.score}/{self.max_score}"


class LearnerDifficultyLevel(models.Model):
    """Tracks learner difficulty level per subject for adaptive pathways"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='difficulty_levels')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    current_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    average_score = models.FloatField(default=0.0)
    total_attempts = models.IntegerField(default=0)
    consecutive_passes = models.IntegerField(default=0)
    consecutive_fails = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['learner', 'subject']
    
    def __str__(self):
        return f"{self.learner.username} - {self.subject.name}: {self.current_level}"


class LearningRecommendation(models.Model):
    """Adaptive learning recommendations based on performance"""
    RECOMMENDATION_TYPES = [
        ('revision', 'Revision Needed'),
        ('practice', 'Additional Practice'),
        ('next_lesson', 'Ready for Next Lesson'),
        ('mastery', 'Concept Mastered'),
        ('simplified', 'Simplified Explanation'),
    ]
    
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    capsule = models.ForeignKey(CurriculumCapsule, on_delete=models.CASCADE)
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    reason = models.TextField()
    suggested_capsules = models.ManyToManyField(
        CurriculumCapsule, 
        related_name='recommended_for',
        blank=True
    )
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=5)  # 1=highest, 10=lowest
    created_at = models.DateTimeField(auto_now_add=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['priority', '-created_at']
    
    def __str__(self):
        return f"{self.learner.username}: {self.recommendation_type} - {self.capsule.title}"


class RevisionActivity(models.Model):
    """Tracks revision activities for adaptive learning"""
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revision_activities')
    capsule = models.ForeignKey(CurriculumCapsule, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)
    revision_count = models.IntegerField(default=0)
    last_revision = models.DateTimeField(auto_now=True)
    improvement_score = models.FloatField(default=0.0)  # Difference from first to latest attempt
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['learner', 'capsule']
    
    def __str__(self):
        return f"{self.learner.username} - {self.capsule.title} (Revisions: {self.revision_count})"


class LearningSimulation(models.Model):
    """Interactive simulations for science and math concepts"""
    SIMULATION_TYPES = [
        ('math_visualization', 'Math Visualization'),
        ('science_experiment', 'Science Experiment'),
        ('interactive_diagram', 'Interactive Diagram'),
        ('step_by_step', 'Step by Step Guide'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    simulation_type = models.CharField(max_length=30, choices=SIMULATION_TYPES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='simulations')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='simulations')
    related_capsule = models.ForeignKey(
        CurriculumCapsule, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='simulations'
    )
    # Configuration stored as JSON for flexibility
    config = models.JSONField(default=dict, help_text="Simulation configuration and parameters")
    instructions = models.TextField(blank=True)
    hints = models.JSONField(default=list, help_text="AI-generated hints for the simulation")
    learning_objectives = models.JSONField(default=list)
    difficulty_level = models.CharField(max_length=20, default='intermediate')
    estimated_time = models.IntegerField(default=10, help_text="Estimated time in minutes")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['subject', 'grade', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.simulation_type})"


class SimulationInteraction(models.Model):
    """Tracks learner interactions with simulations"""
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='simulation_interactions')
    simulation = models.ForeignKey(LearningSimulation, on_delete=models.CASCADE, related_name='interactions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.IntegerField(default=0, help_text="Time spent in seconds")
    interaction_data = models.JSONField(default=dict, help_text="Recorded user interactions")
    hints_used = models.IntegerField(default=0)
    completed_successfully = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.learner.username} - {self.simulation.title}"
