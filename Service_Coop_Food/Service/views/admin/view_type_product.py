from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from Service.decorators import allowed_user
from django.utils.decorators import method_decorator
from Service.models import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings


class TypeProductListView(ListView):

    model = TypeProduct
    template_name = 'admin/type_product.html'
    context_object_name = 'books'
    paginate_by = settings.PAGINATOR_NUMBER

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
