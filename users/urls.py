from django.urls import path
from . import views

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

urlpatterns = api_urlpatterns + web_urlpatterns
