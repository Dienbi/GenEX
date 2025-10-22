from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from users.models import User


def home(request):
    """Home page view"""
    return render(request, 'main/index.html')


def about(request):
    """About page view"""
    return render(request, 'main/about.html')


def signup(request):
    """Signup page view"""
    if request.user.is_authenticated:
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type', 'student')
        
        # Validation
        if not username or not email or not password:
            messages.error(request, 'All fields are required!')
            return render(request, 'main/signup.html')
        
        if password != password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'main/signup.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters!')
            return render(request, 'main/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'main/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return render(request, 'main/signup.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type=user_type
            )
            
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('main:signin')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'main/signup.html')
    
    return render(request, 'main/signup.html')


def signin(request):
    """Signin page view"""
    if request.user.is_authenticated:
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password!')
            return render(request, 'main/signin.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next page if specified, otherwise dashboard
            next_page = request.GET.get('next', 'main:dashboard')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'main/signin.html')


def signout(request):
    """Signout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('main:home')


def forgot_password(request):
    """Forgot password page view"""
    if request.user.is_authenticated:
        return redirect('main:dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if not email:
            messages.error(request, 'Please provide your email address!')
            return render(request, 'main/forgot_password.html')
        
        try:
            user = User.objects.get(email=email)
            # TODO: Implement proper password reset with token
            messages.success(request, 
                'If an account exists with this email, you will receive password reset instructions.')
            return redirect('main:signin')
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist
            messages.success(request, 
                'If an account exists with this email, you will receive password reset instructions.')
            return redirect('main:signin')
    
    return render(request, 'main/forgot_password.html')


@login_required
def dashboard(request):
    """User dashboard"""
    context = {
        'user': request.user,
    }
    return render(request, 'main/dashboard.html', context)
