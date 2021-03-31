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



# Create your views here.
class IndexView(View):
    ##@method_decorator(allowed_user(allowed_roles=[1]))
    def get(self, request):
        return render(request, 'admin/dashboard.html')

    #@method_decorator(allowed_user(allowed_roles=[1]))
    def post(self, request):
        pass


class UserView(View):
    #@method_decorator(allowed_user(allowed_roles=[1]))
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

    #@method_decorator(allowed_user(allowed_roles=[1]))
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
    def get(self, request):
        form_add_user = UserCreateForm
        form_edit_user = UserEditForm
        context = {
            'form_add_user': form_add_user,
            'form_edit_user': form_edit_user
        }
        return render(request, 'admin/add_user.html', context)

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

        new_user = UserCoop.objects.create(
            username=username, password=make_password(password), email=email,
            phone_number=phone_number, cus_id=cus, role_id=role)
        manager_cus = ListCus.objects.filter(id__in=cus_manager)
        new_user.manager_cus.add(*manager_cus)
        return redirect(reverse('admin_user'))

class BranchAddView(View):
    #@method_decorator(allowed_user(allowed_roles=[1]))
    def get(self, request):
        form_add_branch = ListCusCreateForm
        context = {
            'form_add_branch': form_add_branch,
        }
        return  render(request, 'admin/add_branch.html' , context)

    def post(self, request):
        data_add = ListCusCreateForm(request.POST)
        if data_add.is_valid():
            with transaction.atomic():
                site = Site.objects.get(id=data_add.cleaned_data['site'])
                data = data_add.cleaned_data
                data.pop("site")
                new_cus = ListCus.objects.create(**data, site=site)
                create_table_cus(str(new_cus.id))
                return redirect(reverse('admin_branch'))

        else:
            print(data_add.errors)
            form_add_branch_error = ListCusCreateForm(initial=data_add.cleaned_data)
            return render(request, 'admin/add_branch.html', {
                'form_add_branch': form_add_branch_error,
                'message_error': data_add.errors
            })

class UserEditView(View):
    def get(self, request,id):
        user = UserCoop.objects.filter(pk=id).values()[0]
        form_edit_user = UserEditForm(initial=user)
        context = {
            'form_edit_user': form_edit_user,
            'id' : id
        }
        return render(request, 'admin/edit_user.html',context)
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

        UserCoop.objects.filter(pk=id).update(
            username=username, email=email,
            phone_number=phone_number, cus_id=cus, role_id=role)
        manager_cus = ListCus.objects.filter(id__in=cus_manager)
        edit_user = UserCoop.objects.get(pk=id)
        edit_user.manager_cus.add(*manager_cus)

        return redirect(reverse('admin_user'))


class BranchView(View):
    #@method_decorator(allowed_user(allowed_roles=[1]))
    def get(self, request):
        find_name_cus = ''
        find_site = [Site.objects.first().id]
        form_add_branch = ListCusCreateForm
        form_edit_branch = ListCusEditForm
        # list_cus = ListCus.objects.filter(site__in = find_site)
        list_site = Site.objects.all()
        if len(request.GET) > 1 or (len(request.GET) == 1 and request.GET.get('page','') == ''):
            find_name_cus = request.GET.get('input_search_branch','')
            find_site = request.GET.getlist('select_site')
            
        list_cus = ListCus.objects.filter(name__contains=find_name_cus,site__in = find_site)
        page_list_cus = Paginator(list_cus, 6)
        page_number = request.GET.get('page',1)
        page_return = page_list_cus.get_page(page_number)
        context = {
            'list_cus': page_return,
            'list_site': list_site,
            'name_search': find_name_cus,
            'find_site': list(map(int, find_site)),
            'form_add_branch' : form_add_branch,
            'form_edit_branch' : form_edit_branch,
            'message_success' : ''
        }
        return render(request, 'admin/branch.html', context)

    #@method_decorator(allowed_user(allowed_roles=[1]))
    def post(self, request):
        data_add = ListCusCreateForm(request.POST)
        if data_add.is_valid():
            site = Site.objects.get(id=data_add.cleaned_data['site'])
            data = data_add.cleaned_data
            data.pop("site")
            new_cus = ListCus.objects.create(**data, site=site)
            return redirect(reverse('admin_branch'))

        else:
            print(data_add.errors)
            form_add_branch_error = ListCusCreateForm(initial = data_add.cleaned_data)
            return render(request, 'admin/branch.html', {
                'form_add_branch' : form_add_branch_error,
                'message_error' : data_add.errors
            })


