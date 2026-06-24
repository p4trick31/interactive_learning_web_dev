from django.db import models
from django.contrib.auth.models import User



class StudentProfile(models.Model):

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    YEAR_LEVEL_CHOICES = [
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
        ('5th Year', '5th Year'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )

    student_id = models.CharField(
        max_length=30,
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    college = models.CharField(
        max_length=100
    )

    course = models.CharField(
        max_length=100
    )

    year_level = models.CharField(
        max_length=20,
        choices=YEAR_LEVEL_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"


# =========================
# QUIZ MODEL (HTML / CSS / JS)

# =========================
class Quiz(models.Model):

    SUBJECT_CHOICES = [
        ('HTML', 'HTML'),
        ('CSS', 'CSS'),
        ('JavaScript', 'JavaScript'),
    ]

    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.subject})"


# =========================
# QUESTION MODEL
# =========================
class Question(models.Model):   

    QUESTION_TYPE = [
        ('MCQ', 'Multiple Choice'),
        ('SYNTAX', 'Syntax Correction'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()

    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE)

    code_snippet = models.TextField(blank=True, null=True)  
    # used for HTML/CSS/JS code correction questions

    correct_answer = models.TextField(blank=True, null=True)
    explanation = models.TextField(
        blank=True,
        null=True,
        help_text="Explanation shown after answering the question."
    )

    def __str__(self):
        return self.question_text


# =========================
# MCQ CHOICES MODEL
# =========================
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")

    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


# =========================
# STUDENT ATTEMPT MODEL
# =========================
class StudentAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    score = models.FloatField(default=0)
    completed = models.BooleanField(default=False)

    correct_answers = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)

    xp_earned = models.IntegerField(default=0) 

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"


# =========================
# ANSWER TRACKING MODEL
# =========================
class StudentAnswer(models.Model):
    attempt = models.ForeignKey(StudentAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)

    text_answer = models.TextField(blank=True, null=True)

    is_correct = models.BooleanField(default=False)

    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.question.question_text}"
    
class StudentProgress(models.Model):
    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="progress"
    )

    total_xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    completed_quizzes = models.IntegerField(default=0)

    total_score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.student.username} Progress"
    
class Badge(models.Model):
    name = models.CharField(max_length=100)

    description = models.TextField()

    image = models.ImageField(
        upload_to='badges/',
        blank=True,
        null=True
    )

    required_xp = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class StudentBadge(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE
    )

    earned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.badge.name}"
    
class HistoryResult(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quiz_history"
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True)

    quiz_title = models.CharField(max_length=255)

    correct = models.IntegerField()
    total = models.IntegerField()

    score_percent = models.FloatField()

    xp_earned = models.IntegerField()

    total_xp_after = models.IntegerField()

    level = models.IntegerField()

    difficulty = models.CharField(max_length=50)

    passed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz_title}"

class HistoryBadge(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="badge_history"
    )

    badge_name = models.CharField(max_length=100)

    description = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to='badge_history/', null=True, blank=True)

    earned_at = models.DateTimeField(auto_now_add=True)

    quiz = models.ForeignKey(
        "Quiz",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.student.username} - {self.badge_name}"
    
class LearningModule(models.Model):
    SUBJECT_CHOICES = [
        ('HTML', 'HTML'),
        ('CSS', 'CSS'),
        ('JS', 'JavaScript'),
    ]

    subject = models.CharField(
        max_length=10,
        choices=SUBJECT_CHOICES,
        default='HTML'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
class Lesson(models.Model):
    module = models.ForeignKey(
        LearningModule,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    code_snippet = models.TextField(blank=True)

    example_output = models.TextField(blank=True)

    practice_activity = models.TextField(
        blank=True,
        help_text="Small task for the learner."
    )

    documentation_link = models.URLField(blank=True)

    def __str__(self):
        return self.title
    
class QuizFeedback(models.Model):
    history = models.ForeignKey(
        HistoryResult,
        on_delete=models.CASCADE,
        related_name="feedbacks"
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="given_feedback"
    )

    message = models.TextField()
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("history", "teacher")

    def __str__(self):
        return f"{self.teacher.username} - {self.history.quiz_title}"  
    
class TeacherProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=20,
        default="teacher"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Teacher"