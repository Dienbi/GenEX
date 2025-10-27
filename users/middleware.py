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
            '/courses/',  # Liste des cours (sauf cours individuels)
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
            '/courses/admin/',  # Administration des cours
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
            is_allowed = any(path.startswith(allowed) for allowed in self.allowed_paths)
            
            # Allow admins to view individual courses (format: /courses/ID/)
            # Pattern: /courses/123/ (commence par /courses/, se termine par /, et a un ID numérique)
            import re
            is_individual_course = (path.startswith('/courses/') and 
                                  path.endswith('/') and 
                                  path != '/courses/' and
                                  re.match(r'^/courses/\d+/$', path))
            
            # Check if path is restricted (but allow individual courses)
            is_restricted = False
            for restricted in self.restricted_paths:
                if path.startswith(restricted):
                    # Si c'est /courses/, vérifier si c'est un cours individuel
                    if restricted == '/courses/' and is_individual_course:
                        continue  # Ne pas considérer comme restreint
                    is_restricted = True
                    break
            
            # Redirect admins away from restricted paths to backoffice
            if is_restricted and not is_allowed:
                return redirect('users:backoffice_dashboard')
        
        response = self.get_response(request)
        return response
