from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from Service.decorators import allowed_user
from django.utils.decorators import method_decorator
from Service.models import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from Service.forms import *
from django.urls import reverse
import  json
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import  connection
from django.contrib.auth.decorators import user_passes_test


class UserView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request):
        find_cus = 'Tất cả chi nhánh'
        find_name = ''
        find_site = Site.objects.first().id
        find_role = Role.objects.filter(site=find_site).values_list('id', flat=True)
        list_user = UserCoop.objects.all()
        form_add_user = UserCreateForm
        form_edit_user = UserEditForm

        if len(request.GET) > 1 or (len(request.GET) ==1 and  request.GET.get('page','') ==''):
            find_cus = request.GET.get('select_branch_filter_admin')
            find_role = request.GET.getlist('select_role_filter_admin')
            find_name = request.GET.get('input_search_user')
            find_site = request.GET.get('select_site')
            if find_cus == 'all':
                list_user = UserCoop.objects.filter(role__in=find_role, username__contains=find_name)
            else:
                list_user = UserCoop.objects.filter(role__in=find_role, cus=find_cus, username__contains=find_name)
                find_cus = int(find_cus)

        list_site = Site.objects.all()
        list_role = Role.objects.filter(site=list_site[0].id)
        list_cus = ListCus.objects.filter(site=list_site[0].id)
        page_list_user = Paginator(list_user, 10)
        page_number = request.GET.get('page')
        page_return = page_list_user.get_page(page_number)
        context = {
            'list_user' : page_return,
            'cus_chosed' : find_cus,
            'role_chosed' : [int(x) for x in find_role],
            'site_chosed' : find_site,
            'list_cus' : list_cus,
            'list_site' : list_site,
            'list_role' : list_role,
            'name_search' : find_name,
            'form_add_user' : form_add_user,
            'form_edit_user' : form_edit_user
        }
        return render(request, 'admin/user.html', context)

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request):
        ###Add new user###
        message_error = []
        data_add_user = UserCreateForm(request.POST)

        role = request.POST.get('role','')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')
        phone_number = request.POST.get('phone_number', '')
        cus = request.POST.get('cus', '')
        type_ttpp = request.POST.get('type_ttpp', '')
        cus_manager = request.POST.getlist('cus_manager', [])
        print(cus_manager)

        if username == '':
            message_error.append('Tên người dùng không được phép trống')
        if UserCoop.objects.filter(username=username).exists():
            message_error.append('Tên người dùng này đã tồn tại trên hệ thống')
        if email == '':
            message_error.append('Email là trường nhập bắt buộc')
        else:
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if re.search(regex, email) == False:
                message_error.append('Email Không đúng định dạng')
        if phone_number == '':
            message_error.append('Số điện thoại là trường nhập bắt buộc')
        if password == '':
            message_error.append('Mật khẩu  là trường nhập bắt buộc')

        if role == 6 and type_ttpp == '' : ##Validate for TTPP
            message_error.append('Loại TTPP  là trường nhập bắt buộc')
        if role == 5 and cus_manager == [] : ##Validate for TTPP
            message_error.append('Loại TTPP  là trường nhập bắt buộc')

        if message_error:
            return JsonResponse({
                'message_error': message_error
            }, safe=True)

        if role == 6:
            new_user = UserCoop.objects.create(
                username=username, password=make_password(password), email=email,
                phone_number=phone_number, type_ttpp=type_ttpp, cus_id=1,
                role_id=role)
        elif role == 5:
            new_user = UserCoop.objects.create(
                username=username, password=make_password(password), email=email,
                phone_number=phone_number, cus_id=1, cus_manager=','.join(cus_manager),
                role_id=role)
        else:
            new_user = UserCoop.objects.create(
                username=username, password=make_password(password), email=email,
                phone_number=phone_number, cus_id=cus, role_id=role)
        print(new_user)
        return JsonResponse({
            'message_success' : 'oke'
        }, safe=True)

