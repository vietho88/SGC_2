from django.http import HttpResponse, HttpResponseRedirect

def check_has_permission_in_cus(request, cus):
    if int(cus) in request.user.manager_cus.all().values_list('id', flat=True):
        return True
    return False