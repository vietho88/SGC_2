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
import pyqrcode
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
        return render(request, 'report/base_report.html', context = context)

    @method_decorator(allowed_permission(allowed_per='Sửa biên bản'))
    def post(self, request, id_cus, id, index):
        #create new
        number_report = request.POST.get('input-report-number', '')
        number_xe = request.POST.get('input-so-xe', '')
        bill_numbers = request.POST.getlist('input-bill_number[]', '')
        product_codes = request.POST.getlist('input-product-code[]', '')
        product_names = request.POST.getlist('input-product-name[]', '')
        product_units = request.POST.getlist('input-product-unit[]', '')
        product_amounts = request.POST.getlist('input-product-amount[]', '')
        status_bills = request.POST.getlist('input-status-bill[]', '')
        comment_create = request.POST.get('text_area_create', '')
        ttpp_cus = request.POST.get('select-ttpp', '')
        user_id = request.user.id
        with transaction.atomic():
            new_report = Report.objects.create(group_bill = id, drive_number = number_xe, comment_create = comment_create,
                                               number = 400000, user_id_create_id = request.user.id, cus_id_id = id_cus, cus_ttpp_id = ttpp_cus)
            new_report_id = new_report.id
            list_add_result = []
            for index in range(len(bill_numbers)):
                Report_ResultCheck.objects.create(report_id=str(new_report_id),
                                                  bill_number = str(bill_numbers[index]),
                                                  sku=str(product_codes[index]),
                                                  name=str(product_names[index]),
                                                  quanty=str(product_amounts[index]),
                                                  unit=str(product_units[index]),
                                                  status=str(status_bills[index]))
            with connection.cursor() as cur:
                cur.execute("UPDATE ["+str(id_cus)+"|bill] set status_other = 'N', has_report = 1, last_change_date = GETDATE(), report_number = "+str(new_report_id + 400000)+", user_id_change = "+str(user_id)+" where group_hd = '"+str(id)+"'")
                cur.execute("INSERT INTO ["+str(id_cus)+"|log_change_status] (other_status, date_change, user_id, listcus_id, type, group_hd) VALUES (N'N', GETDATE(), "+str(user_id)+", "+str(id_cus)+", 3, "+str(id)+") ")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class PrintReportPDFView(View):
    @method_decorator(allowed_permission(allowed_per='In biên bản'))
    def get(self, request, id_cus, group):
        user_id = request.user.id
        list_manager_cus = request.session['list_cus_manager']
        if 'Tạo biên bản' not in request.session['list_per'] or int(id_cus) not in list_manager_cus:
            raise PermissionDenied
        with connection.cursor() as cur:
            query = "SELECT tb1.status_id, isnull(tb1.status_other, '') as status_other, tb1.report_number, tb2.name, tb2.address, tb2.company_name , tb3.name as name_bill, tb3.symbol as symbol  \
                                    ,tb1.listcus_id, tb1.group_hd\
                                FROM [" + str(id_cus) + "|bill] as tb1 INNER JOIN dbo.service_listcus as tb2 ON tb1.listcus_id = tb2.id   \
                                INNER JOIN dbo.service_statusbill as tb3 ON tb1.status_id = tb3.id \
                                WHERE group_hd = '" + str(group) + "'"
            print_report = cur.execute(query).fetchone()


        if print_report is None:
            messages.error(request, 'Lỗi')
            return HttpResponseRedirect(request.META.get('HTTTP_REFERER'))

        if print_report.status_other == '':
            messages.error(request, 'Biên bản chưa được tạo lập!!')
            return HttpResponseRedirect(request.META.get('HTTTP_REFERER'))
        else:
            forder_path_qr = settings.PATH_IMGAGEQR_REPORT + '/' + group[2:7]
            if not os.path.exists(forder_path_qr):
                os.makedirs(forder_path_qr)
            report = Report.objects.filter(cus_id = id_cus, group_bill = group).first()
            date_report = report.created_at.strftime('%Y%m%d')
            value_qr = "sgcoop|" + str(id_cus) + "|bienban|" + str(group) + "_" + date_report + "|" + str(print_report.report_number if int(print_report.report_number) < 400000   else report.id+400000)
            # big_code = pyqrcode.create(value_qr)
            # big_code.png(path_image_qr, scale=3.5)
            detail_print_report = Report.objects.filter(group_bill=group, cus_id=id_cus).first()
            result_check_print_report = Report_ResultCheck.objects.filter(report_id=detail_print_report.id)
            if print_report.status_other == 'N' :
                with connection.cursor() as cur:
                    cur.execute("UPDATE [" + str(id_cus) + "|bill] set status_other = 'P', last_change_date = GETDATE(), user_id_change = " + str(user_id) + " where group_hd = '" + str(group) + "'").commit()
                    cur.execute("INSERT INTO [" + str(id_cus) + "|log_change_status] (other_status, date_change, user_id, listcus_id, type, group_hd) VALUES (N'P', GETDATE(), " + str(user_id) + ", " + str(id_cus) + ", 3, "+str(group)+") ").commit()

        context = {
            'print_report' : print_report,
            'detail_print_report' : detail_print_report,
            'result_check_print_report' : result_check_print_report,
            'value_qr' : value_qr
        }
        return render(request, 'report/print_report.html', context)

    # #@method_decorator(allowed_user(allowed_roles=[1]))
    def post(self, request, id_cus, group):
        pass

