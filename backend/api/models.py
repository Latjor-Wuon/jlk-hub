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