class BranchEditView(View):
    def get(self, request, id):
        # cus_id = request.GET.get('cus_id','')
        # if cus_id is not None:
        #     find_cus = ListCus.objects.filter(id=cus_id)
        #     if find_cus.exists():
        #         return JsonResponse({
        #             'message' : 'success',
        #             'data' : list(find_cus.values())
        #         },safe=False)
        # return JsonResponse({'message': 'error'}, safe=False)

        branch = ListCus.objects.filter(pk=id).values()[0]
        form_edit_branch = ListCusEditForm(initial = branch)
        context = {
            'form_edit_branch': form_edit_branch,
            'id_branch' : id
        }
        return  render(request, 'admin/edit_branch.html', context)

    def post(self, request, id):
        data_add = ListCusEditForm(request.POST)
        # cus_id = request.POST.get('input-diden-id')
        message_error = []
        if data_add.is_valid():
            name = data_add.cleaned_data['name']
            store_number = data_add.cleaned_data['store_number']

            current_cus = ListCus.objects.filter(id = id)
            edit_cus_name = ListCus.objects.filter(name = name)
            edit_cus_store = ListCus.objects.filter(store_number = store_number)

            if edit_cus_name.exists():
                if current_cus[0].name != edit_cus_name[0].name:
                    message_error.append('Chi nhánh này đã tồn tại !')
                    messages.error(request,'Chi nhánh này đã tồn tại !')

            if edit_cus_store.exists():
                if current_cus[0].store_number != edit_cus_store[0].store_number:
                    message_error.append('Mã cửa hàng này đã tồn tại !')
                    messages.error(request,'Mã cửa hàng này đã tồn tại !')

            if message_error:
                # return JsonResponse({'message_error' : message_error}, safe=False)
                return HttpResponseRedirect(self.request.path_info)
            else:
                cus_updated = current_cus.update( **data_add.cleaned_data)
                return redirect(reverse('admin_branch'))
            # return JsonResponse({
            #     'message_success' : 'Thay đổi thông tin chi nhánh thành công!',
            #     'new_data' : list(ListCus.objects.filter(id = id).values()),
            #     'id' : cus_updated
            # }, safe=False)

        else:
            messages.error(request,data_add.errors)
            message_error.append(data_add.errors)
            return JsonResponse({
                'message_error': message_error
            }, safe=False)