class UserAddView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request):
        form_add_user = UserCreateForm
        form_edit_user = UserEditForm
        context = {
            'form_add_user': form_add_user,
            'form_edit_user': form_edit_user
        }
        return render(request, 'admin/add_user.html', context)

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request):
        ###Add new user###
        message_error = []
        data_add_user = UserCreateForm(request.POST)

        role = request.POST.get('role','')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')
        phone_number = request.POST.get('phone_number', '')
        cus = request.POST.get('cus', '')
        type_ttpp = request.POST.get('type_ttpp', '')
        cus_manager = request.POST.getlist('cus_manager', [])
        role_symbol = Role.objects.get(id=role).symbol
        print(cus_manager)

        if username == '':
            message_error.append('Tên người dùng không được phép trống')
            messages.error(request, 'Tên người dùng không được phép trống')
        if UserCoop.objects.filter(username=username).exists():
            message_error.append('Tên người dùng này đã tồn tại trên hệ thống')
            messages.error(request, 'Tên người dùng này đã tồn tại trên hệ thống')
        if email == '':
            message_error.append('Email là trường nhập bắt buộc')
            messages.error(request, 'Email là trường nhập bắt buộc')
        else:
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if re.search(regex, email) == False:
                message_error.append('Email Không đúng định dạng')
                messages.error(request, 'Email Không đúng định dạng')
        if phone_number == '':
            message_error.append('Số điện thoại là trường nhập bắt buộc')
            messages.error(request, 'Số điện thoại là trường nhập bắt buộc')
        if password == '':
            message_error.append('Mật khẩu  là trường nhập bắt buộc')
            messages.error(request, 'Mật khẩu  là trường nhập bắt buộc')
        if role_symbol == 'TTPP' and type_ttpp == '' : ##Validate for TTPP
            message_error.append('Loại TTPP  là trường nhập bắt buộc')
            messages.error(request, 'Loại TTPP  là trường nhập bắt buộc')
        if cus == '' and cus_manager == [] : ##Validate for TTPP
            message_error.append('Loại TTPP  là trường nhập bắt buộc')
            messages.error(request, 'Loại TTPP  là trường nhập bắt buộc')

        if message_error:
            return redirect(reverse('admin_user_add'))

        if role_symbol == 'TTPP':
            new_user = UserCoop.objects.create(
                username=username, password=make_password(password), email=email,
                phone_number=phone_number, type_ttpp=type_ttpp, cus_id=1,
                role_id=role)
        else:
            new_user = UserCoop.objects.create(
                username=username, password=make_password(password), email=email,
                phone_number=phone_number, cus_id=cus, role_id=role)
            manager_cus = ListCus.objects.filter(id__in=cus_manager)
            new_user.manager_cus.add(*manager_cus)
        print(new_user)
        return redirect(reverse('admin_user'))


class UserEditView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request,id):
        user = UserCoop.objects.filter(pk=id).values()[0]
        form_edit_user = UserEditForm(initial=user)
        context = {
            'form_edit_user': form_edit_user,
            'id' : id
        }
        return render(request, 'admin/edit_user.html',context)

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request, id):
        message_error = []
        data_add_user = UserEditForm(request.POST)

        role = request.POST.get('role', '')
        username = request.POST.get('username', '')
        # password = request.POST.get('password', '')
        email = request.POST.get('email', '')
        phone_number = request.POST.get('phone_number', '')
        cus = request.POST.get('cus', '')
        type_ttpp = request.POST.get('type_ttpp', '')
        cus_manager = request.POST.getlist('cus_manager', [])
        role_symbol = Role.objects.get(id=role).symbol
        print(role_symbol)

        if username == '':
            message_error.append('Tên người dùng không được phép trống')
            messages.error(request, 'Tên người dùng không được phép trống')
        if UserCoop.objects.filter(username=username).exclude(pk=id).exists():
            message_error.append('Tên người dùng này đã tồn tại trên hệ thống')
            messages.error(request, 'Tên người dùng này đã tồn tại trên hệ thống')
        if email == '':
            message_error.append('Email là trường nhập bắt buộc')
            messages.error(request, 'Email là trường nhập bắt buộc')
        else:
            regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if re.search(regex, email) == False:
                message_error.append('Email Không đúng định dạng')
                messages.error(request, 'Email Không đúng định dạng')
        if phone_number == '':
            message_error.append('Số điện thoại là trường nhập bắt buộc')
            messages.error(request, 'Số điện thoại là trường nhập bắt buộc')
        if role_symbol == 'TTPP' and type_ttpp == '':  ##Validate for TTPP
            message_error.append('Loại TTPP  là trường nhập bắt buộc')
            messages.error(request, 'Loại TTPP  là trường nhập bắt buộc')
        if cus == '' and cus_manager == []:  ##Validate for TTPP
            message_error.append('Loại TTPP  là trường nhập bắt buộc')
            messages.error(request, 'Loại TTPP  là trường nhập bắt buộc')

        if message_error:
            return redirect(reverse('admin_user_add'))

        if role_symbol == 'TTPP':
            edit_user = UserCoop.objects.filter(pk=id).update(
                username=username, email=email,
                phone_number=phone_number, type_ttpp=type_ttpp, cus_id=1,
                role_id=role)
        else:
            UserCoop.objects.filter(pk=id).update(
                username=username, email=email,
                phone_number=phone_number, cus_id=cus, role_id=role)
            manager_cus = ListCus.objects.filter(id__in=cus_manager)
            edit_user = UserCoop.objects.get(pk=id)
            edit_user.manager_cus.add(*manager_cus)

        return redirect(reverse('admin_user'))

