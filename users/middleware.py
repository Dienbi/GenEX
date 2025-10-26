from django.shortcuts import redirect
from django.urls import reverse


class AdminAccessMiddleware:
    """
    Middleware to restrict admin users to backoffice only.
    Admins cannot access regular user paths like courses, exercises, etc.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Paths that admins are NOT allowed to access
        self.restricted_paths = [
            '/courses/',
            '/exercises/',
            '/quizzes/',
            '/chatbot/',
            '/voice/',
            '/dashboard/',
            '/about/',
        ]
        
        # Paths that admins CAN access
        self.allowed_paths = [
            '/backoffice/',
            '/signin/',
            '/signout/',
            '/admin/',  # Django admin
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Check if user is admin
        if request.user.is_authenticated and (request.user.is_superuser or request.user.user_type == 'admin'):
            path = request.path
            
            # Redirect home page to backoffice for admins
            if path == '/':
                return redirect('users:backoffice_dashboard')
            
            # Check if trying to access restricted path
            is_restricted = any(path.startswith(restricted) for restricted in self.restricted_paths)
            is_allowed = any(path.startswith(allowed) for allowed in self.allowed_paths)
            
            # Redirect admins away from restricted paths to backoffice
            if is_restricted and not is_allowed:
                return redirect('users:backoffice_dashboard')
        
        response = self.get_response(request)
        return response
