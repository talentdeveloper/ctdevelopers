from chat.utils import update_user_presence


class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_user = request.user
        if request.user.is_authenticated():
            update_user_presence(current_user)

        response = self.get_response(request)
        return response