@csrf_exempt
@login_required(login_url='/login')
def reset_pass(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        id = request.POST.get('id')
        message_error = ''
        message_success = ''
        lock_status = None
        user = UserCoop.objects.filter(id=id)
        if user.exists():
            if message == 'reset':
                UserCoop.objects.filter(id=id).update(password=make_password('Saigoncoop'))
                message_success = 'Success'
            elif message == 'lock':
                old_lock_status = user[0].is_lock
                if old_lock_status :
                    user.update(is_lock = False)
                    lock_status = 0
                else:
                    user.update(is_lock = True)
                    lock_status = 1
                message_success ='Success'
        else:
            message_error = 'Error. Not find id!'

    return JsonResponse({
        'message_error' : message_error,
        'message_success' : message_success,
        'lock_status' : lock_status
    }, safe=False)

class PermissionView(View):
    def get(self, request):
        list_per = Permission.objects.all()
        page = self.request.GET.get('page')
        paginator = Paginator(list_per, 10)
        try:
            list_per = paginator.page(page)
        except PageNotAnInteger:
            list_per = paginator.page(1)
        except EmptyPage:
            list_per = paginator.page(paginator.num_pages)
        context = {
            'list_per' : list_per
        }
        return render(request, 'admin/permision.html', context)

    def post(self, request):
        message = request.POST.get('message','')
        message_error = ''
        message_success = ''
        new_per = None
        name_per = None
        if message == 'add':
            name_per = request.POST.get('name-per','')
            if name_per and Permission.objects.filter(name=name_per).exists() == False:
                new_per = Permission.objects.create(name=name_per).id
                message_success = 'success'
            elif name_per and Permission.objects.filter(name=name_per).exists() == True:
                message_error = 'Tên phân quyền chức năng này đã tồn tại!'
            else:
                message_error = 'Bạn chưa điền tên phân quyền mới!'
        elif message == 'edit':
            name_per = request.POST.get('name-per-edit','')
            id_per = request.POST.get('id_per')
            if name_per and Permission.objects.filter(name=name_per).exclude(id=id_per).exists() == False:
                new_per = Permission.objects.filter(id=id_per).update(name=name_per)
                message_success = 'success'
            elif name_per and Permission.objects.filter(name=name_per).exclude(id=id_per).exists():
                message_error = 'Tên phân quyền chức năng này đã tồn tại!'
            else:
                message_error = 'Tên phân quyền mới đang bị trống!'
        elif message == 'delete':
            id_per = request.POST.get('id_per')
            if id_per:
                with transaction.atomic():
                    Permission.objects.filter(id=id_per).delete()
                    message_success = 'Xóa thành công!'     
        return JsonResponse({
                'message_error' : message_error,
                'message_success' : message_success,
                'new_per_id' : new_per,
                'name_per' : name_per
            },safe=False)
class RoleView(View):
    def get(self, request):
        find_site = Site.objects.all().values_list('id', flat=True)
        find_site = request.GET.getlist('select_site', find_site)
        list_role = Role.objects.filter(site__in=find_site).order_by('id')
        page = self.request.GET.get('page')
        paginator = Paginator(list_role, 10)
        try:
            list_role = paginator.page(page)
        except PageNotAnInteger:
            list_role = paginator.page(1)
        except EmptyPage:
            list_role = paginator.page(paginator.num_pages)
        context = {
            'list_role' : list_role,
            'list_site' : Site.objects.all(),
            'find_site' : list(map(int,find_site))
        }
        return render(request, 'admin/role.html', context)

    def post(self, request):
        pass

class RoleEditView(View):
    def get(self, request, id):
        list_exchange_from_O = []
        list_exchange_from_S = []
        list_exchange_from_W = []
        list_exchange_from_A = []
        list_exchange_from_R = []
        list_exchange_from_F = []
        list_exchange_from_C = []
        role = Role.objects.filter(id=id).first()
        role_permission = RolePermission.objects.filter(role=id).values_list('permission',flat=True)
        role_permission_old = role.rolepermission_set.all().values_list('permission',flat=True)
        print('role_permission_old')
        print(role_permission_old)
        print(role_permission)
        list_all_permission = Permission.objects.all()
        list_recent_exchange = PermissionChangeStatus.objects.filter(role=id)
        for recent in list_recent_exchange:
            if recent.recent_status == 'O':
                try:
                    list_exchange_from_O = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_O = [recent.new_status]
            elif recent.recent_status == 'S':
                try:
                    list_exchange_from_S = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_S = [recent.new_status]
            elif recent.recent_status == 'W':
                try:
                    list_exchange_from_W = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_W = [recent.new_status]
            elif recent.recent_status == 'A':
                try:
                    list_exchange_from_A = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_A = [recent.new_status]
            elif recent.recent_status == 'R':
                try:
                    list_exchange_from_R = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_R = [recent.new_status]
            
            elif recent.recent_status == 'F':
                try:
                    list_exchange_from_F = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_F = [recent.new_status]
            elif recent.recent_status == 'C':
                try:
                    list_exchange_from_C = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_C = [recent.new_status]
        list_exchange_status = [
            [1, 'O'],[2, 'S'],[3, 'W'],[4, 'A'],
            [5, 'R'],[6, 'F'],[7, 'C'],
        ]
        print(list_exchange_from_O)
        context = {
            'role' : role,
            'role_permission_old' : role_permission_old,
            'list_all_permission' : list_all_permission,
            'list_exchange_status' : list_exchange_status,
            'list_exchange_from_O' : list_exchange_from_O,
            'list_exchange_from_S' : list_exchange_from_S,
            'list_exchange_from_W' : list_exchange_from_W,
            'list_exchange_from_A' : list_exchange_from_A,
            'list_exchange_from_R' : list_exchange_from_R,
            'list_exchange_from_F' : list_exchange_from_F,
            'list_exchange_from_C' : list_exchange_from_C
        }
        return render(request, 'admin/edit_role.html', context)

    def post(self, request, id):
        list_per = request.POST.getlist('select_per_edit_role[]')
        list_exchange_o = request.POST.getlist('checkbox_change_o[]',[])
        list_exchange_s = request.POST.getlist('checkbox_change_s[]',[])
        list_exchange_w = request.POST.getlist('checkbox_change_w[]',[])
        list_exchange_a = request.POST.getlist('checkbox_change_a[]',[])
        list_exchange_r = request.POST.getlist('checkbox_change_r[]',[])
        list_exchange_f = request.POST.getlist('checkbox_change_f[]',[])
        list_exchange_c = request.POST.getlist('checkbox_change_c[]',[])
        obj_role = Role.objects.get(id =id)

        with transaction.atomic():
            update_per= obj_role.role_permission.set(list_per, clear=True)
            PermissionChangeStatus.objects.filter(role=id).delete()
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_o),role_id=id, recent_status='O')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_s),role_id=id, recent_status='S')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_w),role_id=id, recent_status='W')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_a),role_id=id, recent_status='A')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_r),role_id=id, recent_status='R')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_f),role_id=id, recent_status='F')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_c),role_id=id, recent_status='C')
            # PermissionChangeStatus.objects.filter(role=id, recent_status='O').update(new_status='|'.join(list_exchange_o))
        return HttpResponseRedirect(self.request.path_info)

