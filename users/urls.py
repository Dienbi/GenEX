from django.urls import path
from . import views

app_name = 'users'

# API endpoints
api_urlpatterns = [
    path('api/register/', views.register_api, name='api-register'),
    path('api/login/', views.login_api, name='api-login'),
    path('api/logout/', views.logout_api, name='api-logout'),
    path('api/profile/', views.UserDetailView.as_view(), name='api-profile'),
    path('api/list/', views.UserListView.as_view(), name='api-user-list'),
]

# Traditional web views
web_urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
]

# Backoffice (Admin) URLs
backoffice_urlpatterns = [
    path('backoffice/', views.backoffice_dashboard, name='backoffice_dashboard'),
    path('backoffice/users/', views.backoffice_user_list, name='backoffice_user_list'),
    path('backoffice/users/create/', views.backoffice_user_create, name='backoffice_user_create'),
    path('backoffice/users/<int:user_id>/', views.backoffice_user_detail, name='backoffice_user_detail'),
    path('backoffice/users/<int:user_id>/edit/', views.backoffice_user_update, name='backoffice_user_update'),
    path('backoffice/users/<int:user_id>/delete/', views.backoffice_user_delete, name='backoffice_user_delete'),
    
    # Quiz management
    path('backoffice/quizzes/', views.backoffice_quiz_list, name='backoffice_quiz_list'),
    path('backoffice/quizzes/create/', views.backoffice_quiz_create, name='backoffice_quiz_create'),
    path('backoffice/quizzes/<int:quiz_id>/', views.backoffice_quiz_detail, name='backoffice_quiz_detail'),
    path('backoffice/quizzes/<int:quiz_id>/edit/', views.backoffice_quiz_update, name='backoffice_quiz_update'),
    path('backoffice/quizzes/<int:quiz_id>/delete/', views.backoffice_quiz_delete, name='backoffice_quiz_delete'),
]

urlpatterns = api_urlpatterns + web_urlpatterns + backoffice_urlpatterns
