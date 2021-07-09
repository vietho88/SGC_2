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
import pyodbc
@allowed_permission(allowed_per = 'Chuyển trạng thái hóa đơn')
def update_status_group_bill(request):
    if request.method == "POST":
        id_group = request.POST.get('input-id-group',None)
        symbol_new_status = request.POST.get('select-status', None)
        symbol_old_status = request.POST.get('input-old-status', None)
        cus_id = request.POST.get('input-cus-id', None)
        type_product_id = request.POST.get('type_product', None)
        user_id = request.user.id
        cus_id_old = request.user.cus.id_old
        if id_group is None or symbol_new_status is None:
            message = "Error"
        else:
            ###Check permission again
            per_change_status = PermissionChangeStatus.objects.filter(role = request.user.role, recent_status = symbol_old_status).first().new_status
            if symbol_new_status not in str(per_change_status):
                return JsonResponse({
                    'message': 'No per mission change from ' + symbol_old_status + ' to ' + symbol_new_status ,
                })

            manager_cus = request.user.manager_cus.all().values_list('id', flat=True)
            if int(cus_id) not in list(manager_cus):
                return JsonResponse({
                    'message': 'You No manager this cus',
                })

            ##check qa with to -> A,H,C , R, V,M : không được QA, phải đầy đủ thông tin
            with connection.cursor() as cur:
                sql_check = cur.execute("SELECT is_qa, symbol,type_product_id,is_po,isnull(po_number,'')+'|'+isnull(vendor_number,'')+'|'+isnull(receiver_number,'')+'|'+isnull(sum_po,'')+'|'+tax_number+'|'+symbol+'|'+bill_number+'|'+city_address+'|'+city_name+bill_date+'|'+result_check+'|'+result_check_luoi as tonghop FROM ["+str(cus_id)+"|bill] WHERE group_hd = '"+str(id_group)+"' ").fetchall() #AND is_po <> 1 
            
            for item in sql_check:
                if symbol_new_status in ['A','R']  :                    
                    if item.is_qa == 1 or '[QA]' in str(item.tonghop):
                            return JsonResponse({
                                'message': 'errorqa',
                            })
                    elif not item.symbol and int(item.type_product_id) !=9 and int(item.is_po)==0  :
                        return JsonResponse({
                            'message': 'erroenough',
                        })            
            ##Néu chuyển từ trạng thái O thì phải thay đổi ket_thuc_dot dua tren bảng CTE va bang moi
            if symbol_old_status == 'O':
                ### 6, 7 ,14 là các ngành hàng , bảng kê của hàng ướt
                date_find = datetime.datetime.now().strftime('%Y-%m-%d')
                date_find_cte = datetime.datetime.now().strftime('%y%m')
                if int(type_product_id) in [6,7,14]:
                    str_find = 'in (6, 7, 14)'
                else:
                    str_find = 'not in (6, 7, 14)'
                cnn_check_cte = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=210.2.93.45,1433;Database=COOP_2019_V1; uid=userai;pwd=userai').cursor()
                max_api_ktt_cte = cnn_check_cte.execute("select (MAX(api_ktt)) as ktd_number from dbo.[CTE|" + str(date_find_cte) + "] where typehd "+str_find+" and UserIdUp = N'" + str(
                    user_id) + "' and Idcus = " + str(cus_id_old) + " and convert(varchar, uploaddate, 23) = '"+date_find+"' and api_ktt is not null").fetchone()
                with connection.cursor() as cursor:
                    max_api_ktt_bill = cursor.execute("SELECT (MAX(api_ktt)) as ktd_number FROM ["+str(cus_id)+"|bill] as tb1 INNER JOIN ["+str(cus_id)+"|log_change_status] as tb2 ON \
                                            tb1.group_hd = tb2.group_hd  WHERE type_product_id "+str_find+" and old_status = 'O' and user_id = "+str(user_id)+" and convert(varchar, date_change, 23) = '"+date_find+"'  and api_ktt is not null").fetchone()
                if str(max_api_ktt_bill[0]) == 'None' and str(max_api_ktt_cte[0]) == 'None':
                    ket_thuc_dot_number = 1
                elif str(max_api_ktt_bill[0]) != 'None' and str(max_api_ktt_cte[0]) != 'None':
                    ket_thuc_dot_number = max(int(max_api_ktt_bill[0]), int(max_api_ktt_cte[0]))
                elif str(max_api_ktt_bill[0]) != 'None':
                    ket_thuc_dot_number = int(max_api_ktt_bill[0])
                else:
                    ket_thuc_dot_number = int(max_api_ktt_cte[0])
                cnn_check_cte.close()

            try:
                find_id_status = StatusBill.objects.get(symbol=symbol_new_status).id
            except StatusBill.DoesNotExist:
                message = "Error"
            else:
                with transaction.atomic():
                    with connection.cursor() as cur:
                        # Nếu là hóa đơn loại O phải cập nhật lại uploadate
                        # Up date status khác PO
                        cur.execute("UPDATE ["+str(cus_id)+"|bill] \
                                    SET \
                                        status_id =  CASE WHEN is_po <> 1 THEN %s ELSE status_id END, \
                                        last_change_date = getdate() " + (', upload_date = getdate()' if symbol_old_status == 'O' else '') + " \
                                        " + (', type_product_id = ' + str(type_product_id) if symbol_old_status == 'O' else '') + " \
                                        " + (', ket_thuc_dot_number = ' + str(ket_thuc_dot_number) if symbol_old_status == 'O' else '') + " \
                                        " + (', has_report = ' + str(1) if symbol_old_status == 'O' and symbol_new_status == 'S' else '') + " \
                                        " + (', user_id_up =   '+str(request.user.id) if symbol_old_status == 'O' else '') + "    \
                                        " + (', status_rpa =   '+"'Receiver'" if symbol_new_status=='R' else ', status_rpa = Null' if symbol_new_status=='A' else '') + " \
                                     WHERE group_hd = '"+str(id_group)+"' " , [find_id_status] )
                        cur.execute("INSERT into ["+str(cus_id)+"|log_change_Status] (listcus_id, user_id, type, old_status, new_status, date_change, group_hd) \
                                     values (%s, %s, %s, %s, %s, getdate(), %s)", [cus_id, request.user.id, 1, symbol_old_status, symbol_new_status, id_group])
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
    list_cus_site_manager = ListCus.objects.all().select_related('site').order_by('site__id').values_list('id', 'name', 'site__name')

    return JsonResponse({
        'list_cus_site' : list(list_cus_site),
        'list_cus_site_manager' : list(list_cus_site_manager),
        'list_rol_site' : list(list_rol_site)
    }, safe=False)

