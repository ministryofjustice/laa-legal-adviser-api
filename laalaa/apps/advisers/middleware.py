from django.http import HttpResponse


class PingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.ping(request) or self.get_response(request)

    def ping(self, request):
        """
        Returns that the server is alive.
        """
        if request.method == "GET":
            if request.path == "/ping.json":
                return HttpResponse("OK")
