from  django.shortcuts import render
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login as log_in, logout as log_out
from django.contrib.auth.hashers import check_password, make_password
from Service.models import UserCoop
from django.contrib.auth.decorators import login_required
import re

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return render(request, 'auth/login.html', {})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')
        user =  authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_lock :
                context = {
                    'old_user': username,
                    'message': 'Tài khoản của bạn tạm thời đã bị khóa, vui lòng liên hệ Admin để được hỗ trợ. Xin cảm ơn!'
                }
                return render(request, 'auth/login.html', context)
            log_in(request, user)
            list_cus_manager = request.user.manager_cus.all().values_list('id', flat=True)
            list_per = request.user.role.role_permission.all().values_list('name', flat=True)
            request.session['list_per'] = list(list_per)
            request.session['list_cus_manager'] = list(list_cus_manager)
            if username == password:
                request.session['required_change_path'] = True
            if next_url :
                return HttpResponseRedirect(next_url)
            else:
                if request.user.is_superuser:
                    return HttpResponseRedirect('/admin')
                elif 'Xem hóa đơn' in list_per:
                    return HttpResponseRedirect('/home/bill')
                else:
                    return HttpResponseRedirect('/home/invoice-list')
        else:
            context = {
                'old_user' : username,
                'message' : 'Thông tin tài khoản hoặc mật khẩu không đúng !!'
            }
            return render(request, 'auth/login.html', context)

class LogoutView(View):
    def get(self, request):
        log_out(request)
        return render(request, 'auth/login.html', {})

@login_required(login_url='/login')
def change_password(request):
    if request.method == 'POST':
        message_error = []
        message_success = None
        pass_old = request.POST.get('pass_old', '')
        pass_new = request.POST.get('pass_new', '')
        pass_new_repeat = request.POST.get('pass_new_repeat', '')
        if pass_old == '' or pass_new == '' or pass_new_repeat == '' :
            message_error.append('Trường yêu cầu không được bỏ trống!')
        else:
            if pass_new != pass_new_repeat :
                message_error.append('Mật khẩu  nhập lại không trùng khớp!')
            else:
                if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{6,}', pass_new):
                    # no match
                    if (request.user.check_password(pass_old)):
                        # request.user.update(password=make_password(pass_new))
                        UserCoop.objects.filter(id=request.user.id).update(password=make_password(pass_new))
                        message_success = 'success'
                    else:
                        message_error.append('Mật khẩu cũ chưa chính xác!')
                else:
                    message_error.append('Mật khẩu  không đúng định dạng yêu cầu!')

        return JsonResponse({
            'message_success' : message_success,
            'message_error' : message_error
        },safe=False)

##########Protected media file ####
@login_required()
def protected_media(request):
    response = HttpResponse(status=200)
    path = request.path
    if path.endswith('.jpg'):
        response['Content-Type'] = 'image/jpeg'
    elif path.endswith('.pdf'):
        response['Content-Type'] = 'application/pdf'
    ## /protectedMdedia la location config trong nginx
    url_path = '/protectedMedia' + request.path.split('/media')[1]
    response['X-Accel-Redirect'] = url_path
    return response
