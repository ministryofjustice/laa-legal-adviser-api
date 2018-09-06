from django.http import HttpResponse

class PingMiddleware(object):
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    if request.method == "GET":
      if request.path == "/ping.json":
        return self.ping(request)
    return self.get_response(request)

  def ping(self, request):
    """
    Returns that the server is alive.
    """
    return HttpResponse("OK")