class RoleAddView(View):
    def get(self, request):
        list_exchange_status = [
            [1, 'O'],[2, 'S'],[3, 'W'],[4, 'A'],
            [5, 'H'],[6, 'R'],[7, 'F'],[8, 'C'],
        ]
        list_all_permission = Permission.objects.all()
        list_site = Site.objects.all()
        context = {
            'list_all_permission' : list_all_permission,
            'list_exchange_status' :list_exchange_status,
            'list_site' : list_site
        }
        return render(request, 'admin/add_role.html' ,context)

    def post(self, request):
        message_error = None
        message_success = None
        name_role = request.POST.get('name_role', None)
        site_id = request.POST.get('select_site', None)
        list_per = request.POST.getlist('select_per_edit_role[]', [])
        list_exchange_o = request.POST.getlist('checkbox_change_o[]',[])
        list_exchange_s = request.POST.getlist('checkbox_change_s[]',[])
        list_exchange_w = request.POST.getlist('checkbox_change_w[]',[])
        list_exchange_a = request.POST.getlist('checkbox_change_a[]',[])
        list_exchange_h = request.POST.getlist('checkbox_change_h[]',[])
        list_exchange_r = request.POST.getlist('checkbox_change_r[]',[])
        list_exchange_f = request.POST.getlist('checkbox_change_f[]',[])
        list_exchange_c = request.POST.getlist('checkbox_change_c[]',[])

        if name_role is None or list_per == []:
            message_error = 'Lỗi thiếu thông tin bắt buộc(Tên bộ phận hoặc quyền)'
        else:
            if Role.objects.filter(name__iexact = name_role,site_id=site_id).exists():
                message_error = 'Bộ phận này đã tồn tại trên hệ thống'
            else:
                with transaction.atomic():
                    site = Site.objects.get(id=site_id)
                    new_role = Role.objects.create(name=name_role, symbol='AA', site= site)
                    id = new_role.id
                    update_per= new_role.role_permission.set(list_per, clear=True)
                    PermissionChangeStatus.objects.filter(role=id).delete()
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_o),role_id=id, recent_status='O')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_s),role_id=id, recent_status='S')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_w),role_id=id, recent_status='W')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_a),role_id=id, recent_status='A')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_h),role_id=id, recent_status='H')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_r),role_id=id, recent_status='R')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_f),role_id=id, recent_status='F')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_c),role_id=id, recent_status='C')
                    # PermissionChangeStatus.objects.filter(role=id, recent_status='O').update(new_status='|'.join(list_exchange_o))
                    message_success = 'Thêm mới bộ phận mới thành công'
        context = {
            'message_error': message_error,
            'message_success' : message_success
        }

        if message_error:
            messages.error(request, message_error)
            return redirect(reverse('admin_role_add'))
        if message_success:
            messages.success(request, message_success)
            return redirect(reverse('admin_role'))


