from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,HttpResponseRedirect , Http404, JsonResponse
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
import re
# Create your views here.

class DataTableHomeInvoiceListView(View):
    @method_decorator(allowed_permission(allowed_per='Xem bảng kê'))
    def get(self, request):
        data = []

        date_from = request.GET.get ('date_from', datetime.datetime.now().strftime('%d/%m/%Y'))
        date_to = request.GET.get ('date_to', datetime.datetime.now().strftime('%d/%m/%Y'))
        cus_search = request.GET.get ('select_cus', request.user.manager_cus.all().values_list('id',flat=True)[0])
        type_product = request.GET.getlist('select_type[]', ['14','15'])
        po_number = request.GET.get ('po_number', '')
        bk_number_search = request.GET.get ('bk_number_search', '')
        receiver_number = request.GET.get ('receiver_number', '')
        vendor_number = request.GET.get ('vendor_number', '')
        is_qa = request.GET.get ('select_qa', '')
        is_nhan_hang = request.GET.get ('select_nhan_hang', '')
        draw = request.GET.get('draw')
        start_num = int(request.GET.get('start', 0))
        length_one_page = int(request.GET.get('length', 25))

        ###Clear "'" tranh tan cong sql injection
        po_number = re.sub('[\', \"]', '', po_number)
        bk_number_search = re.sub('[\', \"]', '', bk_number_search)
        receiver_number = re.sub('[\', \"]', '', receiver_number)
        vendor_number = re.sub('[\', \"]', '', vendor_number)

        ####order datatable custom#####
        number_fieds_sort = request.GET.get('order[0][column]', '')
        type = request.GET.get('order[0][dir]', '')
        query_order = 'tb1.id '
        if number_fieds_sort:
            query_order = self.find_order(number_fieds_sort, type)


        qa_search = "and is_qa = "+ str(is_qa)
        if is_nhan_hang == '1':
            nhan_hang_search = "and (po_number != '' and po_number != 'QA' and po_number is not null) "
        else:
            nhan_hang_search = "and (po_number = '' or po_number = 'QA' or po_number is null) "
        vendor_number_search = "and vendor_number like '%" + str(vendor_number) + "%'"
        receiver_number_search = "and receiver_number like '%" + str(receiver_number) + "%'"
        po_number_search = "and po_number like '%" + str(po_number) + "%'"
        type_product_search = "and type_bk in (" + ",".join(type_product) + ")"
        date_from_convert = date_from[6:10] + '/' + date_from[3:5] + '/'+date_from[0:2] + ' 00:00:00'
        date_to_convert = date_to[6:10] + '/' + date_to[3:5] + '/'+date_to[0:2] + ' 23:59:59'

        query_str_all = "SELECT id FROM ["+str(cus_search)+"|bk]  \
                              WHERE  \
                                upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'  \
                             "+ (qa_search  if is_qa != '' else '' )  +" \
                             "+ (nhan_hang_search  if is_nhan_hang != '' else '' )  +" \
                             "+ (vendor_number_search  if vendor_number != '' else '' )  +" \
                             "+ (receiver_number_search  if receiver_number != '' else '' )  +" \
                             "+ (po_number_search  if po_number != '' else '' )  +" \
                             " + ("and bk_number like '%" + str(bk_number_search) + "%'" if bk_number_search != '' else '') + " \
                             "+ (type_product_search  if len(type_product) > 0  else '' )  + " "

        query_str = "SELECT tb1.id as id_list_invoice, type_bk, bk_number, po_number, receiver_number, vendor_number, is_qa, result_check, name, upload_date, src_img , last_change_date FROM ["+str(cus_search)+"|bk] as tb1 \
                        INNER JOIN service_typeproduct  as tb2 ON tb1.type_bk = tb2.id \
                        WHERE  \
                             upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'  \
                             "+ (qa_search  if is_qa != '' else '' )  +" \
                             " + (nhan_hang_search if is_nhan_hang != '' else '') + " \
                             "+ (vendor_number_search  if vendor_number != '' else '' )  +" \
                             "+ (receiver_number_search  if receiver_number != '' else '' )  +" \
                             "+ (po_number_search  if po_number != '' else '' )  +" \
                             " + ("and bk_number like '%" + str(bk_number_search) + "%'" if bk_number_search != '' else '') + " \
                             "+ (type_product_search  if len(type_product) > 0 else '' )  +" \
                        ORDER BY "+query_order+" \
                        OFFSET " + str(start_num) + " ROWS FETCH NEXT " + str(length_one_page) + " ROWS ONLY  "
        with connection.cursor() as cur:
            invoice_lists_all = cur.execute(query_str_all).fetchall()
            invoice_lists = cur.execute(query_str).fetchall()

        cus_managers = request.user.manager_cus.all().values('id', 'name')
        ###3 là loại bảng kê
        invoice_list_types = TypeProduct.objects.filter(type = 3).values('id', 'name')
        if not cus_managers.exists():
            cus_managers = [[request.user.cus.id, request.user.cus.name]]

        for invoice in invoice_lists:
            try:
                # upload_date = datetime.datetime.strptime(invoice.upload_date, '%b %d %Y %I:%M%p').strftime('%d/%m/%Y %H:%M:%S')
                temp = {
                    'type_bk': invoice.name,
                    'bk_number': invoice.bk_number,
                    'po_number': invoice.po_number,
                    'receiver_number': invoice.receiver_number,
                    'vendor_number': invoice.vendor_number,
                    'upload_date': invoice.upload_date,
                    'is_qa': invoice.is_qa,
                    'src_img': invoice.src_img,
                    'id_list_invoice': invoice.id_list_invoice,
                    'last_change_date': invoice.last_change_date,

                }
                data.append(temp)
            except Exception as e:
                print(e)
        context = {
            "draw": draw,
            "recordsTotal": len(invoice_lists_all),
            "recordsFiltered": len(invoice_lists_all),
            "data": data
        }
        return JsonResponse(context, safe=False)


    @staticmethod
    def find_order(field, type):
        dict_option = {
            0: 'tb1.id',
            1: 'bk_number',
            2: 'type_bk',
            3: 'po_number',
            4: 'receiver_number',
            5: 'vendor_number',
            6: 'upload_date',
            7: 'last_change_date',
            8: 'is_qa',
            9: 'po_number',
        }
        return dict_option[(int(field))] + ' ' + type


