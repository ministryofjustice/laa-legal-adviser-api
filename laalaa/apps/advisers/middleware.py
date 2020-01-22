from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class PingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == "GET":
            if request.path == "/ping.json":
                return self.ping(request)
        pass

    def ping(self, request):
        """
        Returns that the server is alive.
        """
        return HttpResponse("OK")
