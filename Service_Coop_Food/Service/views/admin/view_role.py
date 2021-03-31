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
from django.conf import settings

class RoleView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request):
        find_site = Site.objects.all().values_list('id', flat=True)
        find_site = request.GET.getlist('select_site', find_site)
        list_role = Role.objects.filter(site__in=find_site).prefetch_related('role_permission').order_by('id')
        page = self.request.GET.get('page')
        paginator = Paginator(list_role, settings.PAGINATOR_NUMBER)
        try:
            list_role = paginator.page(page)
        except PageNotAnInteger:
            list_role = paginator.page(1)
        except EmptyPage:
            list_role = paginator.page(paginator.num_pages)
        context = {
            'list_role': list_role,
            'list_site': Site.objects.all(),
            'find_site': list(map(int, find_site))
        }
        return render(request, 'admin/role.html', context)

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request):
        pass


class RoleEditView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request, id):
        list_exchange_from_O = []
        list_exchange_from_S = []
        list_exchange_from_W = []
        list_exchange_from_A = []
        list_exchange_from_H = []
        list_exchange_from_R = []
        list_exchange_from_V = []
        list_exchange_from_M = []
        list_exchange_from_C = []
        role = Role.objects.filter(id=id).first()
        role_permission = RolePermission.objects.filter(role=id).values_list('permission', flat=True)
        role_permission_old = role.rolepermission_set.all().values_list('permission', flat=True)
        role_permission_old_type = role.rolepermission_set.all().values_list('permission__type', flat=True).distinct()
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
            elif recent.recent_status == 'H':
                try:
                    list_exchange_from_H = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_H = [recent.new_status]
            elif recent.recent_status == 'R':
                try:
                    list_exchange_from_R = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_R = [recent.new_status]
            elif recent.recent_status == 'V':
                try:
                    list_exchange_from_V = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_V = [recent.new_status]

            elif recent.recent_status == 'M':
                try:
                    list_exchange_from_M = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_M = [recent.new_status]
            elif recent.recent_status == 'C':
                try:
                    list_exchange_from_C = recent.new_status.split('|')
                except expression as identifier:
                    list_exchange_from_C = [recent.new_status]
        list_exchange_status = [
            [1, 'O'], [2, 'S'], [3, 'W'], [4, 'A'], [5, 'C'],
            [6, 'H'], [7, 'R'], [8, 'M'], [9, 'V'],
        ]
        context = {
            'role': role,
            'role_permission_old': role_permission_old,
            'role_permission_old_type': role_permission_old_type,
            'list_all_permission': list_all_permission,
            'list_exchange_status': list_exchange_status,
            'list_exchange_from_O': list_exchange_from_O,
            'list_exchange_from_S': list_exchange_from_S,
            'list_exchange_from_W': list_exchange_from_W,
            'list_exchange_from_A': list_exchange_from_A,
            'list_exchange_from_H': list_exchange_from_H,
            'list_exchange_from_R': list_exchange_from_R,
            'list_exchange_from_V': list_exchange_from_V,
            'list_exchange_from_M': list_exchange_from_M,
            'list_exchange_from_C': list_exchange_from_C
        }
        return render(request, 'admin/edit_role.html', context)

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request, id):
        list_per = request.POST.getlist('select_per_edit_role[]')
        list_exchange_o = request.POST.getlist('checkbox_change_o[]', [])
        list_exchange_s = request.POST.getlist('checkbox_change_s[]', [])
        list_exchange_w = request.POST.getlist('checkbox_change_w[]', [])
        list_exchange_a = request.POST.getlist('checkbox_change_a[]', [])
        list_exchange_h = request.POST.getlist('checkbox_change_h[]', [])
        list_exchange_r = request.POST.getlist('checkbox_change_r[]', [])
        list_exchange_v = request.POST.getlist('checkbox_change_v[]', [])
        list_exchange_m = request.POST.getlist('checkbox_change_m[]', [])
        list_exchange_c = request.POST.getlist('checkbox_change_c[]', [])
        role_name = request.POST.get('name_role', None)
        obj_role = Role.objects.get(id=id)

        if role_name is None:
            messages.error(request, 'Tên bộ phận không được để trống')
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        else:
            if Role.objects.filter(name = role_name).exclude(id = id).exists() :
                messages.error(request, 'Tên bộ phận này đã tồn tại')
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        with transaction.atomic():
            Role.objects.filter(id=id).update(name = role_name)
            update_per = obj_role.role_permission.set(list_per, clear=True)
            PermissionChangeStatus.objects.filter(role=id).delete()
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_o), role_id=id,
                                                            recent_status='O')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_s), role_id=id,
                                                            recent_status='S')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_w), role_id=id,
                                                            recent_status='W')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_a), role_id=id,
                                                            recent_status='A')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_h), role_id=id,
                                                            recent_status='H')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_r), role_id=id,
                                                            recent_status='R')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_v), role_id=id,
                                                            recent_status='V')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_m), role_id=id,
                                                            recent_status='M')
            PermissionChangeStatus.objects.update_or_create(new_status='|'.join(list_exchange_c), role_id=id,
                                                            recent_status='C')
            # PermissionChangeStatus.objects.filter(role=id, recent_status='O').update(new_status='|'.join(list_exchange_o))
        messages.success(request, 'Chỉnh sửa thành công !!')
        return HttpResponseRedirect(self.request.path_info)


