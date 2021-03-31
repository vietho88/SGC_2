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
import pandas as pd
from io import BytesIO# Create your views here.
from Service.common import common_function
import re
import os
from django.conf import settings
class DataTableHomeView(View):
    @method_decorator(allowed_permission(allowed_per = 'Xem hóa đơn'))
    def get(self, request):
        draw = request.GET.get('draw')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        start_num = int(request.GET.get('start',0))
        length_one_page = int(request.GET.get('length',10))
        cus_search = request.GET.get('list_cus_search','')
        status_search = request.GET.getlist('list_status_search[]')
        date_from_convert = date_from[6:10] + '/' + date_from[3:5] + '/'+date_from[0:2] + ' 00:00:00'
        date_to_convert = date_to[6:10] + '/' + date_to[3:5] + '/'+date_to[0:2] + ' 23:59:59'
        check_search_advance = request.GET.get('check_seach_advance')
        # id_cus = request.user.cus.id
        if  str(cus_search) == '' :
            cus_search = str(request.user.cus.id)
        if str(status_search) != '[]' :
            str_status_search = ','.join(status_search)
        else:
            str_status_search = str(1)

        ####order datatable custom#####
        number_fieds_sort = request.GET.get('order[0][column]', '')
        type = request.GET.get('order[0][dir]', '')
        query_order = 'group_hd asc'
        if number_fieds_sort:
            query_order = self.find_order(number_fieds_sort, type)

        ###Search nâng cao
        if check_search_advance == 'true' :
            bill_number_seach  = request.GET.get('bill_number_search','')
            report_number_search  = request.GET.get('report_number_search','')
            report_company_search  = request.GET.get('report_company_search','')
            tax_number_search  = request.GET.get('tax_number_search','')
            vendor_number_search  = request.GET.get('vendor_number_search','')
            receiver_number_search  = request.GET.get('receiver_number_search','')
            po_number_search  = request.GET.get('po_number','')
            qa_search  = request.GET.get('type_qa','')
            type_report_search  = request.GET.get('type_report','')
            type_product_search = request.GET.get('type_product', '')

            ###Clear "'" tranh tan cong sql injection
            bill_number_seach = re.sub('[\',\"]', '', bill_number_seach)
            report_number_search = re.sub('[\',\"]', '', report_number_search)
            tax_number_search = re.sub('[\',\"]', '', tax_number_search)
            vendor_number_search = re.sub('[\',\"]', '', vendor_number_search)
            receiver_number_search = re.sub('[\',\"]', '', receiver_number_search)
            po_number_search = re.sub('[\',\"]', '', po_number_search)
            report_company_search = re.sub('[\',\"]', '', report_company_search)

            ###Serach expend if have ####
            search_for_type_product = "and type_product_id = '" + str(type_product_search) + "'"
            search_for_bill_number = "and bill_number like '%" + str(bill_number_seach) + "%'"
            search_for_company_name = "and city_name like N'%" + str(report_company_search) + "%'"
            search_for_tax_number = "and tax_number like '%" + str(tax_number_search) + "%'"
            search_for_vendor_number = "and vendor_number like '%" + str(vendor_number_search) + "%'"
            search_for_receiver_number = "and receiver_number like '%" + str(receiver_number_search) + "%'"
            search_for_po_number = "and po_number like '%" + str(po_number_search) + "%'"
            search_for_report_number = "and report_number like '%" + str(report_number_search) + "%'"
            search_for_qa = "and is_qa = '" + str(qa_search) + "'"
            search_for_type_report = "and status_other = '" + str(type_report_search) + "'"
            query_all = "SELECT  group_hd\
                        FROM \
                            [dbo].[" + str(cus_search) + "|bill] \
                        WHERE \
                            listcus_id = " + str(cus_search) + " and status_id in (" + str(str_status_search) + ") \
                            and upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'  \
                            and is_po <> 1 \
                            "+ (search_for_type_product if type_product_search != '' else '') +"  \
                            "+ (search_for_bill_number if bill_number_seach != '' else '') +"  \
                            "+ (search_for_company_name if report_company_search != '' else '') +"  \
                            "+ (search_for_tax_number if tax_number_search != '' else '') +"  \
                            "+ (search_for_vendor_number if vendor_number_search != '' else '') +"  \
                            "+ (search_for_receiver_number if receiver_number_search != '' else '') +"  \
                            "+ (search_for_po_number if po_number_search != '' else '') +"  \
                            "+ (search_for_report_number if report_number_search != '' else '') +"  \
                            "+ (search_for_qa if qa_search != '' else '') +"  \
                            "+ (search_for_type_report if type_report_search != '' else '') +"  \
                        GROUP BY \
                            group_hd \
                        ORDER BY \
                            group_hd "
            query2 = "SELECT\
                        group_hd \
                        ,STRING_AGG(concat(tb1.symbol, '-', tb1.bill_number), '<Br>') symbol\
                        ,STRING_AGG(tb1.tax_number,'|')  tax_number\
                        ,STRING_AGG(tb1.city_name,'|')  city_name\
                        ,STRING_AGG(tb1.bill_date,'|')  bill_date\
                        ,STRING_AGG(tb1.upload_date,'|') upload_date\
                        ,STRING_AGG(tb1.status_id,'|') status_id\
                        ,STRING_AGG(tb1.sum_po,'|') sum_po\
                        ,STRING_AGG(tb1.vendor_number,'|') vendor_number\
                        ,STRING_AGG(tb1.po_number,'|') po_number\
                        ,STRING_AGG(tb1.receiver_number,'|') receiver_number\
                        ,STRING_AGG(tb1.is_qa,'|') is_qa\
                        ,STRING_AGG(tb1.is_hddt,'|') is_hddt\
                        ,STRING_AGG(tb1.has_report,'|') has_report\
                        ,STRING_AGG(tb2.symbol, '<Br>') status_name\
                        ,STRING_AGG(tb1.listcus_id,'|') \
                        ,STRING_AGG(tb1.last_change_date,'|') last_change_date\
                        ,STRING_AGG(tb3.name,'|') type_product_name\
                        ,STRING_AGG(tb1.status_other,'|') status_other\
                        ,STRING_AGG(tb1.report_number,'|') report_number\
                    FROM \
                        [dbo].[" + str(cus_search) + "|bill] as tb1 \
                    INNER JOIN \
                        [dbo].[service_statusbill] as tb2 \
                    ON \
                        tb1.status_id = tb2.id \
                    INNER JOIN \
                        [dbo].[service_typeproduct] as tb3 \
                    ON \
                        tb1.type_product_id = tb3.id \
                    WHERE \
                        tb1.listcus_id = " + str(cus_search) + " and tb1.status_id in (" + str(str_status_search) + ")  \
                        and upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'  \
                        and tb1.is_po <> 1 \
                        "+ (search_for_type_product if type_product_search != '' else '') +"  \
                        "+ (search_for_bill_number if bill_number_seach != '' else '') +"  \
                        "+ (search_for_company_name if report_company_search != '' else '') +"  \
                        "+ (search_for_tax_number if tax_number_search != '' else '') +"  \
                        "+ (search_for_vendor_number if vendor_number_search != '' else '') +"  \
                        "+ (search_for_receiver_number if receiver_number_search != '' else '') +"  \
                        " + (search_for_po_number if po_number_search != '' else '') + "  \
                        " + (search_for_report_number if report_number_search != '' else '') + "  \
                        " + (search_for_qa if qa_search != '' else '') + "  \
                        " + (search_for_type_report if type_report_search != '' else '') + "  \
                    GROUP BY \
                        group_hd \
                    ORDER BY \
                        " + str(query_order) + "\
                    offset " + str(start_num) + " rows fetch next " + str(length_one_page) + " rows only "
        else:
            query_all = "SELECT  group_hd\
                    FROM \
                        [dbo].[" + str(cus_search) + "|bill] \
                    WHERE \
                        listcus_id = " + str(cus_search) + " and status_id in (" + str(str_status_search) + ") \
                        and upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'  \
                        and is_po <> 1 \
                    GROUP BY \
                        group_hd \
                    ORDER BY \
                        group_hd "

            query2 = "SELECT\
                    group_hd \
                    ,STRING_AGG(concat(tb1.symbol, '-', tb1.bill_number), '<Br>') symbol\
                    ,STRING_AGG(tb1.tax_number,'|')  tax_number\
                    ,STRING_AGG(tb1.city_name,'|')  city_name\
                    ,STRING_AGG(tb1.bill_date,'|')  bill_date\
                    ,STRING_AGG(tb1.upload_date,'|') upload_date\
                    ,STRING_AGG(tb1.status_id,'|') status_id\
                    ,STRING_AGG(tb1.sum_po,'|') sum_po\
                    ,STRING_AGG(tb1.vendor_number,'|') vendor_number\
                    ,STRING_AGG(tb1.po_number,'|') po_number\
                    ,STRING_AGG(tb1.receiver_number,'|') receiver_number\
                    ,STRING_AGG(tb1.is_qa,'|') is_qa\
                    ,STRING_AGG(tb1.is_hddt,'|') is_hddt\
                    ,STRING_AGG(tb1.has_report,'|') has_report\
                    ,STRING_AGG(tb2.symbol, '<Br>') status_name\
                    ,STRING_AGG(tb1.listcus_id,'|') \
                    ,STRING_AGG(tb1.last_change_date,'|') last_change_date\
                    ,STRING_AGG(tb3.name,'|') type_product_name\
                    ,STRING_AGG(tb1.status_other,'|') status_other\
                    ,STRING_AGG(tb1.report_number,'|') report_number\
                FROM \
                    [dbo].[" + str(cus_search) + "|bill] as tb1 \
                INNER JOIN \
                    [dbo].[service_statusbill] as tb2 \
                ON \
                    tb1.status_id = tb2.id \
                INNER JOIN \
                    [dbo].[service_typeproduct] as tb3 \
                ON \
                    tb1.type_product_id = tb3.id \
                WHERE \
                    tb1.listcus_id = " + str(cus_search) + " and tb1.status_id in (" + str(str_status_search) + ")  \
                    and upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'  \
                    and tb1.is_po <> 1 \
                GROUP BY \
                    group_hd \
                ORDER BY \
                     " + str(query_order) + "\
                offset " + str(start_num) + " rows fetch next " + str(length_one_page) + " rows only "

        with connection.cursor() as cur:
            total_record = len(cur.execute(query_all).fetchall())
            all_group_bill_limit = cur.execute(query2).fetchall()
            data = []
            for group in all_group_bill_limit:
                try:
                    upload_date = datetime.datetime.strptime(group[5].split('|')[0], '%b %d %Y %I:%M%p').strftime('%d/%m/%Y %H:%M:%S')
                    last_change_date = datetime.datetime.strptime(group[16].split('|')[0], '%b %d %Y %I:%M%p').strftime('%d/%m/%Y %H:%M:%S') if group[16] else upload_date
                    list_sym =group[1].split('<Br>')
                    list_status = group[14].split('<Br>')
                    # indexes = [list_sym.index(x) for x in set(list_sym)]
                    indexes =list(map(lambda x: list_sym.index(x), set(list_sym)))
                    indexes.sort()
                    # a = '<Br>'.join([ list_sym[x] for x in indexes ])
                    a= '<Br>'.join(list(map(lambda x: list_sym[x], indexes)))
                    # b= '<Br>'.join([ list_status[x] for x in indexes ])
                    b= '<Br>'.join(list(map(lambda x: list_status[x], indexes)))

                    temp = {
                        'group' : group[0],
                        'symbol' : a,
                        'tax_number' : group[2].split('|')[0] if group[2] else '',
                        'city_name' : group[3].split('|')[0] if group[3] else '',
                        'date_group_bill' : group[4].split('|')[0] if group[4] else '',
                        'date_upload' : group[5].split('|')[0] if group[5] else '',
                        'last_change_date' :  last_change_date,
                        'upload_date' : upload_date,
                        'status_bill__symbol': b if b else '',
                        'status_bill__name': group[14] if group[14] else '',
                        'reciever_number':group[10].split('|')[0] if group[10] else '',
                        'po_number':group[9].split('|')[0] if group[9] else '',
                        'vendor_number':group[8].split('|')[0] if group[8] else '',
                        'sum_po':group[7].split('|')[0] if group[7] else '',
                        'is_qa' : group[11].split('|')[0] if group[11] else '',
                        'is_hddt' : group[12].split('|')[0] if group[12] else '',
                        'has_report' : group[13].split('|')[0] if group[13] else '',
                        'id_cus' : group[15].split('|')[0] if group[15] else '',
                        'type_product' : group[17].split('|')[0] if group[17] else '',
                        'status_other' : group[18].split('|')[0] if group[18] else '',
                        'report_number' : group[19].split('|')[0] if group[19] else '',
                     }
                    data.append(temp)
                except Exception as e :
                    print(e)

        context = {
            "draw": draw,
            "recordsTotal": total_record,
            "recordsFiltered": total_record,
            "data": data
        }
        return JsonResponse(context, safe=False)

    @staticmethod
    def find_order(field, type):
        dict_option = {
            0: 'group_hd',
            1: 'symbol',
            2: 'report_number',
            3: 'tax_number',
            4: 'city_name',
            5: 'bill_date',
            6: 'upload_date',
            7: 'last_change_date',
            8: 'status_name',
            9: 'status_other',
            10: 'vendor_number',
            11: 'sum_po',
            12: 'po_number',
            13: 'receiver_number',
            14: 'type_product_name',
            15: 'is_qa',
            16: 'is_hddt',
        }
        return dict_option[(int(field))] + ' ' + type


