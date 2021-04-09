from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,HttpResponseRedirect
from Service.decorators import allowed_user, allowed_permission, allowed_cus_manager
from django.utils.decorators import method_decorator
from Service.models import *
import datetime
from Service.common import common_function
from django.db import connection
# Create your views here.

class HomeView(View):
    @method_decorator(allowed_permission(allowed_per = 'Xem hóa đơn'))
    def get(self, request):
        if request.user.role.symbol == 'TTPP':
            return HttpResponseRedirect('/home/warehouse')

        list_cus_manager = request.user.manager_cus.all().values('id', 'name' , 'store_number')
        list_product = TypeProduct.objects.filter(is_show = True,type__in = [1,2])
        cus_chosed = request.GET.get('selectbranch', list_cus_manager[0]['id'])
        status_chosed = request.GET.getlist('selectstatus[]', [StatusBill.objects.first().id])
        date_from = request.GET.get('timeStart', datetime.datetime.now().strftime('%d/%m/%Y'))
        date_to = request.GET.get('timeEnd', datetime.datetime.now().strftime('%d/%m/%Y'))
        list_status = StatusBill.objects.all().order_by('stt').values_list().values_list('id','symbol','name',flat=False)
        #print(list_status)
        ## save old url search
        request.session['url_old_search_bill'] = request.get_full_path_info()
        list_status_per_change = PermissionChangeStatus.objects.filter(role_id=request.user.role_id).exclude(
            new_status__isnull=True).exclude(new_status__exact='').values_list('recent_status', flat=True)

        context = {
            'date_from' :  date_from,
            'date_to' : date_to,
            'list_status' : list_status,
            'list_cus' : list_cus_manager,
            'cus_chosed' : int(cus_chosed),
            'status_chosed' : list(map(int, status_chosed)),
            'list_product' : list_product,
            'list_status_per_change' : list_status_per_change
        }
        return render(request, 'home/base_home_one_file.html', context)

class PrintStatistical(View):
    @method_decorator(allowed_permission(allowed_per = 'Xuất thống kê'))
    # @method_decorator(allowed_cus_manager(cus = request.GET.get('select_cus')))
    def get(self, request):
        date_export = request.GET.get('date_export', None)
        cus_chosed = request.GET.get('select_cus', None)
        status_chosed = request.GET.getlist('select_status', None)
        type_product_chosed = request.GET.getlist('select_type_product', [])
        batch_end_chosed = request.GET.getlist('select_batch', [])

        if None in [date_export, cus_chosed, status_chosed] or type_product_chosed == [] or batch_end_chosed == []:
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


        sql = "SELECT bill_date, bill_number, vendor_number, city_name, result_check \
               FROM ["+str(cus_chosed)+"|bill] as tb1 \
                INNER JOIN Service_typeproduct as tb2 ON tb1.type_product_id = tb2.id \
                WHERE \
                        upload_date > '"+str(date_from_convert)+"' \
                        and upload_date < '"+str(date_to_convert)+"' \
                        and type_product_id in ("+str(str_type_product_chosed)+") \
                        and status_id in ("+str(str_status_chosed)+") \
                        and ket_thuc_dot_number in ("+str_batch_end_chosed+")  \
                        and is_po <> 1  \
                ORDER BY [index],  is_ttpp, upload_date "
        with connection.cursor() as cursor:
            bills = cursor.execute(sql).fetchall()

        ###Phải tính các giá trị tiền hàng VAT (split from resultcheck)
        bills_return = []
        for bill in bills:
            result_check_split = bill.result_check.split('‡')
            try:
                if result_check_split[17] == '' or result_check_split[17] == 'null' or result_check_split[17] == 'None':
                    tien_vat = ''
                elif '[QA]' in result_check_split[17]  :
                    tien_vat = '[QA]'
                else:
                    tien_vat = result_check_split[17]
            except:
                tien_vat = ''

            try:
                if result_check_split[16] == '' or result_check_split[16] == 'null' or result_check_split[16] == 'None':
                    tien_hang = ''
                elif '[QA]' in result_check_split[16]  :
                    tien_hang = '[QA]'
                else:
                    tien_hang = result_check_split[16]
            except:
                tien_hang = ''

            try:
                if result_check_split[18] == '' or result_check_split[18] == 'null' or result_check_split[18] == 'None':
                    tien_thanh_toan = ''
                elif '[QA]' in result_check_split[18]  :
                    tien_thanh_toan = '[QA]'
                else:
                    tien_thanh_toan = result_check_split[18]
            except:
                tien_thanh_toan = ''


            try:
                if float(result_check_split[18]) - float(result_check_split[16]) == 0:
                    vat = 0
                else:
                    vat = round((float(result_check_split[17]) / float(result_check_split[16])) * 100)
            except Exception as error:
                # print(error)
                vat = 0
            bills_return.append([bill.bill_date, bill.bill_number, bill.vendor_number, bill.city_name, tien_hang, vat, tien_vat, tien_thanh_toan])
        context = {
            'cus_name' : ListCus.objects.filter(id = cus_chosed).first().name.upper(),
            'str_list_product_name' : ', '.join(list_product_name),
            'str_batch_end' : str_batch_end_chosed,
            'bills' : bills,
            'bills_return' : bills_return,
            'date_export' : date_export
        }
        return render(request, 'home/print_statistical.html', context)
