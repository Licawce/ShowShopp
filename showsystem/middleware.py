from django.shortcuts import redirect


class AdminAccessMiddleware:
   

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            user = request.user
            if not user.is_authenticated or not user.is_staff:
                return redirect('/')
        return self.get_response(request)
