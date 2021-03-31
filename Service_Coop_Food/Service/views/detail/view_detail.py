from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,HttpResponseRedirect, Http404
from Service.decorators import allowed_user, allowed_permission
from django.utils.decorators import method_decorator
from Service.models import TypeProduct,StatusBill,PermissionChangeStatus,ListCus
from django.db import  connection, transaction
from django.shortcuts import get_object_or_404
from django.contrib import  messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
# Create your views here.
class DetailBillView(View):
    @method_decorator(allowed_permission(allowed_per='Xem hóa đơn'))
    def get(self, request, id_cus, id, index):
        if int(id_cus) not in request.session['list_cus_manager']:
            raise PermissionDenied
        bill_id_po = None
        with connection.cursor() as cur:
            sql_query = "SELECT  \
                            tb1.status_id,  tb1.vendor_number, tb1.po_number, tb1.receiver_number, tb1.sum_po, tb1.tax_number, tb1.symbol, tb1.bill_number, tb1.city_name, tb1.city_address, tb1.bill_date   \
                            ,tb1.result_check, tb1.result_check_luoi, tb1.is_qa, tb1.is_po, tb1.has_report, tb1.src_image, tb2.name, tb1.type_product_id, tb1.group_hd, tb1.src_pdf, \
                            tb1.src_xml, tb1.src_receiver, isnull(tb1.status_other, '') as status_other, tb1.last_change_date, tb1.upload_date, tb1.id\
                        FROM ["+str(id_cus)+"|bill] as tb1  \
                        LEFT JOIN Service_typeproduct as tb2 On tb1.type_product_id = tb2.id \
                        WHERE group_hd = '"+str(id)+"' ORDER BY tb1.is_po, id"
            bills = cur.execute(sql_query).fetchall()

        #check bill exists
        if len(bills):
            try:
                count_bills = len(bills)
                image_bills = [ x.src_image for x in bills ]
                bill = bills[int(index)]
            except Exception as e:
                print(e)
                raise Http404
        else:
            raise Http404

        ## if bill là PO
        if bill.is_po:
            is_po = True
            try:
                result_check = [x for x in (bill.result_check.split('‡'))]
            except Exception:
                result_check = ['', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '','', '']
            try:
                result_check_luoi = [x.split('†') for x in (bill.result_check_luoi.split('‡'))]
            except Exception:
                result_check_luoi = [['','','','','']]
            bill_id_po = bill.id
            bill = bills[0] ####Vì không thể có TH chỉ có 1 mình PO, nếu index 0 chắc chắn k phải PO(lấy data)
        else:
            is_po = False
            try:
                result_check = [x for x in (bill.result_check.split('‡'))]
            except Exception:
                result_check = ['', '', '', '', '', '', '', '', '','', '', '', '', '', '', '', '', '','', '']
            try:
                result_check_luoi = [x.split('†') for x in (bill.result_check_luoi.split('‡'))]
            except Exception:
                result_check_luoi = [['', '', '', '', '', '', '', '']]

        ###only type_product có type = 1,2(Hóa đơn) và show
        list_type_product = TypeProduct.objects.filter(type__in = [1,2], is_show = True).values('id', 'name')
        status_bill = get_object_or_404(StatusBill, pk=bill[0]).symbol
        find_per_change_status = PermissionChangeStatus.objects.filter(recent_status=status_bill, role=request.user.role.id)
        if find_per_change_status and find_per_change_status[0].new_status :
            list_per_change_status = find_per_change_status[0].new_status.split('|')
        else:
            list_per_change_status = []

        ## if hoa don loai C thi tao ma QR de up hoa don thay the
        name_detail = str(id) + "#" +str(bill.upload_date)+ "#" +  "C"  + "#" + str(bill.status_other) + "#" + str(id_cus)
        content_qr = "sgcoop|" + str(id_cus)  + "|HD|" + name_detail + "|" + 'This is name company'

        context = {
            'bill' : bill,
            'index' : index,
            'id' : id,
            'id_cus' : int(id_cus),
            'list_type_product' : list_type_product,
            'list_per_change_status' : list_per_change_status,
            'status_bill' : status_bill,
            'result_check' : result_check,
            'result_check_luoi' : result_check_luoi,
            'count_bills' : count_bills,
            'image_bills' : image_bills,
            'is_po' : is_po,
            'bill_id_po' : bill_id_po,
            'cus_name' : ListCus.objects.filter(id=id_cus).first().name,
            'content_qr' : content_qr

        }
        return render(request, 'detail/base_detail.html', context)

    @method_decorator(allowed_permission(allowed_per ='Chỉnh sửa bộ hóa đơn'))
    def post(self, request, id_cus, id, index):
        type_product = request.POST.get('select-industry', '')
        tax_number = request.POST.get('input-tax-number', '')
        bill_date = request.POST.get('input-date-bill', '')
        company_name = request.POST.get('input-name-company', '')
        company_address = request.POST.get('input-address-company', '')
        bill_symbol = request.POST.get('input-symbol-bill', '')
        bill_number = request.POST.get('input-bill-number', '')
        po_number = request.POST.get('input-po-number', '')
        po_sum = request.POST.get('input-po-money', '').strip().replace(',','')
        vendor = request.POST.get('input-vendor-code', '')
        receiver = request.POST.get('input-receiver-code', '')
        result_check = request.POST.getlist('input-result_check[]', '')
        result_check_luoi = request.POST.getlist('input-result_check_luoi[]', '')
        is_po = request.POST.get('input_hidden_is_po', '')
        bill_id = request.POST.get('input_hidden_id_bill', '')
        # old_status = request.POST.get('input_hidden_old_status', '')
        position = request.POST.get('input_hidden_position', '0')
        is_qa = 0

        if is_po.lower() == 'true' or str(is_po) == '1':
            result_check_luoi_oke = self.split_result_check_luoi(result_check_luoi, 5)
        else:
            result_check_luoi_oke = self.split_result_check_luoi(result_check_luoi, 8)

        with transaction.atomic():
            ##update thong tin chung của bộ và result check, result_check_luoi cua chinh no
            sql_update_common = "UPDATE ["+str(id_cus)+"|bill] SET type_product_id  = %s \
                                                            ,tax_number = %s\
                                                            ,bill_date = %s\
                                                            ,city_name = %s\
                                                            ,city_address = %s\
                                                            ,symbol = %s\
                                                            ,bill_number = %s\
                                                            ,po_number = %s\
                                                            ,sum_po = %s\
                                                            ,vendor_number = %s\
                                                            ,receiver_number = %s\
                                                            ,last_change_date = getdate() \
                                                            ,result_check = CASE WHEN id = "+str(bill_id)+ " THEN %s ELSE result_check END \
                                                            ,result_check_luoi = CASE WHEN id = "+str(bill_id)+ " THEN %s ELSE result_check_luoi END \
                                                            ,is_qa = %s\
                                WHERE group_hd = '"+str(id)+"'"
            list_updates = [
                type_product, tax_number, bill_date, company_name, company_address,
                bill_symbol,bill_number, po_number, po_sum, vendor,
                receiver, '‡'.join([x.strip().replace(',','') for x in  result_check]), result_check_luoi_oke
            ]
            new_values_save_log = '❥'.join(list_updates)
            if '[QA]' in new_values_save_log:
                is_qa = 1
            else:
                ##Check 1 lần nữa ở các hóa đơn còn lại ở bộ (result_check và result_chẹck_luoi)
                with connection.cursor() as cur:
                    check_qa_other = cur.execute("SELECT STRING_AGG(result_check, '❥') , STRING_AGG(result_check_luoi, '❥')  FROM ["+str(id_cus)+"|bill] WHERE group_hd = '"+str(id)+"' and id <> "+str(bill_id)+" ").fetchone()
                if None not in check_qa_other:
                    str_check_qa_other = '❥'.join(list(check_qa_other))
                    if '[QA]' in str_check_qa_other:
                        is_qa = 1
            with connection.cursor() as cur:
                sql_old_values_save_log = cur.execute("SELECT type_product_id, tax_number, bill_date, city_name, city_address, \
                                                        symbol,bill_number, po_number, sum_po, vendor_number, \
                                                        receiver_number, result_check, result_check_luoi  FROM ["+str(id_cus)+"|bill] WHERE iD = "+str(bill_id)+"").fetchone()
            old_values_save_log = '❥'.join(str(x) if x != None else '' for x in sql_old_values_save_log)
            list_updates.append(is_qa)
            with connection.cursor() as cur:
                cur.execute(sql_update_common, list_updates)
                cur.execute("INSERT INTO ["+str(id_cus)+"|log_change_status] (listcus_id, user_id, type, date_change, old_status, new_status, bill_id) \
                             VALUES (%s, %s, %s, getdate(), %s, %s, %s)", [id_cus, request.user.id, 2, old_values_save_log, new_values_save_log,bill_id]) ###update log
            messages.success(request, 'Sửa thông tin thành công !!')
            url_recent = request.META.get('HTTP_REFERER')
            url_split = url_recent.split('/')
            url_split[-1] = str(position)
            url = '/'.join(url_split)
        return HttpResponseRedirect(url)

    @staticmethod
    def split_result_check_luoi(l, n):
        if len(l) < n:
            return '††††'
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


def dowload_media_file(request, type, group_hd, bill_id, cus_id):
    cus_manager = request.user.manager_cus.all().values_list('id', flat=True)
    if int(cus_id) not in list(cus_manager):
        return HttpResponse('You no manager this cus !!')

    if str(type) not in ['pdf', 'img', 'xml']:
        return HttpResponse("File type "+type+" not accept dowload")

    dict_type_select = {
        'img' : 'src_img',
        'pdf' : 'src_pdf',
        'xml' : 'src_xml',
        'receiver' : 'src_receiver',
    }
    query = "SELECT "+dict_type_select[type]+" FROM ["+str(cus_id)+"|bill] WHERE group_hd = '"+str(group_hd)+"' and id = "+str(bill_id)+""
    with connection.cursor() as cursor:
        find_src = cursor.execute(query).fetchone()

    if find_src is  None:
        raise Http404


    try:
        src = settings.MEDIA_ROOT +  find_src[0]
        with  open(src, 'rb') as file:
            respone = HttpResponse(file.read(), content_type="")
            respone['Content-Disposition'] = 'attachment; filename = ' + src.split('/')[-1]
            return respone
    except Exception as e:
        raise Http404
        return HttpResponse("File not exist or you no have permission!!")