@allowed_permission(allowed_per = 'Tải lên PDF PO')
def upload_pdf_po(request):
    if request.method == "POST":
        cus_id = request.POST.get('input-cus-id', None)
        bill_id = request.POST.get('input-bill-id', None)
        pdf_po = request.FILES.get('input_file_upload_po', None)

        if None in [ cus_id, bill_id, pdf_po]:
            return JsonResponse({
                'message': 'Lỗi, Thiếu tham số yêu cầu !!'
            })
        elif not pdf_po.name.endswith('.pdf'):
            return JsonResponse({
                'message': 'Lỗi, File tải lên không phải là pdf !!'
            })

        with connection.cursor() as cur:
            sql_find = cur.execute("SELECT image_name, group_hd, tax_number FROM ["+str(cus_id)+"|bill] WHERE id = "+str(bill_id)+"").fetchone()
        location_image_po = settings.MEDIA_ROOT + 'img/img_po_upload_by_nganhhang'
        if not os.path.exists(location_image_po):
            os.makedirs(location_image_po)

        try:
            pil_images = pdf2image.convert_from_bytes(pdf_po.read(), poppler_path=settings.BASE_DIR+'/poppler-0.68.0/bin')
        except Exception as e:
            print(e)
            return JsonResponse({
                'message' : 'Lỗi !! Không đọc được file PDF này'
            })
        user_id = request.user.id
        for num, image in enumerate(pil_images):
            name = "HDPO_" + sql_find.image_name.replace(".jpg","") + "_" + sql_find.tax_number + "_" + sql_find.group_hd + "_" + datetime.datetime.now().strftime("%H%M%S") + str(num) + '.jpg'
            image.save(location_image_po + '/' + name)
            src_image = "img/img_po_upload_by_nganhhang/"  + name
            with connection.cursor() as cursor:
                ## thay thế theo thứ tự: type_product_id, image_name, user_id_up, result_check, result_check_luoi, [is_po], [src_image] , [last_change_date]
                cursor.execute("INSERT INTO ["+str(cus_id)+"|bill]  \
                               SELECT \
                                  [listcus_id]\
                                  ,[status_id]\
                                  ,NULL\
                                  ,[group_hd]\
                                  ,'"+ str(name)+"'\
                                  ,[po_number]\
                                  ,[vendor_number]\
                                  ,[receiver_number]\
                                  ,[sum_po]\
                                  ,[tax_number]\
                                  ,[symbol]\
                                  ,[bill_number]\
                                  ,[city_name]\
                                  ,[city_address]\
                                  ,[status_other]\
                                  ,[bill_date]\
                                  ,[ket_thuc_dot_number]\
                                  , "+ str(user_id) +"\
                                  ,  [user_id_change]\
                                  ,[upload_date]\
                                  ,[date_change_kho]\
                                  ,[kt_comment]\
                                  ,[ttpp_comment]\
                                  , '0‡‡‡‡5‡‡‡‡10‡‡‡‡‡‡‡‡‡‡‡'\
                                  , '††††' \
                                  ,[check_trung]\
                                  ,[is_qa]\
                                  ,1 \
                                  ,[is_hddt]\
                                  ,[is_ttpp]\
                                  ,[is_rpa]\
                                  ,[api_ktt]\
                                  ,[has_report]\
                                  ,[report_number]\
                                  ,'"+ str(src_image) +"'\
                                  ,[src_pdf]\
                                  ,[src_xml]\
                                  ,[src_receiver]\
                                  ,[nh_comment]\
                                  ,getdate()\
                                  ,[status_rpa]\
                                  ,[user_receiver] FROM ["+str(cus_id)+"|bill]  WHERE id = "+str(bill_id)+" ").commit()
        return JsonResponse({
            'message' : 'success'
        })

