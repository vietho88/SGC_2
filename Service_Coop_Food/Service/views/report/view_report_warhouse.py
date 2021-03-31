from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,HttpResponseRedirect , Http404, HttpResponseForbidden
from Service.decorators import allowed_user,allowed_permission
from django.utils.decorators import method_decorator
from django.db import connection, transaction
import datetime
from Service.models import  *
from django.contrib import messages
from django.conf import settings
import os
from django.shortcuts import get_object_or_404
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import PermissionDenied


# Create your views here.

class ReportBillView(View):
    @method_decorator(allowed_permission(allowed_per='Xem biên bản'))
    def get(self, request, id_cus, id, index):
        is_created = False
        is_expired = None
        detail_report = ''
        result_check_report = ''
        list_per = request.user.role.role_permission.all().values_list('name', flat=True)
        request.session['list_per'] = list(list_per)

        ##If cus not in list_cus_manager => 403
        if int(id_cus) not in request.session['list_cus_manager'] and request.user.cus.ttpp != 1:
            raise Http404
        with connection.cursor() as cur:
            query = "SELECT tb1.status_id, isnull(tb1.status_other, '') as status_other, tb2.name, tb2.address, tb2.company_name , tb3.name as name_bill, tb3.symbol as symbol  \
                        ,tb1.listcus_id, tb1.group_hd, tb1.src_image\
                    FROM ["+str(id_cus)+"|bill] as tb1 INNER JOIN dbo.service_listcus as tb2 ON tb1.listcus_id = tb2.id   \
                    INNER JOIN dbo.service_statusbill as tb3 ON tb1.status_id = tb3.id \
                    WHERE group_hd = '"+str(id)+"' ORDER BY is_po"
            reports = cur.execute(query).fetchall()

        if not len(reports) :
            raise Http404

        src_images = [x.src_image for x in reports]
        report = reports[0]
        ##TH bien ban has created
        if report.status_other:
            try:
                detail_report = Report.objects.get(group_bill = id, cus_id = id_cus)
                result_check_report = Report_ResultCheck.objects.filter(report_id=detail_report.id)
                if (detail_report.created_at + timedelta(days=10)) <  timezone.now():
                    is_expired = 1
            except Exception as e:
                print(e)
                ##TH report đã có Trạng thái phụ nhưng chưa có Dữ liệu

        cus_ttpp = ListCus.objects.filter(ttpp = 1).values('id', 'name', 'store_number')
        date_now = datetime.datetime.now().strftime('%d/%m/%Y')
        if len(report):
            context = {
                'report' : report,
                'date_create' : date_now,
                'report_number' : 199999,
                'detail_report' : detail_report,
                'result_check_report' : result_check_report,
                'cus_ttpp' : cus_ttpp,
                'src_images' : src_images,
                'id_cus' : int(id_cus),
                'is_expired' : is_expired
            }
        else:
            raise Http404
        return render(request, 'report/warehouse_report.html', context = context)

    @method_decorator(allowed_permission(allowed_per='Sửa biên bản'))
    def post(self, request, id_cus, id, index):
        #create new
        ttpp_executes = request.POST.getlist('input-ttpp-execute[]', '')
        id_result_check = request.POST.getlist('input_id_detail[]', [])
        comment_ttpp = request.POST.get('text_area_ttpp', '')
        new_value_save_log = str(comment_ttpp) + str(id_result_check)
        user_id = request.user.id
        with transaction.atomic():
            edit_report = Report.objects.filter(group_bill=id, cus_id_id=id_cus).update(comment_ttpp = comment_ttpp)
            for index in range(len(id_result_check)):
                Report_ResultCheck.objects.filter(id = id_result_check[index]).update(solution = ttpp_executes[index])
            with connection.cursor() as cur:
                cur.execute("INSERT INTO [" + str(id_cus) + "|log_change_status] (listcus_id, user_id, type,  old_status, new_status, group_hd, date_change) \
                                                  VALUES (%s, %s, %s, %s, %s, %s,  GETDATE()) ",[id_cus, user_id, 3, 'old_value_report_str', new_value_save_log, id])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