class ReportEditView(View):
    @method_decorator(allowed_permission(allowed_per='Sửa biên bản'))
    def post(self, request, id_cus, id, index):
        #create new
        number_report = request.POST.get('input-report-number', '')
        number_xe = request.POST.get('input-so-xe', '')
        bill_numbers = request.POST.getlist('input-bill_number[]', '')
        product_codes = request.POST.getlist('input-product-code[]', '')
        product_names = request.POST.getlist('input-product-name[]', '')
        product_units = request.POST.getlist('input-product-unit[]', '')
        product_amounts = request.POST.getlist('input-product-amount[]', '')
        status_bills = request.POST.getlist('input-status-bill[]', '')
        ttpp_executes = request.POST.getlist('input-ttpp-execute[]', '')
        comment_create = request.POST.get('text_area_create', '')
        comment_ttpp = request.POST.get('text_area_ttpp', '')
        ttpp_cus = request.POST.get('select-ttpp', '')
        user_id = request.user.id

        ##select old value
        with connection.cursor() as cur:
            old_value_report = list(Report.objects.filter(group_bill = id).values_list('drive_number', 'cus_ttpp_id', 'comment_create', 'comment_ttpp')[0])
        old_value_report_str = '❥'.join(map(str,old_value_report))
        new_value_save_log = '❥'.join([str(number_xe), str(ttpp_cus) , str(comment_create), str(comment_ttpp)])
        if request.user.cus.ttpp == 1:
            with transaction.atomic():                
                edit_report = Report.objects.filter(group_bill=id, cus_id_id=id_cus).update(comment_ttpp = comment_ttpp)
                id_edit_report = Report.objects.get(group_bill =id,cus_id_id = id_cus).id
                edit_report_cmt = Report_ResultCheck.objects.filter(report_id=id_edit_report).values_list('id',flat=True)
                for idx,value_id in enumerate(edit_report_cmt):
                        Report_ResultCheck.objects.filter(id=value_id).update(solution = ttpp_executes[idx])
                with connection.cursor() as cur:
                    cur.execute("INSERT INTO [" + str(id_cus) + "|log_change_status] (listcus_id, user_id, type,  old_status, new_status, group_hd, date_change) \
                                  VALUES (%s, %s, %s, %s, %s, %s,  GETDATE()) ", [id_cus, user_id, 3, old_value_report_str, new_value_save_log ,id])
        else:
            with transaction.atomic():
                edit_report = Report.objects.filter(group_bill =id,cus_id_id = id_cus).update(group_bill = id, drive_number = number_xe, comment_create = comment_create,
                                                    user_id_create_id = request.user.id, cus_id_id = id_cus, cus_ttpp_id= ttpp_cus)
                id_edit_report = Report.objects.get(group_bill =id,cus_id_id = id_cus).id
                Report_ResultCheck.objects.filter(report_id=id_edit_report).delete()
                for index in range(len(bill_numbers)):
                    Report_ResultCheck.objects.create(report_id=str(id_edit_report),
                                                      bill_number = str(bill_numbers[index]),
                                                      sku=str(product_codes[index]),
                                                      name=str(product_names[index]),
                                                      quanty=str(product_amounts[index]),
                                                      unit=str(product_units[index]),
                                                      status=str(status_bills[index]))
                                                    #   solution=str(ttpp_executes[index]))
                with connection.cursor() as cur:
                    cur.execute("UPDATE [" + str(id_cus) + "|bill] set status_other = 'N', has_report = 1, report_number = "+str(id_edit_report+400000)+", last_change_date = GETDATE(), user_id_change = " + str(user_id) + " where group_hd = '" + str(id) + "'")
                    cur.execute("INSERT INTO [" + str(id_cus) + "|log_change_status] (listcus_id, user_id, type,  old_status, new_status, group_hd, date_change) \
                                                      VALUES (%s, %s, %s, %s, %s, %s,  GETDATE()) ",
                                [id_cus, user_id, 3, old_value_report_str, new_value_save_log, id])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
