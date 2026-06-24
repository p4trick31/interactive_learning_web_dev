from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import re
from django.urls import reverse
from django.db.models import Count, Avg,  Sum, Max
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localtime
from .models import (
    Quiz,
    Question,
    Choice,
    StudentAttempt,
    StudentAnswer,
    StudentProgress,
    Badge,
    StudentBadge,
    HistoryResult,
    HistoryBadge,
    StudentProfile,
    LearningModule,
    QuizFeedback,
    TeacherProfile
)
from django.http import JsonResponse
import json


# HOME PAGE
def home(request):
    return render(request, 'home.html')


@login_required
def update_profile(request):

    profile = StudentProfile.objects.get(user=request.user)

    if request.method == "POST":

        # USER MODEL
        request.user.email = request.POST.get("email")
        request.user.save()

        # PROFILE MODEL
        profile.student_id = request.POST.get("student_id")
        profile.first_name = request.POST.get("first_name")
        profile.last_name = request.POST.get("last_name")
        profile.gender = request.POST.get("gender")
        profile.college = request.POST.get("college")
        profile.course = request.POST.get("course")
        profile.year_level = request.POST.get("year_level")

        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile") # change if your url name differs

    return render(request, "student/profile_page.html", {
        "profile": profile
    })

@login_required
def student_dashboard(request):

    profile_missing = False

    try:
        profile = request.user.student_profile

        # check required fields
        if not all([
            profile.student_id,
            profile.first_name,
            profile.last_name,
            profile.gender,
            profile.college,
            profile.course,
            profile.year_level
        ]):
            profile_missing = True

    except StudentProfile.DoesNotExist:
        profile_missing = True

    badges = Badge.objects.all()
    user_badges = Badge.objects.filter(
    studentbadge__student=request.user,
).distinct()

    html_easy_done = HistoryResult.objects.filter(
        student=request.user,
        quiz_id__in=Quiz.objects.filter(subject="HTML", difficulty="Easy")
        .values_list("id", flat=True),
        
    ).exists()

    html_medium_done = HistoryResult.objects.filter(
        student=request.user,
        quiz_id__in=Quiz.objects.filter(subject="HTML", difficulty="Medium")
        .values_list("id", flat=True),
    
    ).exists()

    html_hard_done = HistoryResult.objects.filter(
        student=request.user,
        quiz_id__in=Quiz.objects.filter(subject="HTML", difficulty="Hard")
        .values_list("id", flat=True),
      
    ).exists()

    # STATUS LOGIC
    if html_hard_done:
        html_status = "completed"
    elif html_medium_done or html_easy_done:
        html_status = "continue"
    else:
        html_status = "start"
    
    

    css_easy_done = HistoryResult.objects.filter(
        student=request.user,
        quiz_id__in=Quiz.objects.filter(subject="CSS", difficulty="Easy")
        .values_list("id", flat=True),
    ).exists()

    css_medium_done = HistoryResult.objects.filter(
        student=request.user,
        quiz_id__in=Quiz.objects.filter(subject="CSS", difficulty="Medium")
        .values_list("id", flat=True),
 
    ).exists()

    css_hard_done = HistoryResult.objects.filter(
        student=request.user,
        quiz_id__in=Quiz.objects.filter(subject="CSS", difficulty="Hard")
        .values_list("id", flat=True),
        
    ).exists()
    if css_hard_done:
        css_status = "completed"
    elif css_medium_done or css_easy_done:
        css_status = "continue"
    else:
        css_status = "start"

    js_easy_done = HistoryResult.objects.filter(
        student=request.user,
        quiz_id__in=Quiz.objects.filter(subject="JavaScript", difficulty="Easy")
        .values_list("id", flat=True),
    ).exists()

    js_medium_done = HistoryResult.objects.filter(
        student=request.user,
        quiz_id__in=Quiz.objects.filter(subject="JavaScript", difficulty="Medium")
        .values_list("id", flat=True),
 
    ).exists()

    js_hard_done = HistoryResult.objects.filter(
        student=request.user,
        quiz_id__in=Quiz.objects.filter(subject="JavaScript", difficulty="Hard")
        .values_list("id", flat=True),
        
    ).exists()
    if js_hard_done:
        js_status = "completed"
    elif js_medium_done or js_easy_done:
        js_status = "continue"
    else:
        js_status = "start"

    return render(
        request,
        "student/student_dashboard.html",
        {
            "badges": badges,
            "user_badges": user_badges,

            "html_easy_done": html_easy_done,
            "html_medium_done": html_medium_done,
            "html_hard_done": html_hard_done,
            "html_status": html_status,

            "css_easy_done": css_easy_done,
            "css_medium_done": css_medium_done,
            "css_hard_done": css_hard_done,
            "css_status": css_status,

            "js_easy_done": js_easy_done,
            "js_medium_done": js_medium_done,
            "js_hard_done": js_hard_done,
            "js_status": js_status,
            "profile_missing": profile_missing,
        }
    )