def get_info_detail_bill(request):
    group_hd = request.GET.get('group_hd', None)
    id_cus = request.GET.get('id_cus', None)
    position = request.GET.get('position', None)

    if None in [group_hd, id_cus, position]:
        return JsonResponse({
            'message': 'missing required parameter'
        })

    manager_cus = request.user.manager_cus.all().values_list('id', flat=True)
    if int(id_cus) not in list(manager_cus):
        return JsonResponse({
            'message': 'You No manager this cus',
        })

    with connection.cursor() as cur:
        sql_query = "SELECT  \
                        tb1.status_id,  tb1.vendor_number, tb1.po_number, tb1.receiver_number, tb1.sum_po, tb1.tax_number, tb1.symbol, tb1.bill_number, tb1.city_name, tb1.city_address, tb1.bill_date   \
                        ,tb1.result_check, tb1.result_check_luoi, tb1.is_qa, tb1.is_po, tb1.has_report, tb1.src_image, tb2.name, tb1.type_product_id, tb1.group_hd, tb1.src_pdf, \
                        tb1.src_xml, tb1.src_receiver, isnull(tb1.status_other, '') as status_other, tb1.last_change_date, tb1.upload_date, tb1.id, tb1.status_rpa\
                    FROM [" + str(id_cus) + "|bill] as tb1  \
                    LEFT JOIN Service_typeproduct as tb2 On tb1.type_product_id = tb2.id \
                    WHERE group_hd = '" + str(group_hd) + "' ORDER BY tb1.is_po, id"
        bills = cur.execute(sql_query).fetchall()

        data = []
        for bill in bills:
            if bill.is_po:
                try:
                    result_check = [x for x in (bill.result_check.split('‡'))]
                except Exception:
                    result_check = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
                try:
                    result_check_luoi = [x.split('†') for x in (bill.result_check_luoi.split('‡'))]
                except Exception:
                    result_check_luoi = [['', '', '', '', '']]
                dict_temp = {
                    'id_image': bill.id,
                    'old_status': bill.status_id,
                    'is_po': bill.is_po,
                    'type_bill': bill.type_product_id,
                    'status_HD': 'S',
                    'city_name': bills[0].city_name,
                    'city_address': bills[0].city_address,
                    'type_product': bills[0].type_product_id,
                    'tax_number': bills[0].tax_number,
                    'bill_date': bills[0].bill_date,
                    'symbol': bills[0].symbol,
                    'number_bill': bills[0].bill_number,
                    'po_number': bill.po_number,
                    'sum_po': bill.sum_po.replace(',','') if bill.sum_po else '',
                    'vendor_number': bills[0].vendor_number,
                    'receiver_number': bills[0].receiver_number,
                    'upload_date': bill.upload_date,
                    'last_change_date': bill.last_change_date,
                    'result_check': result_check,
                    'result_check_luoi': result_check_luoi,
                    'status_rpa': bills[0].status_rpa
                }
            else:
                try:
                    result_check = [x for x in (bill.result_check.split('‡'))]
                except Exception:
                    result_check = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
                try:
                    result_check_luoi = [x.split('†') for x in (bill.result_check_luoi.split('‡'))]
                except Exception:
                    result_check_luoi = [['', '', '', '', '', '', '', '']]
                dict_temp = {
                    'id_image': bill.id,
                    'old_status': bill.status_id,
                    'is_po': bill.is_po,
                    'type_bill': bill.type_product_id,
                    'status_HD': 'S',
                    'city_name': bill.city_name,
                    'city_address': bill.city_address,
                    'type_product': bill.type_product_id,
                    'tax_number': bill.tax_number,
                    'bill_date': bill.bill_date,
                    'symbol': bill.symbol,
                    'number_bill': bill.bill_number,
                    'po_number': bill.po_number,
                    'sum_po': bill.sum_po.replace(',','') if bill.sum_po else '' ,
                    'vendor_number': bill.vendor_number,
                    'receiver_number': bill.receiver_number,
                    'upload_date': bill.upload_date,
                    'last_change_date': bill.last_change_date,
                    'result_check': result_check,
                    'result_check_luoi': result_check_luoi,
                    'status_rpa': bill.status_rpa
                }
            data.append(dict_temp)
        context = {
            'data' : {
                'position' : position,
                'bills' : data
            }
        }
    return  JsonResponse(context, safe=False)