class RoleAddView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request):
        list_exchange_status = [
            [1, 'O'], [2, 'S'], [3, 'W'], [4, 'A'], [5, 'C'],
            [6, 'H'], [7, 'R'], [8, 'M'], [9, 'V'],
        ]
        list_all_permission = Permission.objects.all()
        list_site = Site.objects.all()
        context = {
            'list_all_permission': list_all_permission,
            'list_exchange_status': list_exchange_status,
            'list_site': list_site
        }
        return render(request, 'admin/add_role.html', context)

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request):
        message_error = None
        message_success = None
        name_role = request.POST.get('name_role', None)
        site_id = request.POST.get('select_site', None)
        list_per = request.POST.getlist('select_per_edit_role[]', [])
        list_exchange_o = request.POST.getlist('checkbox_change_o[]', [])
        list_exchange_s = request.POST.getlist('checkbox_change_s[]', [])
        list_exchange_w = request.POST.getlist('checkbox_change_w[]', [])
        list_exchange_a = request.POST.getlist('checkbox_change_a[]', [])
        list_exchange_h = request.POST.getlist('checkbox_change_h[]', [])
        list_exchange_r = request.POST.getlist('checkbox_change_r[]', [])
        list_exchange_v = request.POST.getlist('checkbox_change_v[]', [])
        list_exchange_m = request.POST.getlist('checkbox_change_m[]', [])
        list_exchange_c = request.POST.getlist('checkbox_change_c[]', [])

        if name_role is None or list_per == []:
            message_error = 'Lỗi thiếu thông tin bắt buộc(Tên bộ phận hoặc quyền)'
        else:
            if Role.objects.filter(name__iexact=name_role, site_id=site_id).exists():
                message_error = 'Bộ phận này đã tồn tại trên hệ thống'
            else:
                with transaction.atomic():
                    site = Site.objects.get(id=site_id)
                    new_role = Role.objects.create(name=name_role, symbol='AA', site=site)
                    id = new_role.id
                    update_per = new_role.role_permission.set(list_per, clear=True)
                    PermissionChangeStatus.objects.filter(role=id).delete()
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_o), role_id=id,
                                                          recent_status='O')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_s), role_id=id,
                                                          recent_status='S')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_w), role_id=id,
                                                          recent_status='W')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_a), role_id=id,
                                                          recent_status='A')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_h), role_id=id,
                                                          recent_status='H')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_r), role_id=id,
                                                          recent_status='R')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_v), role_id=id,
                                                          recent_status='V')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_m), role_id=id,
                                                          recent_status='M')
                    PermissionChangeStatus.objects.create(new_status='|'.join(list_exchange_c), role_id=id,
                                                          recent_status='C')
                    # PermissionChangeStatus.objects.filter(role=id, recent_status='O').update(new_status='|'.join(list_exchange_o))
                    message_success = 'Thêm mới bộ phận mới thành công'
        context = {
            'message_error': message_error,
            'message_success': message_success
        }

        if message_error:
            messages.error(request, message_error)
            return redirect(reverse('admin_role_add'))
        if message_success:
            messages.success(request, message_success)
            return redirect(reverse('admin_role'))

