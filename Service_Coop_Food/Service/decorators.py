from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import redirect
from functools import wraps
from django.core.exceptions import PermissionDenied


def allowed_user(allowed_roles = []):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            role_symbol = None
            if request.user.role.symbol is not None:
                role_symbol = request.user.role.symbol
            if role_symbol in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return  HttpResponse('403 ! You no have permission')
        return  wrapper_func
    return decorator


def allowed_permission(allowed_per = ''):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            permission = None
            list_per = request.user.role.role_permission.all().values_list('name', flat=True)
            if allowed_per in list_per:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
                # return  HttpResponse('403 ! You no have permission')
        return  wrapper_func
    return decorator

def allowed_cus_manager(cus = 0):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            cus_manager = request.user.cus_manager.all().values_list('id', flat=True)
            if cus in cus_manager:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
                # return  HttpResponse('403 ! You no have permission manager cus')
        return wrapper_func()
    return decorator()
# def only_admin():
#     def decrator(view_func):
#         @wraps(view_func)
#         def wrap_func(request, *args, **kwargs):
#             role = None
#             if request.user.role is not  None:
#                 role = request.user.role
#             if role == 1:
#                 return wrap_func(request, *args, **kwargs)
#             else:
#                 return HttpResponseRedirect('/')
#         return wrap_func
#     return decrator