def update_status_group_bill(request):
    if request.method == "POST":
        id_group = request.POST.get('input-id-group',None)
        symbol_new_status = request.POST.get('select-status', None)
        symbol_old_status = request.POST.get('input-old-status', None)
        cus_id = request.user.cus.id
        if id_group is None or symbol_new_status is None:
            message = "Error"
        else:
            try:
                find_id_status = StatusBill.objects.get(symbol=symbol_new_status).id
            except StatusBill.DoesNotExist:
                message = "Error"
            else:
                with transaction.atomic():
                    with connection.cursor() as cur:
                        cur.execute("UPDATE ["+str(cus_id)+"|bill] set status_id = %s WHERE group_hd = "+str(id_group)+"", [find_id_status])
                        cur.execute("INSERT into ["+str(cus_id)+"|log_change_Status] (listcus_id, user_id, type, old_status, new_status, date_change) \
                                     values (%s, %s, %s, %s, %s, %s)", [cus_id, request.user.id, 1, symbol_old_status, symbol_new_status, datetime.datetime.now().strftime('%Y-%m-%d')])
                per_change = PermissionChangeStatus.objects.get(recent_status=symbol_new_status, role=request.user.role.id)
                list_per_change_status = per_change.new_status.split('|')
                message = "success"
        return JsonResponse({
            'message' : message,
            'list_per_change_status' : list_per_change_status
        }, safe=False)

