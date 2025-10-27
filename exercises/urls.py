from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'exercises'

router = DefaultRouter()
router.register(r'categories', views.ExerciseCategoryViewSet, basename='exercise-category')
router.register(r'types', views.ExerciseTypeViewSet, basename='exercise-type')
router.register(r'difficulties', views.DifficultyLevelViewSet, basename='difficulty-level')
router.register(r'exercises', views.ExerciseViewSet, basename='exercise')
router.register(r'attempts', views.ExerciseAttemptViewSet, basename='exercise-attempt')
router.register(r'sessions', views.ExerciseSessionViewSet, basename='exercise-session')
router.register(r'ai-generations', views.AIExerciseGenerationViewSet, basename='ai-generation')
router.register(r'collections', views.ExerciseCollectionViewSet, basename='exercise-collection')
router.register(r'favorites', views.ExerciseFavoriteViewSet, basename='exercise-favorite')
router.register(r'wishlist', views.ExerciseWishlistViewSet, basename='exercise-wishlist')
router.register(r'history', views.ExerciseHistoryViewSet, basename='exercise-history')

urlpatterns = [
    # Interface utilisateur
    path('', views.exercise_dashboard, name='exercise-dashboard'),
    path('<int:exercise_id>/', views.exercise_detail, name='exercise-detail'),
    path('<int:exercise_id>/solve/', views.exercise_solve, name='exercise-solve'),
    path('results/<int:submission_id>/', views.exercise_results, name='exercise-results'),
    
    # Collections
    path('collections/', views.collections_list, name='collections-list'),
    path('collections/<int:collection_id>/', views.collection_detail, name='collection-detail'),
    path('collections/<int:collection_id>/exercises/', views.collection_exercises, name='collection-exercises'),
    
    # Favoris et Wishlist
    path('favorites/', views.favorites_list, name='favorites-list'),
    path('wishlist/', views.wishlist_list, name='wishlist-list'),
    
    # API
    path('api/', include(router.urls)),
]