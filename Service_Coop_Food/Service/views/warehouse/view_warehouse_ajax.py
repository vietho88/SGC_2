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
from Service.common import common_function
class DataTableHomeWareHouseView(View):
    # #@method_decorator(allowed_user(allowed_roles=[1]))
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
        status_search = StatusBill.objects.filter(symbol = 'S').values_list('id', flat=True)[0]
        cus_ttpp =request.user.cus_id
        ###Search nâng cao
        if check_search_advance == 'true' :
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
            search_for_report_number = "and report_number like '%" + str(report_number_search) + "%'"
            search_for_qa = "and is_qa = '" + str(qa_search) + "'"
            search_for_type_report = "and status_other = '" + str(type_report_search) + "'"
            query_all = "SELECT  group_hd\
                        FROM \
                            [dbo].[" + str(cus_search) + "|bill] as tb1\
                        INNER JOIN \
                                [dbo].[Service_report] as tb2 \
                            ON \
                                tb1.group_hd = tb2.group_bill \
                        WHERE \
                            tb1.listcus_id = " + str(cus_search) + " and tb1.status_id  = " + str(status_search) + "  \
                            and tb2.created_at > '" + date_from_convert + "' and tb2.created_at < '" + date_to_convert + "'  \
                            and tb1.is_po <> 1 and tb2.cus_ttpp_id = "+str(cus_ttpp)+" \
                            "+ (search_for_type_product if type_product_search != '' else '') +"  \
                            "+ (search_for_bill_number if bill_number_seach != '' else '') +"  \
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
                        [dbo].[" + str(cus_search) + "|bill] as tb1 \
                    INNER JOIN \
                        [dbo].[service_statusbill] as tb2 \
                    ON \
                        tb1.status_id = tb2.id \
                    INNER JOIN \
                        [dbo].[service_typeproduct] as tb3 \
                    ON \
                        tb1.type_product_id = tb3.id \
                    INNER JOIN \
                        [dbo].[Service_report] as tb4 \
                    ON \
                        tb1.group_hd = tb4.group_bill \
                    WHERE \
                        tb1.listcus_id = " + str(cus_search) + " and tb1.status_id  = " + str(status_search) + "  \
                        and tb4.created_at > '" + date_from_convert + "' and tb4.created_at < '" + date_to_convert + "'  \
                        and tb1.is_po <> 1 and tb4.cus_ttpp_id = "+str(cus_ttpp)+" \
                        "+ (search_for_type_product if type_product_search != '' else '') +"  \
                        "+ (search_for_bill_number if bill_number_seach != '' else '') +"  \
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
                        group_hd \
                    offset " + str(start_num) + " rows fetch next " + str(length_one_page) + " rows only "
        else:
            query_all = "SELECT  group_hd\
                    FROM \
                        [dbo].[" + str(cus_search) + "|bill] as tb1\
                    INNER JOIN \
                        [dbo].[Service_report] as tb2 \
                    ON \
                        tb1.group_hd = tb2.group_bill \
                    WHERE \
                        tb1.listcus_id = " + str(cus_search) + " and tb1.status_id  = " + str(status_search) + "  \
                        and tb2.created_at > '" + date_from_convert + "' and tb2.created_at < '" + date_to_convert + "'  \
                        and tb1.is_po <> 1 and tb2.cus_ttpp_id = "+str(cus_ttpp)+" \
                    GROUP BY \
                        group_hd \
                    ORDER BY \
                        group_hd "

            query2 = "SELECT\
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
                    [dbo].[" + str(cus_search) + "|bill] as tb1 \
                INNER JOIN \
                    [dbo].[service_statusbill] as tb2 \
                ON \
                    tb1.status_id = tb2.id \
                INNER JOIN \
                    [dbo].[service_typeproduct] as tb3 \
                ON \
                    tb1.type_product_id = tb3.id \
                INNER JOIN \
                    [dbo].[Service_report] as tb4 \
                ON \
                    tb1.group_hd = tb4.group_bill \
                WHERE \
                    tb1.listcus_id = " + str(cus_search) + " and tb1.status_id  = " + str(status_search) + "  \
                    and tb4.created_at > '" + date_from_convert + "' and tb4.created_at < '" + date_to_convert + "'  \
                    and tb1.is_po <> 1 and tb4.cus_ttpp_id = "+str(cus_ttpp)+" \
                GROUP BY \
                    group_hd \
                ORDER BY \
                    group_hd \
                offset " + str(start_num) + " rows fetch next " + str(length_one_page) + " rows only "

        with connection.cursor() as cur:
            total_record = len(cur.execute(query_all).fetchall())
            all_group_bill_limit = cur.execute(query2).fetchall()
            data = []
            for group in all_group_bill_limit:
                try:
                    upload_date = datetime.datetime.strptime(group[5].split('|')[0], '%b %d %Y %I:%M%p').strftime('%d/%m/%Y %H:%M:%S')
                    last_change_date = datetime.datetime.strptime(group[16].split('|')[0], '%b %d %Y %I:%M%p').strftime('%d/%m/%Y %H:%M:%S') if group[16] else upload_date
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
                except Exception as e :
                    print(e)

        context = {
            "draw": draw,
            "recordsTotal": total_record,
            "recordsFiltered": total_record,
            "data": data
        }
        return JsonResponse(context, safe=False)

    # #@method_decorator(allowed_user(allowed_roles=[1]))
    def post(self, request):
        pass
