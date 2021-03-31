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
from django.db import  connection
from Service.models import UserCoop, ListCus, Site
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

class DashBoardView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request):
        num_site = Site.objects.all().count()
        num_cus = ListCus.objects.all().count()
        num_user = UserCoop.objects.all().count()
        num_role = Role.objects.all().count()
        context = {
            'num_site': num_site,
            'num_cus': num_cus,
            'num_user': num_user,
            'num_role': num_role
        }
        return  render(request, 'admin/dashboard.html' , context)

    def post(self, request):
        pass
