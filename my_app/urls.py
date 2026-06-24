from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('html-dashboard/', views.html_dashboard, name='html_dashboard'),
    path('css-dashboard/', views.css_dashboard, name='css_dashboard'),
    path('js-dashboard/', views.js_dashboard, name='js_dashboard'),
    path("quiz-data/<int:quiz_id>/", views.quiz_data, name="quiz_data"),
    path("submit-quiz/", views.submit_quiz, name="submit_quiz"),
    path("profile/update/", views.update_profile, name="update_profile"),
    path("learning/html/", views.html_learning_page, name="html_learning"),
    path("learning/css/", views.css_learning_page, name="css_learning"),
    path("learning/js/", views.js_learning_page, name="js_learning"),
    path("feedback/save/<int:history_id>/", views.save_feedback, name="save_feedback"),
    path("feedback/get/<int:history_id>/", views.get_feedback, name="get_feedback"),
    path("teacher/overall-analytics/", views.overall_analytics, name="overall_analytics"),
    path("notifications/read/<int:pk>/", views.mark_notification_read, name="mark_notification_read"),
    path(
        "notifications/",
        views.notification_data,
        name="notification_data"
    ),
    path(
        "teacher/html-analytics/",
        views.html_analytics,
        name="html_analytics"
    ),
    path(
        "teacher/css-analytics/",
        views.css_analytics,
        name="css_analytics"
    ),
    path(
        "teacher/js-analytics/",
        views.js_analytics,
        name="js_analytics"
    ),
    path(
    "teacher/student-history/<int:student_id>/",
    views.student_history,
    name="student_history"
),
    path(
        "teacher/dashboard/",
        views.teacher_dashboard,
        name="teacher_dashboard"
    ),
    path(
        "learning/",
        views.learning_modules,
        name="learning_modules"
    ),
    path(
        "progress-history/<str:difficulty>/",
        views.progress_history,
        name="progress_history"
    ),
    path(
    "profile/",
    views.profile,
    name="profile"
),
    path(
    "leaderboard/",
    views.leaderboard,
    name="leaderboard"
),
path(
    "update-profile-picture/",
    views.update_profile_picture,
    name="update_profile_picture"
),
]