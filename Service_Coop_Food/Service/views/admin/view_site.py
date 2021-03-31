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

class SiteView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request):
        list_site = Site.objects.all()
        page = self.request.GET.get('page')
        paginator = Paginator(list_site, settings.PAGINATOR_NUMBER)
        try:
            list_site = paginator.page(page)
        except PageNotAnInteger:
            list_site = paginator.page(1)
        except EmptyPage:
            list_site = paginator.page(paginator.num_pages)
        context = {
            'list_site': list_site
        }
        return render(request, 'admin/site.html', context)


class SiteAddView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request):
        form_add_site = SiteAddForm
        return render(request, 'admin/add_site.html', context={'form_add_site': form_add_site})

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request):
        form_add_site = SiteAddForm(request.POST)
        if form_add_site.is_valid():
            form_add_site.save()
            messages.success(request, 'Thêm mới thành công')
        else:
            print(form_add_site.errors)
            messages.error(request, 'Tên mô hình này đã tồn tại !')
            return redirect(reverse('admin_site_add'))
        return redirect(reverse('admin_site'))


class SiteEditView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request, id):
        form_edit_site = SiteEditForm(instance=Site.objects.get(id=id))
        context = {
            'form_edit_site': form_edit_site,
            'id': id
        }
        return render(request, 'admin/edit_site.html', context)

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request, id):
        site = Site.objects.get(id=id)
        form_edit_site = SiteEditForm(request.POST or None, instance=site)
        if form_edit_site.is_valid():
            name = form_edit_site.cleaned_data['name']
            if Site.objects.exclude(pk=id).filter(name = name).exists():
                messages.error(request, 'Tên mô hình này đã tồn tại trên hệ thống !')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                form_edit_site.save()
        else:
            messages.error(request, 'Tên mô hình không thể để trống !')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return redirect(reverse('admin_site'))


class SiteDeleteView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request, id):
        pass

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request, id):
        Site.objects.filter(id=id).delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))