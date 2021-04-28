from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,HttpResponseRedirect , Http404
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
from django.core.exceptions import PermissionDenied
from Service.common import common_function
# Create your views here.

class InvoiceListView(View):
    @method_decorator(allowed_permission(allowed_per='Xem bảng kê'))
    def get(self, request):
        date_from = request.GET.get ('timeStart', datetime.datetime.now().strftime('%d/%m/%Y'))
        date_to = request.GET.get ('timeEnd', datetime.datetime.now().strftime('%d/%m/%Y'))
        cus_search = request.GET.get ('select_cus', list(request.user.manager_cus.all().values_list('id',flat=True))[0])
        type_product_search = request.GET.getlist('select_type', ['14', '15'])
        bk_number_search = request.GET.get ('invoice_list_number', '')
        po_number_search = request.GET.get ('po_number', '')
        receiver_number_search = request.GET.get ('receiver_number', '')
        vendor_number_search = request.GET.get ('vendor_number', '')
        qa_search = request.GET.get ('select_qa', '')
        list_cus_manager = request.user.manager_cus.all().values('id', 'name' , 'store_number')
        list_status = StatusBill.objects.all().order_by('stt').values_list().values_list('id','symbol','name',flat=False)
        list_product = TypeProduct.objects.filter(is_show = True,type__in = [1,2])
        cus_managers = request.user.manager_cus.all().values('id', 'name', 'store_number')
        ###3 là loại bảng kê
        invoice_list_types = TypeProduct.objects.filter(type = 3).values('id', 'name')
        if not cus_managers.exists():
            cus_managers = [[request.user.cus.id, request.user.cus.name, request.user.cus.store_number]]

        ## save old url search
        request.session['url_old_search_invoice_list'] = request.get_full_path_info()
        context = {
            'date_from' : date_from,
            'date_to' : date_to,
            'cus_managers' : cus_managers,
            'cus_manager_chosed' : int(cus_search),
            'po_number_chosed' : po_number_search,
            'bk_number_chosed' : bk_number_search,
            'receiver_number_chosed' : receiver_number_search,
            'vendor_number_chosed' : vendor_number_search,
            'invoice_list_types' : invoice_list_types,
            'qa_chosed' : qa_search,
            'invoice_list_type_chosed' : type_product_search ,
            'list_cus' : list_cus_manager,
            'list_status' : list_status,
            'list_product' : list_product,
        }
        return render(request, 'invoice_list/invoice_list_show.html', context = context)


