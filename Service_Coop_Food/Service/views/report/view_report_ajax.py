from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect , Http404, JsonResponse
from Service.decorators import allowed_user,allowed_permission
from django.utils.decorators import method_decorator
import datetime
from Service.models import  *
from django.conf import settings
import os
from django.shortcuts import get_object_or_404
from django.db import  connection, connections, transaction
# Create your views here.

def update_other_status(request):
    if request.method == 'POST':
        message = request.POST.get('message', None)
        group_bill = request.POST.get('group_bill', None)
        cus_id = request.POST.get('cus_id', None)
        user_id = request.user.id
        ##Hủy hóa đơn => Chuyển other status lại N
        if message == 'cancle_report':
            other_status_update = 'N'
        ## Xác nhận xử lí xong biên bản
        elif message == 'excute_done':
            other_status_update = 'E'
        query = "UPDATE ["+str(cus_id)+"|bill] set status_other = '"+str(other_status_update)+"', last_change_date = getdate(), user_id_change = "+str(user_id)+" WHERE group_hd = '"+str(group_bill)+"'"
        query_log = "INSERT INTO "
        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(query)
                cur.execute("INSERT INTO ["+str(cus_id)+"|log_change_status] (other_status, date_change, user_id, listcus_id, type, group_hd) VALUES (N'"+str(other_status_update)+"', GETDATE(), "+str(user_id)+", "+str(cus_id)+", 3, "+str(group_bill)+") ")
        return JsonResponse({
            'message' : 'success'
        })