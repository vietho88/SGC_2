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


class PermissionView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request):
        list_per = Permission.objects.all().order_by('type')
        page = self.request.GET.get('page')
        paginator = Paginator(list_per, settings.PAGINATOR_NUMBER)
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

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
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