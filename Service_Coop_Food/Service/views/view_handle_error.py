from django.shortcuts import render

def handler404(request, *args, **kwargs):
    return render(request, 'handler_error/404.html', status=404)
def handler500(request, *args, **kwargs):
    return render(request, 'handler_error/500.html', status=500)
def handler403(request, *args, **kwargs):
    return render(request, 'handler_error/403.html', status=403)