def signup_view(request):
    if request.method == "POST":

        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        role = request.POST.get('role', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        errors = {}
        success = {}

        # =========================
        # VALIDATION
        # =========================
        if not role:
            errors["role_error"] = "Please select a role (Student or Teacher)"

        if role == "teacher":

            if not first_name:
                errors["first_name_error"] = "First name is required"

            if not last_name:
                errors["last_name_error"] = "Last name is required"

        # Username
        if len(username) < 5:
            errors["username_error"] = "Username must be at least 5 characters"

        elif " " in username:
            errors["username_error"] = "Username must not contain spaces"

        elif User.objects.filter(username=username).exists():
            errors["username_error"] = "Username is already taken"

        else:
            success["username_success"] = True

        # Email
        if "@gmail.com" not in email:
            errors["email_error"] = "Email must be a valid Gmail address (@gmail.com required)"
        elif User.objects.filter(email=email).exists():
            errors["email_error"] = "Email is already registered"

        else:
            success["email_success"] = True

        # Password
        if len(password) < 8 or not re.search(r'\d', password):
            errors["password_error"] = "Password must be 8+ chars and include numbers"
        else:
            success["password_success"] = True

        # If errors → return WITH VALUES (VERY IMPORTANT)
        if errors:
            return render(request, "home.html", {
                **errors,
                **success,
                "username_value": username,
                "email_value": email,
                "role_selected": role,
                "first_name_value": first_name,
                "last_name_value": last_name,
            })

        # duplicate check
        if User.objects.filter(username=username).exists():
            return render(request, "home.html", {
                "username_error": "Username already exists",
                "email_value": email,
                "role_selected": role
            })

        # create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        if role == "teacher":
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            TeacherProfile.objects.create(
                user=user
            )
        if role == "student":
            StudentProfile.objects.create(user=user)

        return redirect(f"{reverse('home')}?signup=success")

    return redirect('home')


# LOGIN VIEW
def login_view(request):
    if request.method == "POST":

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user_obj = None

        if User.objects.filter(username=username).exists():
            user_obj = authenticate(
                request,
                username=username,
                password=password
            )

        elif User.objects.filter(email=username).exists():
            user_instance = User.objects.get(email=username)

            user_obj = authenticate(
                request,
                username=user_instance.username,
                password=password
            )

        # Username/email not found
        if not User.objects.filter(username=username).exists() and \
           not User.objects.filter(email=username).exists():

            return render(request, "home.html", {
                "login_username_error":
                    "Username or Email not recognized",
                "login_username_value": username,
            })

        # Password incorrect
        if user_obj is None:
            return render(request, "home.html", {
                "login_password_error":
                    "Password does not match username/email",
                "login_username_value": username,
            })

        # Success
        login(request, user_obj)
        if hasattr(user_obj, "teacherprofile"):
            return redirect("teacher_dashboard")

        return redirect("student_dashboard")

    return redirect("home")

@login_required
def html_dashboard(request):

    easy_quiz = Quiz.objects.filter(subject="HTML", difficulty="Easy").first()
    medium_quiz = Quiz.objects.filter(subject="HTML", difficulty="Medium").first()
    hard_quiz = Quiz.objects.filter(subject="HTML", difficulty="Hard").first()

    # check completion
    easy_done = StudentAttempt.objects.filter(
        student=request.user,
        quiz=easy_quiz,
        completed=True
    ).exists() if easy_quiz else False

    medium_done = StudentAttempt.objects.filter(
        student=request.user,
        quiz=medium_quiz,
        completed=True
    ).exists() if medium_quiz else False

    hard_done = StudentAttempt.objects.filter(
        student=request.user,
        quiz=hard_quiz,
        completed=True
    ).exists() if hard_quiz else False

    # history
    easy_attempt = StudentAttempt.objects.filter(
        student=request.user,
        quiz=easy_quiz
    ).order_by("-created_at").first()

    medium_attempt = StudentAttempt.objects.filter(
        student=request.user,
        quiz=medium_quiz
    ).order_by("-created_at").first()

    hard_attempt = StudentAttempt.objects.filter(
        student=request.user,
        quiz=hard_quiz
    ).order_by("-created_at").first()

    return render(request, "student/html_dashboard.html", {
        "easy_quiz": easy_quiz,
        "medium_quiz": medium_quiz,
        "hard_quiz": hard_quiz,

        "easy_done": easy_done,
        "medium_done": medium_done,
        "hard_done": hard_done,

        "easy_attempt": easy_attempt,
        "medium_attempt": medium_attempt,
        "hard_attempt": hard_attempt,
    })

@login_required
def css_dashboard(request):

    easy_quiz = Quiz.objects.filter(subject="CSS", difficulty="Easy").first()
    medium_quiz = Quiz.objects.filter(subject="CSS", difficulty="Medium").first()
    hard_quiz = Quiz.objects.filter(subject="CSS", difficulty="Hard").first()

    # check completion
    easy_done = StudentAttempt.objects.filter(
        student=request.user,
        quiz=easy_quiz,
        completed=True
    ).exists() if easy_quiz else False

    medium_done = StudentAttempt.objects.filter(
        student=request.user,
        quiz=medium_quiz,
        completed=True
    ).exists() if medium_quiz else False

    hard_done = StudentAttempt.objects.filter(
        student=request.user,
        quiz=hard_quiz,
        completed=True
    ).exists() if hard_quiz else False

    # history
    easy_attempt = StudentAttempt.objects.filter(
        student=request.user,
        quiz=easy_quiz
    ).order_by("-created_at").first()

    medium_attempt = StudentAttempt.objects.filter(
        student=request.user,
        quiz=medium_quiz
    ).order_by("-created_at").first()

    hard_attempt = StudentAttempt.objects.filter(
        student=request.user,
        quiz=hard_quiz
    ).order_by("-created_at").first()

    return render(request, "student/css_dashboard.html", {
        "easy_quiz": easy_quiz,
        "medium_quiz": medium_quiz,
        "hard_quiz": hard_quiz,

        "easy_done": easy_done,
        "medium_done": medium_done,
        "hard_done": hard_done,

        "easy_attempt": easy_attempt,
        "medium_attempt": medium_attempt,
        "hard_attempt": hard_attempt,
    })

@login_required
def js_dashboard(request):

    easy_quiz = Quiz.objects.filter(subject="JavaScript", difficulty="Easy").first()
    medium_quiz = Quiz.objects.filter(subject="JavaScript", difficulty="Medium").first()
    hard_quiz = Quiz.objects.filter(subject="JavaScript", difficulty="Hard").first()

    # check completion
    easy_done = StudentAttempt.objects.filter(
        student=request.user,
        quiz=easy_quiz,
        completed=True
    ).exists() if easy_quiz else False

    medium_done = StudentAttempt.objects.filter(
        student=request.user,
        quiz=medium_quiz,
        completed=True
    ).exists() if medium_quiz else False

    hard_done = StudentAttempt.objects.filter(
        student=request.user,
        quiz=hard_quiz,
        completed=True
    ).exists() if hard_quiz else False

    # history
    easy_attempt = StudentAttempt.objects.filter(
        student=request.user,
        quiz=easy_quiz
    ).order_by("-created_at").first()

    medium_attempt = StudentAttempt.objects.filter(
        student=request.user,
        quiz=medium_quiz
    ).order_by("-created_at").first()

    hard_attempt = StudentAttempt.objects.filter(
        student=request.user,
        quiz=hard_quiz
    ).order_by("-created_at").first()

    return render(request, "student/js_dashboard.html", {
        "easy_quiz": easy_quiz,
        "medium_quiz": medium_quiz,
        "hard_quiz": hard_quiz,

        "easy_done": easy_done,
        "medium_done": medium_done,
        "hard_done": hard_done,

        "easy_attempt": easy_attempt,
        "medium_attempt": medium_attempt,
        "hard_attempt": hard_attempt,
    })

@login_required
def submit_quiz(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    data = json.loads(request.body)

    quiz_id = data.get("quiz_id")
    answers = data.get("answers", {})

    quiz = Quiz.objects.get(id=quiz_id)

    # Create Attempt
    attempt = StudentAttempt.objects.create(
        student=request.user,
        quiz=quiz,
        score=0,
        completed=True,
        xp_earned=0  
    )

    total_questions = quiz.questions.count()
    correct_count = 0
    xp_earned = 0

    for question_id, user_answer in answers.items():

        question = Question.objects.get(id=question_id)

        is_correct = False
        selected_choice = None
        text_answer = None

        # ==========================
        # MCQ QUESTIONS
        # ==========================
        if question.question_type == "MCQ":

            try:
                selected_choice = Choice.objects.get(id=user_answer)

                if selected_choice.is_correct:

                    is_correct = True
                    correct_count += 1

                    if quiz.difficulty == "Easy":
                        xp_earned += 30

                    elif quiz.difficulty == "Medium":
                        xp_earned += 50

                    elif quiz.difficulty == "Hard":
                        xp_earned += 75

            except Choice.DoesNotExist:
                pass

        # ==========================
        # SYNTAX / BLANK QUESTIONS
        # ==========================
        else:

            if isinstance(user_answer, dict):

                text_answer = (
                    user_answer.get("blank")
                    or user_answer.get("text")
                    or ""
                ).strip()

            else:
                text_answer = str(user_answer).strip()

            correct_answer = (
                question.correct_answer or ""
            ).strip()

            if text_answer.lower() == correct_answer.lower():

                is_correct = True
                correct_count += 1

                if quiz.difficulty == "Easy":
                    xp_earned += 30

                elif quiz.difficulty == "Medium":
                    xp_earned += 50

                elif quiz.difficulty == "Hard":
                    xp_earned += 75

        # ==========================
        # SAVE ANSWER
        # ==========================
        StudentAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_choice=selected_choice,
            text_answer=text_answer,
            is_correct=is_correct
        )

    # ==========================
    # COMPUTE SCORE
    # ==========================
    score = (
        (correct_count / total_questions) * 100
        if total_questions > 0
        else 0
    )

    attempt.correct_answers = correct_count
    attempt.total_questions = total_questions
    attempt.score = score
    attempt.xp_earned = xp_earned
    attempt.save()

    # ==========================
    # UPDATE STUDENT PROGRESS
    # ==========================
    progress, created = StudentProgress.objects.get_or_create(
        student=request.user
    )

    progress.total_xp += xp_earned
    progress.completed_quizzes += 1
    progress.total_score += score

    # LEVEL SYSTEM
    # Every 500 XP = +1 level
    progress.level = (progress.total_xp // 250) + 1

    progress.save()

    percent = round(score, 2)
    total = total_questions
    correct = correct_count

    HistoryResult.objects.create(
        student=request.user,
        quiz_id=quiz.id,
        quiz_title=quiz.title,

        correct=correct,
        total=total,

        score_percent=percent,

        xp_earned=xp_earned,
        total_xp_after=progress.total_xp,

        level=progress.level,
        difficulty=quiz.difficulty,

        passed=percent >= 60
    )

    # ==========================
    # UNLOCK BADGES
    # ==========================
    available_badges = Badge.objects.filter(
        required_xp__lte=progress.total_xp
    )

    unlocked_badges = []

    for badge in available_badges:

        badge_obj, created = StudentBadge.objects.get_or_create(
            student=request.user,
            badge=badge
        )

        if created:

            badge_data = {
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "image": badge.image.url if badge.image else None,
                "required_xp": badge.required_xp
            }

            unlocked_badges.append(badge_data)

            # ✅ SAVE HISTORY HERE (CORRECT PLACE)
            HistoryBadge.objects.create(
                student=request.user,
                badge_name=badge.name,
                description=badge.description,
                image=badge.image,
                quiz=quiz
            )

    # ==========================
    # RESPONSE
    # ==========================
    return JsonResponse({
        "score": round(score, 2),
        "correct": correct_count,
        "total": total_questions,
        "xp_earned": xp_earned,
        "total_xp": progress.total_xp,
        "level": progress.level,
        "new_badges": unlocked_badges,
        "quiz_title": quiz.title,
        "difficulty": quiz.difficulty,
        
    })



def quiz_data(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)

    data = {
        "questions": []
    }

    for q in quiz.questions.all():

        data["questions"].append({
            "id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "code_snippet": q.code_snippet,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
             "subject": q.quiz.subject,

            "choices": [
                {
                    "id": c.id,
                    "choice_text": c.choice_text,
                    "is_correct": c.is_correct
                }
                for c in q.choices.all()
            ]
        })

    return JsonResponse(data)

@login_required
def progress_history(request, difficulty):

    difficulty = difficulty.capitalize()
    subject = request.GET.get("subject")

    history = HistoryResult.objects.filter(
        student=request.user,
        difficulty=difficulty
    ).order_by("-created_at")

    badges = HistoryBadge.objects.filter(
        student=request.user,
        quiz__subject=subject,
        quiz__difficulty=difficulty
    )

    data = {
        "history": list(history.values(
            "quiz_title",
            "score_percent",
            "xp_earned",
            "level",
            "passed",
            "difficulty",
            "correct",
            "total",
            "total_xp_after",
            "created_at"
        )),
        "badges": []
    }

    for b in badges:
        badge_obj = Badge.objects.filter(name=b.badge_name).first()

        data["badges"].append({
            "badge_name": b.badge_name,
            "description": b.description,
            "image": b.image.url if b.image else None,
            "required_xp": badge_obj.required_xp if badge_obj else 0
        })

    return JsonResponse(data)

from django.db.models import Avg

def leaderboard(request):

    leaderboard_data = []

    students = StudentProfile.objects.select_related("user")

    for profile in students:

        progress = getattr(profile.user, "progress", None)

        badges_qs = StudentBadge.objects.filter(
            student=profile.user
        ).select_related("badge")

        badge_count = badges_qs.count()

        badge_list = [
            {
                "name": b.badge.name,
                "image": (
                    b.badge.image.url
                    if b.badge.image else ""
                )
            }
            for b in badges_qs
        ]

        badge_json = json.dumps(badge_list)

        average_score = (
            HistoryResult.objects.filter(
                student=profile.user
            ).aggregate(
                avg=Avg("score_percent")
            )["avg"] or 0
        )

        leaderboard_data.append({
            "profile": profile,
            "xp": progress.total_xp if progress else 0,
            "level": progress.level if progress else 1,
            "completed_quizzes":
                progress.completed_quizzes if progress else 0,
            "average_score": round(average_score, 2),
            "badge_count": badge_count,
            "badges_json": badge_json,
        })

    leaderboard_data.sort(
        key=lambda x: (
            x["xp"],
            x["average_score"],
            x["badge_count"]
        ),
        reverse=True
    )

    for rank, student in enumerate(
        leaderboard_data,
        start=1
    ):
        student["rank"] = rank

    html_leaderboard = build_subject_leaderboard("HTML")
    css_leaderboard = build_subject_leaderboard("CSS")
    js_leaderboard = build_subject_leaderboard("JS")

    return render(
        request,
        "student/leaderboard.html",
        {
            "leaderboard": leaderboard_data,
            "total_students": len(leaderboard_data),

            "html_leaderboard": html_leaderboard,
            "css_leaderboard": css_leaderboard,
            "js_leaderboard": js_leaderboard,
        }
    )

SUBJECT_MAP = {
    "HTML": "HTML",
    "CSS": "CSS",
    "JS": "JavaScript",
    "JavaScript": "JavaScript",
}
def build_subject_leaderboard(subject_key):
    subject_name = SUBJECT_MAP.get(subject_key)
    if not subject_name:
        return []
    data = []

    students = StudentProfile.objects.select_related("user")

    for profile in students:
        progress = getattr(profile.user, "progress", None)

        subject_history = HistoryResult.objects.filter(
            student=profile.user,
            quiz__subject=subject_name
        )

        avg_score = (
            subject_history.aggregate(
                avg=Avg("score_percent")
            )["avg"] or 0
        )

        subject_xp = (
            subject_history.aggregate(
                total=Sum("xp_earned")
            )["total"] or 0
        )
        completed_subject_quizzes = subject_history.count()

        if avg_score == 0 and subject_xp == 0:
            continue

        badges_qs = HistoryBadge.objects.filter(
            student=profile.user,
            quiz__subject=subject_name
        ).select_related("quiz")

        badge_list = [
            {
                "name": b.badge_name,
                "image": (
                    b.image.url
                    if b.image else ""
                )
            }
            for b in badges_qs
        ]
        badge_count = badges_qs.count()

        data.append({
            "profile": profile,
            "xp": subject_xp,
            "average_score": round(avg_score, 2),
            "badge_count": badge_count,
            "badges_json": json.dumps(badge_list),
            "level": progress.level if progress else 1,
            "completed_quizzes": completed_subject_quizzes,
            
        })

    data.sort(
        key=lambda x: (
            x["xp"],
            x["average_score"]
        ),
        reverse=True
    )

    for rank, student in enumerate(data, start=1):
        student["rank"] = rank

    return data

@login_required
def profile(request):
    user = request.user

    profile = user.student_profile
    progress = getattr(user, "progress", None)

    histories = HistoryResult.objects.filter(
        student=user
    ).order_by("-created_at")

    average_score = histories.aggregate(
        avg=Avg("score_percent")
    )["avg"] or 0

    highest_score = histories.aggregate(
        max=Max("score_percent")
    )["max"] or 0

    total_correct = histories.aggregate(
        total=Sum("correct")
    )["total"] or 0

    total_questions = histories.aggregate(
        total=Sum("total")
    )["total"] or 0

    total_wrong = total_questions - total_correct

    perfect_scores = histories.filter(
        score_percent=100
    ).count()

    badges = StudentBadge.objects.filter(
        student=user
    ).select_related("badge")

    context = {
        "profile": profile,
        "progress": progress,
        "average_score": round(average_score, 2),
        "highest_score": highest_score,
        "total_correct": total_correct,
        "total_wrong": total_wrong,
        "perfect_scores": perfect_scores,
        "badge_count": badges.count(),
        "badges": badges,
        "recent_history": histories,
    }

    return render(
        request,
        "student/profile_page.html",
        context
    )

@login_required
def update_profile_picture(request):
    if request.method == "POST":
        profile = request.user.student_profile

        image = request.FILES.get("profile_picture")

        if image:
            profile.profile_picture = image
            profile.save()

    return redirect("profile")

@login_required
def learning_modules(request):


    return render(
        request,
        "student/learning_page.html"
    )

def html_learning_page(request):
    modules = LearningModule.objects.filter(
        subject='HTML',
        is_published=True
    ).prefetch_related('lessons')

    return render(
        request,
        'student/html_learning_page.html',
        {
            'modules': modules
        }
    )

def css_learning_page(request):
    modules = LearningModule.objects.filter(
        subject='CSS',
        is_published=True
    ).prefetch_related('lessons')

    return render(
        request,
        'student/css_learning_page.html',
        {
            'modules': modules
        }
    )
def js_learning_page(request):
    modules = LearningModule.objects.filter(
        subject='JS',
        is_published=True
    ).prefetch_related('lessons')

    return render(
        request,
        'student/js_learning_page.html',
        {
            'modules': modules
        }
    )

@login_required
def teacher_dashboard(request):
    students = StudentProfile.objects.select_related("user").order_by("student_id")


    return render(
        request,
        "teacher/teacher_dashboard.html",
        {
            "students": students
        }
    )


from django.db.models import Avg, Sum

def get_subject_analytics(subject):
    

    subject = subject.strip()

    histories = (
        HistoryResult.objects
        .filter(quiz__subject=subject)
        .values(
            "student",
            "student__student_profile__first_name",
            "student__student_profile__last_name",
            "student__student_profile__student_id",
            "student__student_profile__course",
             "student__student_profile__year_level",
            "student__student_profile__profile_picture",
        )
        .annotate(
            attempts=Count("id"),
            avg_score=Avg("score_percent"),
            latest_attempt=Max("created_at")
        )
        .order_by("-latest_attempt")
    )
    print("SUBJECT:", subject)
    print("QUERY:", histories.query)
    print("COUNT:", histories.count())

    base = HistoryResult.objects.filter(
        quiz__subject=subject
    )

    grouped = (
        base
        .values(
            "student",
            "student__student_profile__first_name",
            "student__student_profile__last_name"
        )
        .annotate(
            attempts=Count("id"),
            avg_score=Avg("score_percent"),
        )
    )

    stats = base.aggregate(
        top_score=Max("score_percent"),
        total_attempts=Count("id")
    )

    # Most active student
    most_active = grouped.order_by("-attempts").first()

    # Top performer
    top_performer = grouped.order_by("-avg_score").first()
    

    return {
        "subject": subject,
        "histories": histories,
        "students_count": grouped.count(),
        "total_attempts": stats["total_attempts"],

        "top_score": stats["top_score"],

        "most_active": most_active,
        "top_performer": top_performer,
        
    }

@login_required
def html_analytics(request):

    context = get_subject_analytics("HTML")

    return render(
        request,
        "teacher/html_analytics.html",
        context
    )

@login_required
def css_analytics(request):

    context = get_subject_analytics("CSS")

    return render(
        request,
        "teacher/css_analytics.html",
        context
    )

@login_required
def js_analytics(request):

    context = get_subject_analytics("JavaScript")

    return render(
        request,
        "teacher/js_analytics.html",
        context
    )



@login_required
def student_history(request, student_id):

    subject = request.GET.get("subject")

    histories = (
        HistoryResult.objects
        .filter(
            student_id=student_id,
            quiz__subject=subject
        )
        .select_related("quiz")
        .order_by("-created_at")
    )


    # PRELOAD all attempts in ONE query
    attempts = (
        StudentAttempt.objects
        .filter(
            student_id=student_id,
            quiz__in=histories.values_list("quiz", flat=True)
        )
        .prefetch_related(
            "answers__question",
            "answers__selected_choice"
        )
    )

    # Map quiz_id → attempt
    attempt_map = {a.quiz_id: a for a in attempts}

    data = []

    for history in histories:

        attempt = attempt_map.get(history.quiz_id)

        answers = []

        if attempt:

            for answer in attempt.answers.all():

                answers.append({
    "question": answer.question.question_text,
    "selected": (
        answer.selected_choice.choice_text
        if answer.selected_choice
        else answer.text_answer
    ),
    "correct": answer.is_correct,
    "feedback": answer.feedback,
    "code_snippet": answer.question.code_snippet,
    "explanation": answer.question.explanation,   # ✅ ADD THIS
    "choices": [
        {
            "choice_text": c.choice_text,
            "is_correct": c.is_correct
        }
        for c in answer.question.choices.all()
    ] if answer.question.question_type == "MCQ" else []
})
        teacher_feedback = QuizFeedback.objects.filter(
        history=history,
        teacher=request.user
    ).first()
        data.append({
            "id": history.id,
            "quiz": history.quiz_title,
            "difficulty": history.difficulty,
            "score": history.score_percent,
            "correct": history.correct,
            "total": history.total,
            "student_first_name": history.student.student_profile.first_name,
            "student_last_name": history.student.student_profile.last_name,
            "student_id": history.student.student_profile.student_id,
            "course": history.student.student_profile.course,
            "year_level": history.student.student_profile.year_level,
            "profile_picture": (
                history.student.student_profile.profile_picture.url
                if history.student.student_profile.profile_picture
                else None
            ),
            "has_feedback": QuizFeedback.objects.filter(
                history=history,
                teacher=request.user
            ).exists(),
              "teacher_feedback": (
            teacher_feedback.message
            if teacher_feedback
            else ""
        ),
            "answers": answers
        })

    return JsonResponse({"histories": data})

@login_required
def save_feedback(request, history_id):
    if request.method == "POST":

        data = json.loads(request.body)
        message = data.get("message", "").strip()

        if not message:
            return JsonResponse({
                "success": False,
                "error": "Empty feedback"
            })

        history = HistoryResult.objects.get(id=history_id)

        feedback, created = QuizFeedback.objects.update_or_create(
            history=history,
            teacher=request.user,
            defaults={
                "message": message
            }
        )

        return JsonResponse({
            "success": True,
            "created": created,
            "message": feedback.message
        })

    return JsonResponse({"success": False}, status=400)

@login_required
def get_feedback(request, history_id):
    feedback = QuizFeedback.objects.filter(
        history_id=history_id,
        teacher=request.user
    ).first()

    return JsonResponse({
        "success": True,
        "exists": feedback is not None,
        "message": feedback.message if feedback else ""
    })


@login_required
def overall_analytics(request):

    course = request.GET.get("course")
    year = request.GET.get("year")

    subjects = ['HTML', 'CSS', 'JavaScript']

    data = []
    easy = []
    medium = []
    hard = []
    xp = []

    for subject in subjects:

        attempts = StudentAttempt.objects.filter(
            quiz__subject=subject
        )

        # COURSE FILTER
        if course:
            attempts = attempts.filter(
                student__student_profile__course=course
            )

        # YEAR FILTER
        if year:
            attempts = attempts.filter(
                student__student_profile__year_level=year
            )

        total_attempts = attempts.count()

        avg_score = (
            attempts.aggregate(avg=Avg("score"))["avg"]
            or 0
        )

        passed = attempts.filter(
            score__gte=75
        ).count()

        failed = attempts.filter(
            score__lt=75
        ).count()

        user_attempts = (
            attempts
            .values("student")
            .distinct()
            .count()
        )

        easy.append(
            attempts.filter(
                quiz__difficulty="Easy"
            ).count()
        )

        medium.append(
            attempts.filter(
                quiz__difficulty="Medium"
            ).count()
        )

        hard.append(
            attempts.filter(
                quiz__difficulty="Hard"
            ).count()
        )

        xp.append(
            attempts.aggregate(
                total=Sum("xp_earned")
            )["total"] or 0
        )

        data.append({
            "subject": subject,
            "avg_score": round(avg_score, 1),
            "attempts": total_attempts,
            "passed": passed,
            "failed": failed,
            "user_attempts": user_attempts,
        })

    return render(
        request,
        "teacher/overall_analytics.html",
        {
            "data": data,
            "subjects": json.dumps(subjects),
            "avg_scores": json.dumps(
                [d["avg_score"] for d in data]
            ),
            "attempts": json.dumps(
                [d["attempts"] for d in data]
            ),
            "easy": json.dumps(easy),
            "medium": json.dumps(medium),
            "hard": json.dumps(hard),
            "xp_trend": json.dumps(xp),

            "selected_course": course,
            "selected_year": year,
        }
    )


@login_required
def notification_data(request):

    feedbacks = QuizFeedback.objects.filter(
        history__student=request.user
    ).select_related("history", "teacher").order_by("-created_at")
    unread_count = QuizFeedback.objects.filter(
        history__student=request.user,
        is_read=False
    ).count()

    data = []
    

    for f in feedbacks:
        data.append({
            "id": f.id,
            "quiz": f.history.quiz_title,
            "message": f.message,
            "teacher_first_name": f.teacher.first_name or f.teacher.username,
            "date": localtime(f.created_at).strftime("%b %d, %Y • %I:%M %p"),
            "is_read": f.is_read,
        })

    return JsonResponse({"notifications": data, "unread_count": unread_count})
@login_required
def mark_notification_read(request, pk):
    feedback = QuizFeedback.objects.get(id=pk, history__student=request.user)
    feedback.is_read = True
    feedback.save()

    return JsonResponse({"success": True})
# LOGOUT VIEW
def logout_view(request):
    logout(request)
    return redirect('home')