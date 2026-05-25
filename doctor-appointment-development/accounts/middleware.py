"""
Custom middleware for accounts app
"""
from django.shortcuts import redirect
from django.contrib import messages


class UserRoleMiddleware:
    """Middleware to handle user role-based access"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Process view for role-based access control"""
        if not request.user.is_authenticated:
            return None
        
        # Check if user is trying to access wrong dashboard
        path = request.path_info
        
        if path.startswith('/dashboard/'):
            if path.startswith('/dashboard/admin/'):
                if not request.user.is_super_admin():
                    messages.error(request, 'You do not have permission to access this page.')
                    return redirect('dashboard:index')
            elif path.startswith('/dashboard/doctor/'):
                if not request.user.is_doctor():
                    messages.error(request, 'You do not have permission to access this page.')
                    return redirect('dashboard:index')
            elif path.startswith('/dashboard/employee/'):
                if not request.user.is_employee():
                    messages.error(request, 'You do not have permission to access this page.')
                    return redirect('dashboard:index')
        
        return None
