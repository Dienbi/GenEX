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