def get_log_to_show(request, id_cus, group, id):
    if request.method == "GET":
        with connection.cursor() as cur:
            find_all_log = cur.execute("SELECT type,old_status, new_status, tb2.username, date_change from ["+id_cus+"|log_change_status] as tb1 \
                                        inner join Service_usercoop as tb2 on tb1.user_id = tb2.id where bill_id = %s \
                                         or group_hd = %s or other_status like %s order by tb1.id ", [id, group, '%'+str(group)+'%']).fetchall()
        if not len(find_all_log):
            return JsonResponse({}, safe=False)

        log_change_status, log_change_detail_bill = [], []
        list_des = {
            3: 'Tên công ty',
            4: 'Địa chỉ',
            0: 'Ngành Hàng',
            1: 'Mã Số Thuế',
            2: 'Ngày hóa đơn',
            5: 'Ký hiệu hóa đơn',
            6: 'Số hóa đơn',
            7: 'Số PO/Tranfer',
            8: 'Tổng tiền PO',
            9: 'Mã Vendor',
            10: 'Mã Receiver',
            11: 'Lưới tiền',
            12: 'Lưới hóa đơn',
        }

        for log in find_all_log:
            ##typ3 =1 chuyen trang thai tung bo,typ3 = 6 chuyen trang thai hang loat
            if log.type in ['1', '6']  :
                log_change_status.append(list(log))
            elif log.type == '2':
                detail_log = []
                old = log.old_status.split('❥')
                old[11] = old[11].split('‡|')[0] ### clear result_check   cũ có chứa ‡|PO‡tổng tiền
                new = log.new_status.split('❥')
                for index, (first, second) in enumerate(zip(old, new)):
                    if first != second:
                        detail_log.append(list_des[index])
                if len(detail_log):
                    log_change_detail_bill.append([log.username, log.date_change, detail_log])
        context = {
            'log_change_status' : log_change_status,
            'log_change_detail_bill' : log_change_detail_bill
        }

        if log_change_status == [] and log_change_detail_bill == []:
            return JsonResponse({}, safe=False)

        return JsonResponse(context, safe=False)
def get_log_rpa_to_show(request, id_cus, group, id):
    if request.method == "GET":
        with connection.cursor() as cur:
            find_all_log_rpa = cur.execute("SELECT id,new_status,convert(varchar, date_change, 8)+', '+convert(varchar, date_change, 103) as time FROM dbo.["+id_cus+"|log_change_status] WHERE (group_hd = %s and type = 8) or (bill_id = %s and type = 9) ORDER BY date_change",[group,id]).fetchall()
        dict_log_rpa = {}
        list_log_rpa = []
        for ind,i_log in enumerate(find_all_log_rpa):
            list_log_rpa.append(list(i_log))
        data = {'data':list_log_rpa}
        return JsonResponse(data,safe=False)