def get_log_to_show_bk(request, id_cus, id):
    if request.method == "GET":
        with connection.cursor() as cur:
            find_all_log = cur.execute("SELECT type,old_status, new_status, tb2.username, date_change from [" + id_cus + "|log_change_status] as tb1 \
                                           inner join Service_usercoop as tb2 on tb1.user_id = tb2.id where bill_id = %s \
                                            and type = 5 order by tb1.id  ",
                                       [id ]).fetchall()
        if not len(find_all_log):
            return JsonResponse({}, safe=False)

        log_change_bk = []
        list_des = {
            1: 'Số bảng kê',
            0: 'Loại bảng kê',
            2: 'Số PO',
            3: 'Số Receiver',
            4: 'Mã Vendor',
            5: 'Lưới thông tin',
            6: 'Trạng thái QA',
        }

        for log in find_all_log:
            detail_log = []
            old = log.old_status.split('❥')
            new = log.new_status.split('❥')
            for index, (first, second) in enumerate(zip(old, new)):
                if first != second:
                    detail_log.append(list_des[index])
            if len(detail_log):
                log_change_bk.append([log.username, log.date_change, detail_log])

        if not len(log_change_bk):
            return JsonResponse({}, safe=False)

        context = {
            'log_change_bk': log_change_bk
        }

        return JsonResponse(context, safe=False)

def find_bill_to_print_pom(request):
    if request.method == 'GET':
        id_cus = request.GET.get("id_cus", None)
        list_product = ','.join(request.GET.getlist('type_product[]', ['14']))
        date_search = request.GET.get('date', None)
        date_find_from = date_search[6:10] + '/' + date_search[3:5] + '/' + date_search[0:2] + ' 00:00:00'
        date_find_to = date_search[6:10] + '/' + date_search[3:5] + '/' + date_search[0:2] + ' 23:59:59'
        with connection.cursor() as cursor:
            list_invoice = cursor.execute("select bk_number, receiver_number , src_receiver, id, vendor_number from  [" + str(
                id_cus) + "|bk] where type_bk in ("+str(list_product)+")  and receiver_number <> '' and upload_date > %s  and upload_date < %s ",
                                          [date_find_from, date_find_to]).fetchall()
        if len(list_invoice):
            base_path = settings.MEDIA_ROOT
            list_exist = [ list(x) for x in list_invoice if os.path.exists(base_path + x.src_receiver)]
            return JsonResponse({
                'message' : 'success',
                'data' : list_exist
            })

        else:
            return JsonResponse({'message' : 'no data'})

    elif request.method == 'POST':
        id_cus = request.POST.get('id_cus')
        list_id = ','.join(request.POST.getlist('input_id_print[]', ['0']))
        with connection.cursor() as cursor:
            list_exist = cursor.execute("select src_receiver from ["+str(id_cus)+"|bk] where id in ("+str(list_id)+")").fetchall()

        base_path = settings.MEDIA_ROOT
        base_forder = base_path + '/pdf_merge/' + str(request.user.cus_id)
        if not os.path.exists(base_forder):
            os.makedirs(base_forder)
        path_save = '/pdf_pom_bk' + '_' + str(request.user.id) + '.pdf'

        from PyPDF2 import PdfFileMerger
        merger = PdfFileMerger()
        for pdf in list_exist:
            merger.append(base_path + pdf.src_receiver)
        merger.write(base_forder + path_save)
        merger.close()
        return JsonResponse({
            'message' : 'oke',
             'data' :  str(request.user.cus_id) + path_save
        })