@login_required()
def change_option_site_add_user(request):
    site_id = request.GET.get('site_id')
    list_cus_site = ListCus.objects.filter(site=site_id).values_list('id', 'name')
    list_rol_site = Role.objects.filter(site=site_id).values_list('id', 'name')

    return JsonResponse({
        'list_cus_site' : list(list_cus_site),
        'list_rol_site' : list(list_rol_site)
    }, safe=False)


@login_required()
@allowed_permission(allowed_per = 'Xuất báo cáo excel')
def export_excel_report_home(request):
    if request.method == 'GET':
        message = request.GET.get('message')
        cus_search = request.GET.get('list_cus_search', '')
        status_search = request.GET.getlist('list_status_search[]')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        date_from_convert = date_from[6:10] + '/' + date_from[3:5] + '/' + date_from[0:2] + ' 00:00:00'
        date_to_convert = date_to[6:10] + '/' + date_to[3:5] + '/' + date_to[0:2] + ' 23:59:59'
        check_search_advance = request.GET.get('check_seach_advance')
        ####If check_dowload exist ==>dow file
        check_dowload = request.GET.get('dowload', '')

        if not common_function.check_has_permission_in_cus(request, cus_search):
            return HttpResponse("Bạn không có quyền quản lí chi nhánh này")

        data_export = []
        if  str(cus_search) == '' :
            cus_search = str(request.user.cus.id)
        if str(status_search) != '[]' :
            str_status_search = ','.join(status_search)
        else:
            str_status_search = str(1)

        # if check_search_advance == 'true' :
        bill_number_seach  = request.GET.get('bill_number_search','')
        report_number_search  = request.GET.get('report_number_search','')
        tax_number_search  = request.GET.get('tax_number_search','')
        vendor_number_search  = request.GET.get('vendor_number_search','')
        receiver_number_search  = request.GET.get('receiver_number_search','')
        po_number_search  = request.GET.get('po_number','')
        qa_search  = request.GET.get('type_qa','')
        type_report_search  = request.GET.get('type_report','')
        type_product_search = request.GET.get('type_product', '')

        ###Serach expend if have ####
        search_for_type_product = "and type_product_id = '" + str(type_product_search) + "'"
        search_for_bill_number = "and bill_number like '%" + str(bill_number_seach) + "%'"
        search_for_tax_number = "and tax_number like '%" + str(tax_number_search) + "%'"
        search_for_vendor_number = "and vendor_number like '%" + str(vendor_number_search) + "%'"
        search_for_receiver_number = "and receiver_number like '%" + str(receiver_number_search) + "%'"
        search_for_po_number = "and po_number like '%" + str(po_number_search) + "%'"
        search_for_report_number = "and po_number like '%" + str(report_number_search) + "%'"
        search_for_qa = "and is_qa = '" + str(qa_search) + "'"
        search_for_type_report = "and status_other = '" + str(type_report_search) + "'"
        query = "SELECT\
                tb1.symbol as symbol, tb1.bill_number as bill_number , tb1.bill_date as bill_date, \
                tb1.tax_number as tax_number, tb1.city_name as city_name, tb1.city_address as city_address, \
                tb2.symbol as status_name, tb1.result_check as result_check, tb1.vendor_number as vendor_number, \
                tb1.po_number as po_number, tb3.name as type_product, tb1.ket_thuc_dot_number as ket_thuc_dot_number \
                ,tb1.report_number, tb1.status_other, tb1.result_check_luoi, tb1.receiver_number \
                FROM \
                    [dbo].[" + str(cus_search) + "|bill] as tb1 \
                INNER JOIN \
                    [dbo].[service_statusbill] as tb2 \
                ON \
                    tb1.status_id = tb2.id \
                INNER JOIN \
                    [dbo].[service_typeproduct] as tb3 \
                ON \
                    tb1.type_product_id = tb3.id \
                WHERE \
                    tb1.listcus_id = " + str(cus_search) + " and tb1.status_id in (" + str(str_status_search) + ")  \
                    and upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'  \
                    and tb1.is_po <> 1 and tb1.status_id <> 1\
                    "+ (search_for_type_product if type_product_search != '' else '') +"  \
                    "+ (search_for_bill_number if bill_number_seach != '' else '') +"  \
                    "+ (search_for_tax_number if tax_number_search != '' else '') +"  \
                    "+ (search_for_vendor_number if vendor_number_search != '' else '') +"  \
                    "+ (search_for_receiver_number if receiver_number_search != '' else '') +"  \
                    " + (search_for_po_number if po_number_search != '' else '') + "  \
                    " + (search_for_qa if qa_search != '' else '') + "  \
                    " + (search_for_type_report if type_report_search != '' else '') + "  \
                ORDER BY \
                    group_hd "
        current_full_url = request.build_absolute_uri()
        with connection.cursor() as cursor:
            bills = cursor.execute(query).fetchall()

        message_return = 'nodata' if bills == [] else 'success'
        money_before_tax = ''
        money_tax = ''
        money_after_tax = ''
        name_product = ''
        name_cus = ListCus.objects.filter(id = cus_search).first().name
        if check_dowload != '' :
            for index, bill in enumerate(bills, start=1):
                result_split = bill.result_check.split('‡')
                try:
                    money_before_tax = '{:,.0f}'.format(int(result_split[16]))
                    money_tax = '{:,.0f}'.format(int(result_split[17]))
                    money_after_tax = '{:,.0f}'.format(int(result_split[18]))
                    name_product = bill.result_check_luoi.split('†')[1]
                except:
                    pass
                dict_bill = [
                    index,
                    name_cus,
                    bill.bill_date,
                    bill.symbol,
                    bill.bill_number ,
                    bill.report_number if bill.report_number != '0' else '',
                    bill.bill_date,
                    bill.tax_number,
                    bill.city_name,
                    bill.city_address,
                    bill.status_name,
                    bill.status_other,
                    name_product,
                    money_before_tax,
                    money_tax,
                    money_after_tax,
                    bill.vendor_number,
                    bill.po_number,
                    bill.type_product,
                    bill.ket_thuc_dot_number,
                    bill.receiver_number if bill.receiver_number not in ['nan', 'none'] else ''
                ]
                data_export.append(dict_bill)

            column = ['STT', 'Tên đơn vị', 'Ngày nhận hóa đơn', 'Ký hiệu', 'Số hóa đơn',
                      'Số biên bản' , 'Ngày hóa đơn', 'Mã số thuế','Tên công ty', 'Địa chỉ',
                      'Trạng thái hóa đơn', 'Trạng thái biên bản', 'Tên mặt hàng ', 'Tổng tiền trước thuế', 'Tổng tiền thuế',
                      'Tổng tiền sau thuế' ,'Mã vendor', 'PO/Transfer', 'Ngành hàng', 'Đợt', 'Mã receiver' ]
            df = pd.DataFrame(data=data_export, columns=column)
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                df.to_excel(writer, sheet_name='Sheet1', index=False)
                writer.save()
                return HttpResponse(b.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        else:
            return JsonResponse({
                'message': message_return,
                'current_full_url': current_full_url.replace('http://127.0.0.1:5085/', 'http://sgc02.qlhd.vn/')
            })

@allowed_permission(allowed_per = 'Xuất thống kê')
def export_statistical_home(request):
    if request.method == 'GET':
        message = request.GET.get('message')
        list_status = request.GET.getlist('list_status[]', ['1','2'])
        cus = request.GET.get('cus',1)
        date = request.GET.get('date')
        date_from_convert = date[6:10] + '/' + date[3:5] + '/' + date[0:2] + ' 00:00:00'
        date_to_convert = date[6:10] + '/' + date[3:5] + '/' + date[0:2] + ' 23:59:59'
        list_type_product_return = []
        list_dot_return = []
        if message == 'get_data':
            with connection.cursor() as cur:
                query_type_product = "SELECT distinct tb2.id, tb2.name FROM ["+str(cus)+"|bill] as tb1 INNER JOIN [service_typeproduct] as tb2 \
                        ON  \
                            tb1.type_product_id = tb2.id\
                        WHERE \
                            tb1.listcus_id = "+str(cus)+" and tb1.status_id in ("+str(','.join(list_status))+") \
                            and upload_date > '"+date_from_convert+"' and upload_date < '"+date_to_convert+"'"
                query_dot = "SELECT distinct tb1.ket_thuc_dot_number FROM ["+str(cus)+"|bill] as tb1 INNER JOIN [service_typeproduct] as tb2 \
                         ON  \
                             tb1.type_product_id = tb2.id\
                         WHERE \
                             tb1.listcus_id = " + str(cus) + " and tb1.status_id in (" + str(','.join(list_status)) + ") \
                            and upload_date > '"+date_from_convert+"' and upload_date < '"+date_to_convert+"' "
                list_type_product = cur.execute(query_type_product).fetchall()
                list_dot  = cur.execute(query_dot).fetchall()
                if len(list_type_product):
                    list_type_product_return =  [ list(x) for x in list_type_product]
                    list_dot_return =  [ list(x) for x in list_dot if x[0] is not None]
                return JsonResponse({
                    'message' : 'success',
                    'list_type_product' : list_type_product_return,
                    'list_dot' :list_dot_return
                })
        elif message == 'export_excel':
            pass

@allowed_permission(allowed_per = 'Chuyển trạng thái hóa đơn hàng loạt')
@csrf_exempt
def get_group_bill_exchange_many_status(request):
    cus_find = request.GET.get('cus_find', None)
    status_find = request.GET.get('status_find', None)
    type_product_find = request.GET.getlist('type_product_find[]', None)
    batch_end_find = request.GET.getlist('batch_end_find[]', None)
    date_search = request.GET.get('date', None)
    date_find_from = date_search[6:10] + '/' + date_search[3:5] + '/' + date_search[0:2] + ' 00:00:00'
    date_find_to = date_search[6:10] + '/' + date_search[3:5] + '/' + date_search[0:2] + ' 23:59:59'

    query_select_all = "SELECT\
                        group_hd \
                        ,STRING_AGG(concat(tb1.symbol, '-', tb1.bill_number), '<Br>')\
                        ,STRING_AGG(tb1.tax_number,'|')  \
                        ,STRING_AGG(tb1.city_name,'|')  \
                        ,STRING_AGG(tb1.bill_date,'|') \
                        ,STRING_AGG(tb1.upload_date,'|') \
                        ,STRING_AGG(tb1.status_id,'|') \
                        ,STRING_AGG(tb1.sum_po,'|') \
                        ,STRING_AGG(tb1.vendor_number,'|')\
                        ,STRING_AGG(tb1.po_number,'|') \
                        ,STRING_AGG(tb1.receiver_number,'|') \
                        ,STRING_AGG(tb1.is_qa,'|') \
                        ,STRING_AGG(tb1.is_hddt,'|') \
                        ,STRING_AGG(tb1.has_report,'|') \
                        ,STRING_AGG(concat(tb2.symbol, ' - ', tb2.name), '|') \
                        ,STRING_AGG(tb1.listcus_id,'|') \
                        ,STRING_AGG(tb1.last_change_date,'|') \
                        ,STRING_AGG(tb3.name,'|') \
                        ,STRING_AGG(tb1.status_other,'|') \
                        ,STRING_AGG(tb1.report_number,'|') \
                    FROM \
                        [dbo].[" + str(cus_find) + "|bill] as tb1 \
                    INNER JOIN \
                        [dbo].[service_statusbill] as tb2 \
                    ON \
                        tb1.status_id = tb2.id \
                    INNER JOIN \
                        [dbo].[service_typeproduct] as tb3 \
                    ON \
                        tb1.type_product_id = tb3.id \
                    WHERE \
                        tb1.listcus_id = " + str(cus_find) + " and tb1.status_id = "+str(status_find)+"  \
                        and upload_date > '" + date_find_from + "' and upload_date < '" + date_find_to + "'  \
                        and tb1.is_po <> 1 and type_product_id in ("+str(',').join(type_product_find)+") \
                        and ket_thuc_dot_number in ("+str(',').join(batch_end_find)+") \
                    GROUP BY \
                        group_hd \
                    ORDER BY \
                        group_hd "

    with connection.cursor() as cur:
        all_group_bill_limit = cur.execute(query_select_all).fetchall()
        data = []
        for group in all_group_bill_limit:
            try:
                upload_date = datetime.datetime.strptime(group[5].split('|')[0], '%b %d %Y %I:%M%p').strftime(
                    '%d/%m/%Y %H:%M:%S')
                last_change_date = datetime.datetime.strptime(group[16].split('|')[0], '%b %d %Y %I:%M%p').strftime(
                    '%d/%m/%Y %H:%M:%S') if group[16] else upload_date
                temp = {
                    'group' : group[0],
                    'symbol' : group[1],
                    'tax_number' : group[2].split('|')[0] if group[2] else '',
                    'city_name' : group[3].split('|')[0] if group[3] else '',
                    'date_group_bill' : group[4].split('|')[0] if group[4] else '',
                    'date_upload' : group[5].split('|')[0] if group[5] else '',
                    'last_change_date' :  last_change_date,
                    'upload_date' : upload_date,
                    'status_bill__symbol': group[14].split('|')[0] if group[14] else '',
                    'status_bill__name': group[14].split('|')[0] if group[14] else '',
                    'reciever_number':group[10].split('|')[0] if group[10] else '',
                    'po_number':group[9].split('|')[0] if group[9] else '',
                    'vendor_number':group[8].split('|')[0] if group[8] else '',
                    'sum_po':group[7].split('|')[0] if group[7] else '',
                    'is_qa' : group[11].split('|')[0] if group[11] else '',
                    'is_hddt' : group[12].split('|')[0] if group[12] else '',
                    'has_report' : group[13].split('|')[0] if group[13] else '',
                    'id_cus' : group[15].split('|')[0] if group[15] else '',
                    'type_product' : group[17].split('|')[0] if group[17] else '',
                    'status_other' : group[18].split('|')[0] if group[18] else '',
                    'report_number' : group[19].split('|')[0] if group[19] else '',
                }
                data.append(temp)
            except Exception as e:
                print(e)
    symbol_status = StatusBill.objects.get(id=status_find).symbol
    list_per_change = PermissionChangeStatus.objects.filter(recent_status= symbol_status, role_id = request.user.role_id).values_list('new_status')
    list_per_change_return = list(list_per_change)[0][0].split('|')
    return JsonResponse({
        'message' : 'success',
        'group_bills' : data,
        'list_per_change' : list_per_change_return
    })

@allowed_permission(allowed_per = 'Chuyển trạng thái hóa đơn hàng loạt')
def get_batch_type_change_many_status(request):
    if request.method == 'GET':
        bill_status = request.GET.get('list_status', None)
        cus_find = request.GET.get('cus' , None)
        message_send = request.GET.get('message' , None)
        type_product_find = request.GET.getlist('type_product[]' , None)
        date_find = request.GET.get('date', None)
        date_find_from = date_find[6:10] + '/' + date_find[3:5] + '/' + date_find[0:2] + ' 00:00:00'
        date_find_to = date_find[6:10] + '/' + date_find[3:5] + '/' + date_find[0:2] + ' 23:59:59'

        if message_send == 'find_type_product' :
            if None in [bill_status, cus_find, date_find]:
                return JsonResponse({
                    'message' : 'Lỗi'
                })

            query_distinct_type_product = "SELECT Distinct type_product_id, name from [" + str(cus_find) + "|bill] as tb1 INNER JOIN Service_typeproduct as tb2 ON tb1.type_product_id = tb2.id \
                         WHERE status_id = " + str(bill_status) + " and is_po <> 1 and upload_date > '" + str(date_find_from) + "'  and upload_date < '"+ str(date_find_to) +"' and name <> 'TTPP-HDDT'"
            with connection.cursor() as cur:
                type_products = cur.execute(query_distinct_type_product).fetchall()
            return JsonResponse({
                'message': 'success',
                'type_products': [list(x) for x in type_products]
            })
        else:
            if None in [bill_status, cus_find, date_find, type_product_find]:
                return JsonResponse({
                    'message': 'Lỗi'
                })

            query_distinct_batch = "SELECT Distinct ket_thuc_dot_number from [" + str(cus_find) + "|bill]  \
                         WHERE status_id = " + str(bill_status) + " and is_po <> 1 and upload_date > '" + str(
                date_find_from) + "'  and upload_date < '" + str(date_find_to) + "'  and type_product_id in ("+str(','.join(type_product_find))+")"
            with connection.cursor() as cur:
                batch_ends = cur.execute(query_distinct_batch).fetchall()
            return JsonResponse({
                'message': 'success',
                'batch_ends': [list(x) for x in batch_ends]
            })

@allowed_permission(allowed_per = 'Chuyển trạng thái hóa đơn hàng loạt')
def change_status_many_bill_one_time(request):
    if request.method == 'POST':
        cus_id = request.POST.get('hidden_cus', None)
        groups  = request.POST.get('groups', None)
        new_status = request.POST.get('select_new_status', None)
        convert_groups = [("'" + x + "'") for x in groups.split(',')]
        str_group = ','.join(convert_groups)
        with connection.cursor() as cur:
            all_groups = cur.execute("SELECT \
                                     group_hd, is_qa, receiver_number, symbol, type_product_id, status_id \
                                     FROM ["+str(cus_id)+"|bill] \
                                     WHERE group_hd in ("+str_group+") and is_po <> 1 group by group_hd, is_qa, receiver_number, symbol, type_product_id, status_id ").fetchall()

        list_success = []
        list_fail_because_qa = []
        list_fail_because_data = []

        ###Kiểm tra lại quyền chuyển hóa đơn########
        # per_change_status = PermissionChangeStatus.objects.filter(role=request.user.role,
        #                                                           recent_status=symbol_old_status).first().new_status
        # if new_status not in str(per_change_status):
        #     return JsonResponse({
        #         'message': 'No per mission change from ' + symbol_old_status + ' to ' + symbol_new_status,
        #     })

        # nếu new_status = 'W', 'O' thì thoải mái không phải lo gì cả#
        ##Hóa các loại còn lại không chứa QA hoặc phải có ký hiệu hóa đơn
        if new_status in ['W', 'O']:
            list_success = [ "'"+group.group_hd+"'" for group in groups]
        else:
            for group in all_groups:
                if(group.is_qa == 1):
                    list_fail_because_qa.append(group.group_hd)
                elif(not group.symbol):
                    list_fail_because_data.append(group.group_hd)
                else:
                    list_success.append("'"+group.group_hd+"'")

        id_new_status = StatusBill.objects.get(symbol = new_status).id
        user_id = request.user.id
        if list_success:
            old_status_save_log = list(StatusBill.objects.filter(id= all_groups[0].status_id))[0].symbol
            with transaction.atomic():
                with connection.cursor() as cur:
                    cur.execute("UPDATE  ["+str(cus_id)+"|bill] set \
                                      status_id =  CASE WHEN is_po <> 1 THEN %s ELSE status_id END, \
                                      last_change_date = getdate(), user_id_change = %s \
                                 WHERE group_hd in ("+(','.join(list_success))+")", [id_new_status, user_id]).commit()
                    ##other_status save all group
                    cur.execute("INSERT INTO ["+str(cus_id)+"|log_change_status] (listcus_id, user_id, type, old_status, new_status, date_change, other_status) \
                                 VALUES (%s, %s, %s, %s, %s, getdate(), %s)", [cus_id, user_id, 6, old_status_save_log, new_status, ','.join(list_success)])
        ##Hóa đơn muốn sang R thì bắt buộc k QA và chứa receiver
        return JsonResponse({
            'message' : 'success',
            'list_success' : list_success,
            'list_fail_because_qa' : list_fail_because_qa,
            'list_fail_because_data' : list_fail_because_data,
        })

@csrf_exempt
def clear_mac(request):
    if request.method == 'POST':
        if request.user.is_take_photo:
            src_mac_txt = settings.DIR_SAVE_MAC + '/' + str(request.user.cus_id) + '_' + str(request.user.id) + '.txt'
            if os.path.exists(src_mac_txt):
                os.remove(src_mac_txt)
                return JsonResponse({'message': 'clear_done'})
            return JsonResponse({'message': 'not_exist'})
        else:
            return JsonResponse({'message': 'no per_mission'})

@allowed_permission(allowed_per = 'IN pom/inv')
def print_pdf_pom(request):
    if request.method == 'GET':
        message = request.GET.get('message')
        cus = request.GET.get('cus')
        date_search = request.GET.get('date', None)
        date_find_from = date_search[6:10] + '/' + date_search[3:5] + '/' + date_search[0:2] + ' 00:00:00'
        date_find_to = date_search[6:10] + '/' + date_search[3:5] + '/' + date_search[0:2] + ' 23:59:59'
        type = request.GET.get('type', 'pom')

        ##check permisson for cus ##
        manager_cus = request.user.manager_cus.all().values_list('id', flat=True)
        if int(cus) not in list(manager_cus):
            return JsonResponse({
                'message': 'You No manager this cus',
            })

        if message == 'get_type_product':
            if type == 'pom':
                with connection.cursor() as cur:
                    list_type_product = cur.execute("SELECT distinct tb1.type_product_id, tb2.name from ["+str(cus)+"|bill] as tb1 join service_typeproduct as tb2 on tb1.type_product_id = tb2.id  where receiver_number is not null and receiver_number != '' and ISNUMERIC(po_number) = 1 and  upload_date > '" + str(date_find_from) + "'  and upload_date < '"+ str(date_find_to) +"' and tb2.id <> 7 and ket_thuc_dot_number <> 100 order by type_product_id").fetchall()
            else:
                with connection.cursor() as cur:
                    id_r = StatusBill.objects.get(symbol = 'R').id
                    list_type_product = cur.execute("SELECT distinct tb1.type_product_id, tb2.name from [" + str(
                        cus) + "|bill] as tb1 join service_typeproduct as tb2 on tb1.type_product_id = tb2.id  where status_id = "+str(id_r)+"  and po_number like 'I%' and upload_date > '" + str(date_find_from) + "'  and upload_date < '"+ str(date_find_to) +"' and tb2.id <> 7  and ket_thuc_dot_number <> 100 order by type_product_id").fetchall()
            list_return = [ list(x) for x in list_type_product]

            return JsonResponse({
                'message' : 'oke',
                'list_type_product' : list_return
            })
        elif message == 'get_end_batch':
            list_product = ','.join(request.GET.getlist('list_product[]', ['1000']))
            if type == 'pom':
                with connection.cursor() as cur:
                    list_type_product = cur.execute("SELECT distinct ket_thuc_dot_number from [" + str(
                        cus) + "|bill]   where receiver_number is not null and receiver_number != '' and ISNUMERIC(po_number) = 1 and  upload_date > '" + str(
                        date_find_from) + "'  and upload_date < '" + str(
                        date_find_to) + "'  and ket_thuc_dot_number <> 100 and type_product_id in ("+list_product+") order by ket_thuc_dot_number  ").fetchall()
            else:
                with connection.cursor() as cur:
                    id_r = StatusBill.objects.get(symbol='R').id
                    list_type_product = cur.execute("SELECT distinct ket_thuc_dot_number from [" + str(
                        cus) + "|bill] where status_id = " + str(
                        id_r) + "  and po_number like 'I%' and upload_date > '" + str(
                        date_find_from) + "'  and upload_date < '" + str(
                        date_find_to) + "' and  ket_thuc_dot_number <> 100 and type_product_id in ("+list_product+") order by ket_thuc_dot_number  ").fetchall()
            list_return = [list(x) for x in list_type_product]

            return JsonResponse({
                'message': 'oke',
                'list_end_batch': list_return
            })

        elif message == 'get_data':
            list_product = ','.join(request.GET.getlist('list_product[]', ['1000']))
            list_end_batch = ','.join(request.GET.getlist('list_end_batch[]', ['1000']))
            if type == 'pom':
                where_clause = "receiver_number != '' and ISNUMERIC(po_number) = 1 and  upload_date > '" + str(
                        date_find_from) + "'  and upload_date < '" + str(
                        date_find_to) + "'  and ket_thuc_dot_number in ("+list_end_batch+") and type_product_id in (" + list_product + ")   and is_po <> 1 "
            else:
                id_r = StatusBill.objects.get(symbol='R').id
                where_clause = "status_id = " + str(
                        id_r) + "  and po_number like 'I%' and upload_date > '" + str(
                        date_find_from) + "'  and upload_date < '" + str(
                        date_find_to) + "' and  ket_thuc_dot_number in ("+list_end_batch+") and type_product_id in (" + list_product + ")  and is_po <> 1  "
            query_select_all = "SELECT\
                                    group_hd \
                                    ,STRING_AGG(concat(tb1.symbol, '-', tb1.bill_number), '<Br>') bill_number\
                                    ,STRING_AGG(tb1.receiver_number,'|') receiver_number\
                                    ,STRING_AGG(tb1.ket_thuc_dot_number,'|') end_batch_number\
                                    ,STRING_AGG(tb1.src_receiver,'|') src_receiver\
                                    ,STRING_AGG(tb3.name,'|') name_type\
                                FROM \
                                    [dbo].[" + str(cus) + "|bill] as tb1 \
                                INNER JOIN \
                                    [dbo].[service_typeproduct] as tb3 \
                                ON \
                                    tb1.type_product_id = tb3.id \
                                WHERE "+str(where_clause)+"\
                                GROUP BY \
                                    group_hd \
                                ORDER BY \
                                    group_hd "

            base_path = settings.MEDIA_ROOT
            with connection.cursor() as cur:
                all_group_bill_limit = cur.execute(query_select_all).fetchall()
                data = []
                for group in all_group_bill_limit:
                    try:
                        src_receiver = group.src_receiver.split('|')[0]
                        if os.path.exists(base_path + src_receiver):
                            temp = {
                                'group': group.group_hd,
                                'reciever_number': group.receiver_number.split('|')[0],
                                'type_product': group.name_type.split('|')[0],
                                'bill_number': group.bill_number.split('|')[0],
                                'end_batch': group.end_batch_number.split('|')[0],
                                'src_receiver': src_receiver,
                            }
                            data.append(temp)
                    except Exception as e:
                        print(e)
            if len(data):
                return JsonResponse({
                    'message' : 'success',
                    'data' : data
                })

            return JsonResponse({
                'message' : 'no group find'
            })

    elif request.method == 'POST':
        id_cus = request.POST.get('id_cus')
        list_id = ','.join( [ "'" + str(x) + "'" for x in (request.POST.getlist('input_id_print[]', ['0']))])
        with connection.cursor() as cursor:
            list_exist = cursor.execute(
                "select distinct  src_receiver from [" + str(id_cus) + "|bill] where group_hd in (" + str(list_id) + ") and is_po <> 1").fetchall()

        base_path = settings.MEDIA_ROOT
        base_forder = base_path + 'pdf_merge/' + str(request.user.cus_id)
        if not os.path.exists(base_forder):
            os.makedirs(base_forder)
        path_save = '/pdf_pom_inv' + '_' + str(request.user.id) + '.pdf'

        from PyPDF2 import PdfFileMerger
        merger = PdfFileMerger()
        for pdf in list_exist:
            merger.append(base_path + pdf.src_receiver)
        merger.write(base_forder + path_save)
        merger.close()
        return JsonResponse({
            'message': 'oke',
            'data': str(request.user.cus_id) + path_save
        })