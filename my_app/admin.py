from django.contrib import admin
from .models import Quiz, Question, Choice, TeacherProfile, Lesson, QuizFeedback, LearningModule, StudentAttempt, StudentAnswer,HistoryResult, StudentProfile, HistoryBadge, StudentProgress, StudentBadge, Badge


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'difficulty')


class StudentAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'completed')


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(StudentAttempt, StudentAttemptAdmin)
admin.site.register(StudentAnswer)
admin.site.register(StudentProgress)
admin.site.register(Badge)
admin.site.register(StudentBadge)
admin.site.register(HistoryResult)
admin.site.register(HistoryBadge)
admin.site.register(StudentProfile)
admin.site.register(LearningModule)
admin.site.register(Lesson)
admin.site.register(QuizFeedback)
admin.site.register(TeacherProfile)