class SiteView(View):
    def get(self, request):
        list_site = Site.objects.all()
        page = self.request.GET.get('page')
        paginator = Paginator(list_site, 10)
        try:
            list_site = paginator.page(page)
        except PageNotAnInteger:
            list_site = paginator.page(1)
        except EmptyPage:
            list_site = paginator.page(paginator.num_pages)
        context = {
            'list_site' : list_site
        }
        return render(request, 'admin/site.html', context)

    

class SiteAddView(View):
    def get(self, request):
        form_add_site = SiteAddForm
        return render(request, 'admin/add_site.html', context={'form_add_site': form_add_site})

    def post(self, request):
        form_add_site = SiteAddForm(request.POST)
        if form_add_site.is_valid():
            form_add_site.save()
            messages.success(request, 'Thêm mới một site thành công')
        else:
            print(form_add_site.errors)
            messages.error(request,'Tên site đã tồn tại')
            return redirect(reverse('admin_site_add'))
        return redirect(reverse('admin_site_add'))

class SiteEditView(View):
    def get(self, request, id):
        form_edit_site = SiteAddForm(instance=Site.objects.get(id=id))
        context={
            'form_edit_site':form_edit_site,
            'id' : id
        }
        return render(request, 'admin/edit_site.html', context)

    def post(self, request,id):
        form_edit_site = SiteAddForm(request.POST, instance=Site.objects.get(id=id))
        if form_edit_site.is_valid():
            form_edit_site.save()
        else:
            messages.error(request, 'Có lỗi gì đó đã xảy ra')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return redirect(reverse('admin_site'))


class SiteDeleteView(View):
    def get(self, request, id):
        pass

    def post(self, request, id):
        Site.objects.filter(id=id).delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class TypeProductListView(ListView):

    model = TypeProduct
    template_name = 'admin/type_product.html'
    context_object_name = 'books'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(TypeProductListView, self).get_context_data(**kwargs)
        books = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(books, self.paginate_by)
        try:
            books = paginator.page(page)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        context['books'] = books
        return context

class TypeProductCreateView(CreateView):
    model = TypeProduct
    template_name = 'admin/add_type_product.html'
    fields = '__all__'
    success_url = reverse_lazy('admin_type_product')


class TypeProductUpdateView(UpdateView):

    model = TypeProduct
    template_name = 'admin/edit_type_product.html'
    context_object_name = 'book'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('admin_type_product')

class TypeProductDeleteView(DeleteView):
    model = TypeProduct
    template_name = 'admin/delete_type_product.html'
    success_url = reverse_lazy('admin_type_product')


