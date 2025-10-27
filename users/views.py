from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_api(request):
    """API endpoint for user registration"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_api(request):
    """API endpoint for user login"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_api(request):
    """API endpoint for user logout"""
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({
            'error': 'Token not found'
        }, status=status.HTTP_400_BAD_REQUEST)


# Traditional Django views (for HTML templates)
def register_view(request):
    """Traditional Django view for user registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', 'student')
        level = request.POST.get('level')
        student_class = request.POST.get('student_class')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'users/register.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            level=level,
            student_class=student_class
        )
        messages.success(request, 'Registration successful')
        return redirect('login')
    
    return render(request, 'users/register.html')


def login_view(request):
    """Traditional Django view for user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'users/login.html')


@login_required
def logout_view(request):
    """Traditional Django view for user logout"""
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('login')


@login_required
def dashboard_view(request):
    """User dashboard view"""
    return render(request, 'users/dashboard.html', {'user': request.user})


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.level = request.POST.get('level', user.level)
        user.student_class = request.POST.get('student_class', user.student_class)
        user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    
    return render(request, 'users/profile.html', {'user': request.user})


# ===== BACKOFFICE VIEWS (Admin Only) =====
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_superuser or user.user_type == 'admin')


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_dashboard(request):
    """Admin backoffice dashboard"""
    from quizzes.models import Quiz, QuizAttempt
    from exercises.models import Exercise, ExerciseSubmission
    
    total_users = User.objects.count()
    total_students = User.objects.filter(user_type='student').count()
    total_admins = User.objects.filter(user_type='admin').count()
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Quiz statistics
    total_quizzes = Quiz.objects.count()
    active_quizzes = Quiz.objects.filter(is_active=True).count()
    total_quiz_attempts = QuizAttempt.objects.count()
    
    # Exercise statistics
    total_exercises = Exercise.objects.count()
    public_exercises = Exercise.objects.filter(is_public=True).count()
    total_exercise_submissions = ExerciseSubmission.objects.count()
    correct_submissions = ExerciseSubmission.objects.filter(is_correct=True).count()
    exercise_success_rate = (correct_submissions / total_exercise_submissions * 100) if total_exercise_submissions > 0 else 0
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_admins': total_admins,
        'recent_users': recent_users,
        'total_quizzes': total_quizzes,
        'active_quizzes': active_quizzes,
        'total_quiz_attempts': total_quiz_attempts,
        'total_exercises': total_exercises,
        'public_exercises': public_exercises,
        'total_exercise_submissions': total_exercise_submissions,
        'correct_submissions': correct_submissions,
        'exercise_success_rate': exercise_success_rate,
    }
    return render(request, 'users/backoffice/dashboard.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_user_list(request):
    """Admin user list view with search and pagination"""
    search_query = request.GET.get('search', '')
    user_type_filter = request.GET.get('user_type', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Apply user type filter
    if user_type_filter:
        users = users.filter(user_type=user_type_filter)
    
    # Pagination
    paginator = Paginator(users, 20)  # 20 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'user_type_filter': user_type_filter,
    }
    return render(request, 'users/backoffice/user_list.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_user_create(request):
    """Admin create user view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        user_type = request.POST.get('user_type', 'student')
        level = request.POST.get('level', '')
        student_class = request.POST.get('student_class', '')
        is_active = request.POST.get('is_active') == 'on'
        
        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'users/backoffice/user_form.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'users/backoffice/user_form.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            level=level if level else None,
            student_class=student_class if student_class else None,
            is_active=is_active
        )
        
        messages.success(request, f'User {username} created successfully')
        return redirect('users:backoffice_user_list')
    
    context = {'action': 'create'}
    return render(request, 'users/backoffice/user_form.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_user_update(request, user_id):
    """Admin update user view"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.user_type = request.POST.get('user_type', user.user_type)
        user.level = request.POST.get('level', user.level)
        user.student_class = request.POST.get('student_class', user.student_class)
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Update password if provided
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        
        user.save()
        messages.success(request, f'User {user.username} updated successfully')
        return redirect('users:backoffice_user_list')
    
    context = {
        'action': 'update',
        'user_obj': user,
    }
    return render(request, 'users/backoffice/user_form.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_user_delete(request, user_id):
    """Admin delete user view"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent admin from deleting themselves
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account')
        return redirect('users:backoffice_user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully')
        return redirect('users:backoffice_user_list')
    
    context = {'user_obj': user}
    return render(request, 'users/backoffice/user_confirm_delete.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_user_detail(request, user_id):
    """Admin view user detail"""
    user = get_object_or_404(User, id=user_id)
    context = {'user_obj': user}
    return render(request, 'users/backoffice/user_detail.html', context)


# ===== BACKOFFICE QUIZ VIEWS (Admin Only) =====
from quizzes.models import Quiz, Question, QuizAttempt
from quizzes.ai_service import GeminiQuizGenerator


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_quiz_list(request):
    """Admin quiz list view with search and pagination"""
    search_query = request.GET.get('search', '')
    
    # Only show quizzes created by admins or superusers
    quizzes = Quiz.objects.filter(
        Q(created_by__user_type='admin') | Q(created_by__is_superuser=True)
    ).order_by('-created_at')
    
    # Apply search filter
    if search_query:
        quizzes = quizzes.filter(
            Q(title__icontains=search_query) |
            Q(subject__icontains=search_query)
        )
    
    # Add attempt count for each quiz
    for quiz in quizzes:
        quiz.attempt_count = quiz.attempts.count()
        quiz.can_edit = quiz.attempt_count == 0
    
    # Pagination
    paginator = Paginator(quizzes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'users/backoffice/quiz_list.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_quiz_create(request):
    """Admin create quiz view using AI"""
    if request.method == 'POST':
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        user_prompt = request.POST.get('user_prompt')
        
        if not title or not subject or not user_prompt:
            messages.error(request, 'All fields are required')
            return render(request, 'users/backoffice/quiz_form.html')
        
        try:
            # Generate quiz using AI
            ai_generator = GeminiQuizGenerator()
            quiz_data = ai_generator.generate_quiz(user_prompt, subject)
            
            # Create quiz
            quiz = Quiz.objects.create(
                title=title,
                subject=subject,
                user_prompt=user_prompt,
                created_by=request.user,
                is_active=True
            )
            
            # Create questions
            for idx, q_data in enumerate(quiz_data['questions'], 1):
                Question.objects.create(
                    quiz=quiz,
                    question_text=q_data['question_text'],
                    option_a=q_data['option_a'],
                    option_b=q_data['option_b'],
                    option_c=q_data['option_c'],
                    option_d=q_data['option_d'],
                    correct_answer=q_data['correct_answer'].upper(),
                    order=idx
                )
            
            messages.success(request, f'Quiz "{title}" created successfully with {len(quiz_data["questions"])} questions!')
            return redirect('users:backoffice_quiz_list')
            
        except Exception as e:
            messages.error(request, f'Failed to generate quiz: {str(e)}')
            return render(request, 'users/backoffice/quiz_form.html', {
                'action': 'create',
                'title': title,
                'subject': subject,
                'user_prompt': user_prompt
            })
    
    context = {'action': 'create'}
    return render(request, 'users/backoffice/quiz_form.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_quiz_detail(request, quiz_id):
    """Admin view quiz detail"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    attempts = quiz.attempts.all()[:10]  # Last 10 attempts
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'attempts': attempts,
        'total_attempts': quiz.attempts.count(),
        'can_edit': quiz.attempts.count() == 0,
    }
    return render(request, 'users/backoffice/quiz_detail.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_quiz_update(request, quiz_id):
    """Admin update quiz view - only if no attempts"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if quiz can be edited
    if quiz.attempts.count() > 0:
        messages.error(request, 'Cannot edit this quiz - users have already taken it')
        return redirect('users:backoffice_quiz_detail', quiz_id=quiz.id)
    
    if request.method == 'POST':
        quiz.title = request.POST.get('title', quiz.title)
        quiz.subject = request.POST.get('subject', quiz.subject)
        quiz.is_active = request.POST.get('is_active') == 'on'
        quiz.save()
        
        # Update questions
        questions = quiz.questions.all()
        for question in questions:
            question_id = str(question.id)
            question.question_text = request.POST.get(f'question_text_{question_id}', question.question_text)
            question.option_a = request.POST.get(f'option_a_{question_id}', question.option_a)
            question.option_b = request.POST.get(f'option_b_{question_id}', question.option_b)
            question.option_c = request.POST.get(f'option_c_{question_id}', question.option_c)
            question.option_d = request.POST.get(f'option_d_{question_id}', question.option_d)
            question.correct_answer = request.POST.get(f'correct_answer_{question_id}', question.correct_answer)
            question.save()
        
        messages.success(request, f'Quiz "{quiz.title}" updated successfully')
        return redirect('users:backoffice_quiz_detail', quiz_id=quiz.id)
    
    context = {
        'action': 'update',
        'quiz': quiz,
        'questions': quiz.questions.all(),
    }
    return render(request, 'users/backoffice/quiz_edit.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_quiz_delete(request, quiz_id):
    """Admin delete quiz view"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        title = quiz.title
        quiz.delete()
        messages.success(request, f'Quiz "{title}" deleted successfully')
        return redirect('users:backoffice_quiz_list')
    
    context = {
        'quiz': quiz,
        'attempts_count': quiz.attempts.count()
    }
    return render(request, 'users/backoffice/quiz_confirm_delete.html', context)


# ==================== EXERCISES MANAGEMENT ====================

@user_passes_test(is_admin, login_url='main:signin')
def backoffice_exercise_list(request):
    """Admin exercise list view with search and pagination"""
    from exercises.models import Exercise, ExerciseCategory, ExerciseType, DifficultyLevel
    
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    difficulty_filter = request.GET.get('difficulty', '')
    type_filter = request.GET.get('type', '')
    
    exercises = Exercise.objects.all().order_by('-created_at')
    
    # Apply search filter
    if search_query:
        exercises = exercises.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Apply category filter
    if category_filter:
        exercises = exercises.filter(category_id=category_filter)
    
    # Apply difficulty filter
    if difficulty_filter:
        exercises = exercises.filter(difficulty_id=difficulty_filter)
    
    # Apply type filter
    if type_filter:
        exercises = exercises.filter(exercise_type_id=type_filter)
    
    # Pagination
    paginator = Paginator(exercises, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    categories = ExerciseCategory.objects.all()
    difficulties = DifficultyLevel.objects.all()
    types = ExerciseType.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'difficulty_filter': difficulty_filter,
        'type_filter': type_filter,
        'categories': categories,
        'difficulties': difficulties,
        'types': types,
        'total_exercises': exercises.count(),
    }
    return render(request, 'users/backoffice/exercise_list.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_exercise_detail(request, exercise_id):
    """Admin exercise detail view"""
    from exercises.models import Exercise, ExerciseSubmission
    
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    # Get recent submissions
    recent_submissions = ExerciseSubmission.objects.filter(exercise=exercise).order_by('-submission_time')[:10]
    
    # Get statistics
    total_submissions = ExerciseSubmission.objects.filter(exercise=exercise).count()
    correct_submissions = ExerciseSubmission.objects.filter(exercise=exercise, is_correct=True).count()
    success_rate = (correct_submissions / total_submissions * 100) if total_submissions > 0 else 0
    
    context = {
        'exercise': exercise,
        'recent_submissions': recent_submissions,
        'total_submissions': total_submissions,
        'correct_submissions': correct_submissions,
        'success_rate': success_rate,
    }
    return render(request, 'users/backoffice/exercise_detail.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_exercise_create(request):
    """Admin create exercise view"""
    from exercises.models import ExerciseCategory, ExerciseType, DifficultyLevel
    from exercises.forms import ExerciseForm
    
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.created_by = request.user
            exercise.save()
            messages.success(request, f'Exercise "{exercise.title}" created successfully')
            return redirect('users:backoffice_exercise_list')
    else:
        form = ExerciseForm()
    
    context = {
        'form': form,
        'categories': ExerciseCategory.objects.all(),
        'types': ExerciseType.objects.all(),
        'difficulties': DifficultyLevel.objects.all(),
    }
    return render(request, 'users/backoffice/exercise_create.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_exercise_edit(request, exercise_id):
    """Admin edit exercise view"""
    from exercises.models import Exercise
    from exercises.forms import ExerciseForm
    
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            messages.success(request, f'Exercise "{exercise.title}" updated successfully')
            return redirect('users:backoffice_exercise_detail', exercise_id=exercise.id)
    else:
        form = ExerciseForm(instance=exercise)
    
    context = {
        'form': form,
        'exercise': exercise,
    }
    return render(request, 'users/backoffice/exercise_edit.html', context)


@user_passes_test(is_admin, login_url='main:signin')
def backoffice_exercise_delete(request, exercise_id):
    """Admin delete exercise view"""
    from exercises.models import Exercise, ExerciseSubmission
    
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    if request.method == 'POST':
        title = exercise.title
        exercise.delete()
        messages.success(request, f'Exercise "{title}" deleted successfully')
        return redirect('users:backoffice_exercise_list')
    
    # Get submission count
    submissions_count = ExerciseSubmission.objects.filter(exercise=exercise).count()
    
    context = {
        'exercise': exercise,
        'submissions_count': submissions_count,
    }
    return render(request, 'users/backoffice/exercise_delete.html', context)