class DetailInvoiceList(View):
    @method_decorator(allowed_permission(allowed_per='Xem bảng kê'))
    def get(self, request, cus_id, id):
        if int(cus_id) not in request.session['list_cus_manager']:
            raise PermissionDenied
        query_str = "SELECT id, listcus_id, image_name, type_bk, bk_number \
                    , po_number, receiver_number, vendor_number, result_check \
                    , src_img, upload_date, is_qa, user_id_up, user_id_change,src_receiver \
                    FROM ["+str(cus_id)+"|bk] WHERE id = "+str(id)+""
        with connection.cursor() as cur:
            list_invoice = cur.execute(query_str).fetchone()

        try:
            list_result_checks = [ x.split('†') for x in list_invoice.result_check.split('‡')]
        except:
            list_result_checks = ['', '', '']
        list_type_bks = TypeProduct.objects.filter(type = 3, is_show = True).values('id', 'name')
        cus_name = ListCus.objects.filter(id=cus_id).values_list('name', flat=True)[0]
        context = {
            'list_invoice' : list_invoice,
            'list_type_bks' : list_type_bks,
            'list_result_checks' : list_result_checks,
            'cus_id' : cus_id,
            'cus_name' : cus_name,
        }

        return render(request, 'invoice_list/invoice_list_detail.html', context)

    @method_decorator(allowed_permission(allowed_per='Sửa bảng kê'))
    def post(self, request, cus_id, id):
        type_bk = request.POST.get('select-type-bk',14)
        bk_number = request.POST.get('input-bk-number','')
        po_number = request.POST.get('input-po-number','')
        receiver_number = request.POST.get('input-receiver-number','')
        vendor_number = request.POST.get('input-vendor-number','')
        result_check = request.POST.getlist('input-result_check_luoi[]',[])
        user_id = request.user.id
        str_result_check_insert = self.split_result_check_luoi(result_check, 3)

        str_check_qa = '❥'.join([type_bk, bk_number, po_number, receiver_number, vendor_number, str_result_check_insert])
        if '[QA]' in str_check_qa:
            is_qa = 1
        else:
            is_qa = 0

        sql_update = "UPDATE ["+str(cus_id)+"|bk] SET \
                            type_bk = "+str(type_bk)+" \
                            ,po_number = '"+str(po_number)+"' \
                            ,bk_number = '"+str(bk_number)+"' \
                            ,receiver_number = '"+str(receiver_number)+"' \
                            ,vendor_number = '"+str(vendor_number)+"' \
                            ,result_check = N'"+str(str_result_check_insert)+"' \
                            ,user_id_change = '"+str(user_id)+"' \
                            ,is_qa = '"+str(is_qa)+"' \
                            ,last_change_date = getdate() \
                      WHERE id = "+str(id)+" "
        sql_insert_log = "INSERT INTO ["+str(cus_id)+"|log_change_status] (listcus_id, user_id, type, old_status, new_status, date_change, bill_id)  \
                                 VALUES (%s, %s, %s, %s, %s, getdate(), %s )"
        with connection.cursor() as cur:
            sql_old_values_save_log = cur.execute(
                "SELECT  type_bk, bk_number \
                    , po_number, receiver_number, vendor_number, result_check \
                    , is_qa \
                FROM [" + str(cus_id) + "|bk] WHERE id = " + str(id) + "").fetchone()
        old_values_save_log = '❥'.join(str(x) if x != None else '' for x in sql_old_values_save_log)

        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(sql_update)
                cur.execute(sql_insert_log, [cus_id, user_id, 5, str(old_values_save_log), str(str_check_qa) + '❥' + str(is_qa), id])
            messages.success(request, 'Chỉnh sửa thành công !!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @staticmethod
    def split_result_check_luoi(l, n):
        if len(l) < n:
            return '†††'
        list_temp1 = []
        list_temp2 = []
        for (i, x) in enumerate(l, start=1):
            if i % n == 0:
                list_temp1.append(x.strip())
                tem_str = '†'.join(list_temp1)
                list_temp2.append(tem_str)
                list_temp1 = []
            else:
                list_temp1.append(x.strip())

        return '‡'.join(list_temp2)
class PrintInvoiceList(View):
    @method_decorator(allowed_permission(allowed_per = 'Xuất thống kê'))
    # @method_decorator(allowed_cus_manager(cus = request.GET.get('select_cus')))
    def get(self, request):
        date_export = request.GET.get('date_export', None)
        cus_chosed = request.GET.get('select_cus', None)
        status_chosed = request.GET.getlist('select_status', None)
        type_product_chosed = request.GET.getlist('select_type_product', [])
        batch_end_chosed = request.GET.getlist('select_batch', [])

        if None in [date_export, cus_chosed] or type_product_chosed == [] :
            return HttpResponse("Thiếu dữ liệu để chiết xuất thống kê!! Vui lòng chọn rồi thử lại")

        if not common_function.check_has_permission_in_cus(request, cus_chosed):
            return HttpResponse("Bạn không có quyền quản lí chi nhánh này")

        list_product_name = TypeProduct.objects.filter(pk__in = type_product_chosed).values_list('name', flat=True)
        str_list_product_name = ','.join(list(list_product_name))
        str_status_chosed = ','.join(status_chosed)
        str_type_product_chosed = ','.join(type_product_chosed)
        str_batch_end_chosed = ','.join(batch_end_chosed)
        date_from_convert = date_export[6:10] + '/' + date_export[3:5] + '/' + date_export[0:2] + ' 00:00:00'
        date_to_convert = date_export[6:10] + '/' + date_export[3:5] + '/' + date_export[0:2] + ' 23:59:59'


        sql = "SELECT isnull(bk_number,'') as bk_number, isnull(po_number,'') as po_number, isnull(vendor_number,'') as vendor_number, isnull(receiver_number,'') as receiver_number \
               FROM ["+str(cus_chosed)+"|bk] as tb1 \
                INNER JOIN Service_typeproduct as tb2 ON tb1.type_bk = tb2.id \
                WHERE \
                        upload_date > '"+str(date_from_convert)+"' \
                        and upload_date < '"+str(date_to_convert)+"' \
                        and type_bk in ("+str(str_type_product_chosed)+") \
                         ORDER BY [index]"
        with connection.cursor() as cursor:
            bills = cursor.execute(sql).fetchall()
        # print(bills)

        ###Phải tính các giá trị tiền hàng VAT (split from resultcheck)
        bills_return = []
        
        context = {
            'cus_name' : ListCus.objects.filter(id = cus_chosed).first().name.upper(),
            'str_list_product_name' : ', '.join(list_product_name),
            'str_batch_end' : str_batch_end_chosed,
            'bills' : bills,
            'bills_return' : bills_return,
            'date_export' : date_export
        }
        return render(request, 'invoice_list/print_invoice_list_show.html', context)