def create_table_cus(id_cus):
    query_create_table_ife = 'CREATE TABLE [dbo].['+id_cus+'|bill](                                        \
        [id] [int] IDENTITY(1,1) NOT NULL,                                        \
        [listcus_id] [int] NOT NULL,                                        \
        [status_id] [int] NOT NULL,                                        \
        [type_product_id] [int] NULL,                                        \
        [group_hd] [nvarchar](20) NOT NULL,                                        \
        [image_name] [nvarchar](100) NOT NULL,                                        \
        [po_number] [nvarchar](20) NULL,                                        \
        [vendor_number] [nvarchar](20) NULL,                                        \
        [receiver_number] [nvarchar](20) NULL,                                        \
        [sum_po] [nvarchar](20) NULL,                                        \
        [tax_number] [nvarchar](20) NULL,                                        \
        [symbol] [nvarchar](5) NULL,                                        \
        [bill_number] [nvarchar](20) NULL,                                        \
        [city_name] [nvarchar](max) NULL,                                        \
        [city_address] [nvarchar](max) NULL,                                        \
        [status_other] [nvarchar](5) NULL,                                        \
        [bill_date] [datetime] NULL,                                        \
        [ket_thuc_dot_number] [int] NULL,                                        \
        [user_id_up] [int] NOT NULL,                                        \
        [user_id_change] [int] NULL,                                        \
        [upload_date] [datetime] NOT NULL,                                        \
        [kt_comment] [nvarchar](max) NULL,                                        \
        [ttpp_comment] [nvarchar](max) NULL,                                        \
        [result_check] [nvarchar](max) NULL,                                        \
        [result_check_luoi] [nvarchar](max) NULL,                                        \
        [check_trung] [nvarchar](max) NULL,                                        \
        [is_qa] [tinyint] NULL,                                        \
        [is_po] [tinyint] NULL,                                        \
        [is_hddt] [tinyint] NULL,                                        \
        [is_ttpp] [tinyint] NULL,                                        \
        [is_rpa] [tinyint] NULL,                                        \
        [has_report] [tinyint] NULL,                                        \
        [src_image] [nvarchar](max) NULL,                                        \
        [src_pdf] [nvarchar](max) NULL,                                        \
        [src_xml] [nvarchar](max) NULL,                                        \
        [src_receiver] [nvarchar](max) NULL,                                        \
         CONSTRAINT [PK_'+id_cus+'|bill] PRIMARY KEY CLUSTERED                                         \
        (                                        \
            [id] ASC                                        \
        )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]                                        \
        ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]'
    query_create_table_log = 'CREATE TABLE [dbo].['+id_cus+'|log_change_status](                                        \
        [id] [int] IDENTITY(1,1) NOT NULL,                                        \
        [listcus_id] [int] NOT NULL,                                        \
        [user_id] [int] NOT NULL,                                        \
        [type] [nvarchar](50) NULL,                                        \
        [old_status] [nvarchar](10) NULL,                                        \
        [new_status] [nvarchar](10) NULL,                                        \
        [date_change] [datetime] NULL,                                        \
         CONSTRAINT [PK_'+id_cus+'|log_change_status] PRIMARY KEY CLUSTERED                                         \
        (                                        \
            [id] ASC                                        \
        )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]                                        \
        ) ON [PRIMARY]'
    query_create_table_bk = 'CREATE TABLE [dbo].['+id_cus+'|bk](                                        \
        [id] [int] IDENTITY(1,1) NOT NULL,                                        \
        [image_name] [nvarchar](100) NULL,                                        \
        [type_bk] [nvarchar](20) NULL,                                        \
        [bk_number] [nvarchar](20) NULL,                                        \
        [po_number] [nvarchar](20) NULL,                                        \
        [receiver_number] [nvarchar](20) NULL,                                        \
        [vendor_number] [nvarchar](20) NULL,                                        \
        [is_qa] [nchar](10) NULL,                                        \
        [user_id_up] [int] NOT NULL,                                        \
        [user_id_change] [int] NULL,                                        \
         CONSTRAINT [PK_'+id_cus+'|bk] PRIMARY KEY CLUSTERED                                         \
        (                                        \
            [id] ASC                                        \
        )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]                                        \
        ) ON [PRIMARY]'
    with connection.cursor() as cur:
        cur.execute(query_create_table_ife)
        cur.execute(query_create_table_log)
        cur.execute(query_create_table_bk)