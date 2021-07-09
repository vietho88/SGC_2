from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from Service.decorators import allowed_user, allowed_permission
from django.utils.decorators import method_decorator
from Service.models import *
import json
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import datetime
from django.db import  connection
from django.http import Http404
from django.db.transaction import atomic
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import pdf2image
from PIL import Image


@csrf_exempt
def update_comment(request):
    if request.method == 'POST':
        user_cmt = request.user
        cus_id = request.user.cus_id
        cmt_text = str(request.POST['comment_text']).strip(" ")
        # print(request.headers['Referer'])
        if '/detail/' in request.headers['Referer'] :
            type = 1
            group_hd = request.POST['group_hd']
            comment_user.objects.create(user_created=user_cmt,comment_text= cmt_text,group_hd = group_hd,type=type)
            
        elif '/invoice_list_detail/' in request.headers['Referer']:
            type = 2
            group_hd = request.POST['image_name']
            comment_user.objects.create(user_created=user_cmt,comment_text= cmt_text,group_hd = group_hd,type=type)
        elif 'bill/report/' in request.headers['Referer'] :
            type = 3
            group_hd = request.POST['group_hd']
            comment_user.objects.create(user_created=user_cmt,comment_text= cmt_text,group_hd = group_hd,type=type)
        cmt_data = comment_user.objects.filter(group_hd=group_hd,type=type).values()
        data = {'data':list(cmt_data)}
        # a = request.POST.get('data_form', None)
        return JsonResponse(data)
    if request.method == 'GET':
        cmt_data = ''
        user_cmt = request.user
        cus_id = request.user.cus_id
        if '/detail/' in request.headers['Referer'] :
            type = 1
            group_hd = request.GET.get('group_hd')
        elif '/invoice_list_detail/' in request.headers['Referer'] :
            type = 2
            group_hd = request.GET.get('image_name')
        elif 'bill/report/' in request.headers['Referer'] :
            type = 3
            group_hd = request.GET.get('group_hd')
        cmt_data = comment_user.objects.filter(group_hd=group_hd,type=type).values()
        data = {'data':list(cmt_data)}
        return JsonResponse(data)