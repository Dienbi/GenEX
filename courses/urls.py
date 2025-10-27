from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # URLs pour les cours
    path('', views.course_list, name='course_list'),
    path('create/', views.course_create, name='course_create'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('<int:pk>/summary/', views.course_summary, name='course_summary'),
    path('<int:pk>/audio/<int:section_index>/', views.generate_section_audio, name='generate_section_audio'),
    path('<int:pk>/audio-list/', views.get_course_audio_list, name='get_course_audio_list'),
    path('<int:pk>/download-pdf/', views.course_download_pdf, name='course_download_pdf'),
    path('<int:pk>/regenerate-pdf/', views.course_regenerate_pdf, name='course_regenerate_pdf'),
    path('<int:course_pk>/assign-folder/', views.course_assign_folder, name='course_assign_folder'),
    path('<int:course_pk>/unassign-folder/<int:folder_pk>/', views.course_unassign_folder, name='course_unassign_folder'),
    
    # URLs pour les dossiers
    path('folders/', views.folder_list, name='folder_list'),
    path('folders/create/', views.folder_create, name='folder_create'),
    path('folders/<int:pk>/', views.folder_detail, name='folder_detail'),
    path('folders/<int:pk>/edit/', views.folder_edit, name='folder_edit'),
    path('folders/<int:pk>/delete/', views.folder_delete, name='folder_delete'),
    
    # URLs pour l'administration des cours
    path('admin/', views.admin_course_list, name='admin_course_list'),
    path('admin/create/', views.admin_course_create, name='admin_course_create'),
    path('admin/<int:pk>/', views.admin_course_detail, name='admin_course_detail'),
    path('admin/<int:pk>/edit/', views.admin_course_edit, name='admin_course_edit'),
    path('admin/<int:pk>/delete/', views.admin_course_delete, name='admin_course_delete'),
]