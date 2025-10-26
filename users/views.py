from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
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
    total_users = User.objects.count()
    total_students = User.objects.filter(user_type='student').count()
    total_admins = User.objects.filter(user_type='admin').count()
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_admins': total_admins,
        'recent_users': recent_users,
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
