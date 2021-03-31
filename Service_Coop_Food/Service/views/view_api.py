from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from Service.decorators import allowed_user
from django.utils.decorators import method_decorator
from Service.models import StatusBill,ListCus
from django.core.paginator import Paginator
from Service.forms import *
from django.urls import reverse
import json
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib import messages
import datetime
from django.db import  connection
from django.http import Http404
from django.db.transaction import atomic
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
import re
from io import BytesIO
import pandas as pd
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os

class HelloView(APIView):
    # permission_classes = (IsAuthenticated,)
    def get(self, request):
        content = {
            'message': 'Hello, api'
        }
        return Response(content)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def api_check_exist_bill(request):
#     cus_id = request.GET.get('id_cus', None)
#     tax_number = request.GET.get('tax_number', None)
#     bill_number = request.GET.get('bill_number', None)
#     message = ''
#     image_name = ''
#     if None in [cus_id, tax_number, bill_number]:
#         message = 'Error! Truyền thiếu tham số!!'
#     else:
#         cus_id = re.sub(r'[^\w]', '', cus_id)
#         tax_number = re.sub(r'[^\w]', '', tax_number)
#         bill_number = re.sub(r'[^\w]', '', bill_number)
#         try:
#             with connection.cursor() as cur:
#                 find_bill = cur.execute("SELECT image_name from ["+str(cus_id)+"|bill] WHERE tax_number like '%"+str(tax_number)+"%' and bill_number like  '%"+str(bill_number)+"%' ").fetchone()
#             if find_bill:
#                 message = 'Thành công'
#                 image_name = find_bill.image_name
#             else:
#                 message = 'Chưa tồn tại tên ảnh'
#         except:
#             message = 'Error! Bảng này chưa tồn tại trên hệ thống!!'
#     context = {
#         'message': message,
#         'image_name': image_name,
#     }
#     return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_export_excel(request):
    '''
        api to dowload file excel use in rpa
    '''
    list_data_bill = []
    list_data_po = []
    list_group = []

    date_send = request.GET.get('date', None)  ###định dạng dd/md/YYYY
    date = date_send[6:10] + date_send[3:5] + date_send[:2]
    status = request.GET.get('status', None)
    select_nganh_hang = request.GET.getlist('select_nganh_hang')
    list_nganh_hang_search = ','.join(select_nganh_hang)
    #id_cus = request.GET.get('cus_id', None)
    id_cus = request.user.cus_id

    if None in [date_send, status, select_nganh_hang, id_cus]:
        return JsonResponse({
            'message': 'Missing para'
        })

    str_status = StatusBill.objects.get(symbol = status).id
    list_cus_manager = request.user.manager_cus.all().values_list('id', flat=True)
    if int(id_cus) not in list_cus_manager:
        return JsonResponse({
            'message': 'use not permission in cus'
        })
    id_user = request.user.id

    with connection.cursor() as cursor:
        find_dot_sql = cursor.execute(
            "SELECT distinct(ket_thuc_dot_number) from dbo.[" + str(id_cus) + "|bill] as tb1 join service_statusbill on tb1.status_id = service_statusbill.id where service_statusbill.symbol = '" + str(
                status) + "' and convert(varchar, upload_date, 112) = '" + date + "' ").fetchall()
        if  len(find_dot_sql) > 0:
            str_dots = ','.join([str(x[0]) for x in find_dot_sql])
        else:
            return JsonResponse({
                'message': 'No batch found!!'
            })
        sql_list_bill = cursor.execute("SELECT  tb1.result_check, isnull(tb1.result_check_luoi,'') as result_check_luoi, tb1.image_name, tb1.id, tb3.name, \
                   isnull(tb2.name,'') as name, tb1.status_id, tb1.po_number,tb1.sum_po, tb1.group_hd , \
                   convert(varchar, tb1.upload_date, 120) as N'Ngày Tạo', convert(varchar, tb1.last_change_date, 120) as last_change_date, \
                   tb1.status_other, tb1.ket_thuc_dot_number, tb1.is_qa, tb1.tax_number, tb1.is_qa,  tb1.is_hddt, tb1.vendor_number, tb1.symbol, tb1.bill_number, tb1.bill_date, \
                   tb1.city_name, tb1.city_address,  \
                   tb1.status_rpa, tb1.receiver_number,convert(varchar, tb1.upload_date, 103) as upload_date, tb3.address, tb3.name as name_cus FROM dbo.[" + str(id_cus) + "|bill] as tb1 \
                    INNER JOIN service_typeproduct as tb2 ON tb1.type_product_id = tb2.id INNER JOIN service_Listcus as tb3 ON tb3.Id = tb1.listcus_id \
                   WHERE tb1.is_po <> 1 and  tb1.ket_thuc_dot_number in (" + str(str_dots) + ")  and tb1.status_id = "+str(str_status)+"  and tb1.type_product_id in  (" + str(list_nganh_hang_search) + ")  \
                    and convert(varchar, upload_date, 112) = '" + date + "' and result_check is not null  order by tb1.ket_thuc_dot_number, tb1.type_product_id ,tb1.last_change_date, tb1.upload_date").fetchall()

    if len(sql_list_bill) == 0:
        return JsonResponse({
            'message': 'No data to export!!'
        })

    for bill in sql_list_bill:
        temp = [bill.status_rpa, bill.name_cus, bill.name, bill.symbol, bill.bill_number, bill.bill_date, bill.tax_number, bill.city_name, bill.city_address] + bill.result_check_luoi.split('†') + bill.result_check.split('‡')[0:-3]  + ['', bill.po_number, bill.sum_po,'QA' if bill.is_qa else '', bill.vendor_number, bill.group_hd, bill.image_name, bill.receiver_number, bill.upload_date]
        list_data_bill.append(temp)
        list_group.append(str(bill.group_hd))
    str_list_group = str(','.join(["'" + x + "'" for x in list_group]))
    with connection.cursor() as cursor:
        sql_list_po = cursor.execute("SELECT group_hd, STRING_AGG(bill_number, ',') as bill_number,  STRING_AGG(result_check_luoi ,',') as result_check_luoi, STRING_AGG(is_po ,',')\
                            as is_po, STRING_AGG(is_qa ,',') as is_qa,  po_number  FROM dbo.[" + str(id_cus) + "|bill] WHERE  \
                           group_hd in ("+str_list_group+")  group by group_hd, po_number  ").fetchall()
    for po in sql_list_po:
        if '1' in po.is_po:
            po_number = po.po_number
            is_qa  = po.is_qa.split(',')[0]
            bill_number = ','.join(list(set((filter(None, (po.bill_number.split(',')))))))
            for item in  po.result_check_luoi.split('‡'):
                temp = [ po_number ] + item.split('†')[:5] + ['QA' if is_qa == 1  else '', bill_number]
                list_data_po.append(temp)
    df_bill = pd.DataFrame(list_data_bill,
                             columns=["Status", "Tên doanh nghiệp", "Số mẫu hóa đơn", "Ký hiệu hóa đơn",
                                      "Số hóa đơn", "Ngày", "Mã số thuế người bán/người mua", "Công Ty",
                                      "Địa chỉ", "Mã hàng hóa/Dịch vụ", "Tên hàng hóa/Dịch vụ/Diễn giải",
                                      "Đơn vị tính", "Số lượng", "Đơn giá", "Thuế VAT Mặt Hàng (%)",
                                      "Tiền thuế VAT Mặt hàng", "Thành tiền", "Cộng tiền HÀng Hóa(0%)",
                                      "Thuế VAT hóa đơn (0%)", "Tiền thuế VAT hoá đơn (0%)",
                                      "Tổng tiền thanh toán (0%)", "Cộng tiền HÀng Hóa(5%)",
                                      "Thuế VAT hóa đơn (5%)", "Tiền thuế VAT hoá đơn (5%)",
                                      "Tổng tiền thanh toán (5%)", "Cộng tiền HÀng Hóa(10%)",
                                      "Thuế VAT hóa đơn (10%)", "Tiền thuế VAT hoá đơn (10%)",
                                      "Tổng tiền thanh toán (10%)", "Cộng tiền HÀng Hóa(...%)",
                                      "Thuế VAT hóa đơn (...%)", "Tiền thuế VAT hoá đơn (...%)",
                                      "Tổng tiền thanh toán (...%)", "Tổng cộng tiền Hàng Hóa",
                                      "Tổng cộng tiền thuế VAT hoá đơn", "Tổng cộng tiền thanh toán",
                                      "Hình thức thanh toán", "Mã PO", "Tổng tiền PO", "Thực Trạng",
                                      "Mã Vendor", "HDgroup", "Tên ảnh", "Receiver", "UploadDate"])
    df_po = pd.DataFrame(list_data_po,
                             columns=["Mã PO", "Mã SKU", "Đơn giá", "SL trước sửa", "SL sau sửa", "Thành tiền",
                                      "Note", "Số HD"])
    with BytesIO() as byte_io:
        writer = pd.ExcelWriter(byte_io, engine='xlsxwriter')
        df_bill.to_excel(writer, sheet_name='Sheet', index=False)
        df_po.to_excel(writer, sheet_name='Sheet1', index=False)
        writer.save()
        response = HttpResponse(byte_io.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename= export_excel.xlsx'
        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_export_excel_invoice_list(request):
    list_invoice_list = []
    list_temp = []

    date = request.GET.get('date', None)
    type_invoice_list = request.GET.get('type_bang_ke', None)
    # cus_id = request.GET.get('cus_id', None)
    cus_id = request.user.cus_id
    if None in [date, type_invoice_list, cus_id]:
        return JsonResponse({
            'message' : 'missing para require'
        })


    list_cus_manager = request.user.manager_cus.all().values_list('id', flat=True)
    if int(cus_id) not in list_cus_manager:
        return JsonResponse({
            'message' : 'use not permission in cus'
        })
    name_cus = ListCus.objects.get(pk = cus_id).name

    with connection.cursor() as cursor:
        sql_list_invoice = cursor.execute(
            "SELECT tb2.name, tb1.image_name, tb1.is_qa, tb1.vendor_number, tb1.bk_number,  tb1.result_check FROM [dbo].[" + str(cus_id) + "|bk] as tb1 inner join service_typeproduct as tb2 on tb1.type_bk = tb2.id where CONVERT(varchar,tb1.upload_date,103) = '" + date + "'   and tb1.type_bk = " + str(type_invoice_list) + "  ").fetchall()
    if len(sql_list_invoice) == 0:
        return JsonResponse({
            'message': 'error : Not data to export'
        }, safe=False)
    for num, invoice in enumerate(sql_list_invoice):
        list_sku = []
        list_amount = []
        list_money = []
        try:
            for line in invoice.result_check.split("‡"):
                list_sku.append(line.split("†")[0])
                list_amount.append(line.split("†")[1])
                list_money.append(line.split("†")[2])
            sku = "+".join(list_sku)
            amount = "+".join(list_amount)
            money = "+".join(list_money)
        except :
            pass
        list_temp = [
            num + 1, '', name_cus, invoice.name , invoice.bk_number, '', sku, amount,
            money, invoice.vendor_number, 'QA' if invoice.is_qa == 1 else '', invoice.image_name
        ]
        list_invoice_list.append(list_temp)

    pf_invoice_list = pd.DataFrame(list_invoice_list,
                            columns=['STT', 'Status', 'Tên Doanh Nghiệp', 'Loại Bảng Kê', 'Số Bảng Kê',
                                     'Tên Nhà Cung Cấp', 'SKU', 'Số Lượng', 'Đơn Giá', 'Mã Vendor',
                                     'Thực Trạng', 'Tên Ảnh'])

    with BytesIO() as byte_io:
        writer = pd.ExcelWriter(byte_io, engine='xlsxwriter')
        pf_invoice_list.to_excel(writer, sheet_name='Sheet', index=False)
        writer.save()
        response = HttpResponse(byte_io.getvalue(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename= export_excel_bk.xlsx'
        return response

#####function check table exist ######
def checkExistTable(name):
    with connection.cursor() as cursor:
        sql_checkk = cursor.execute("SELECT OBJECT_ID(N'dbo." + name + "|bill') AS 'Object ID'").fetchone()
        if sql_checkk[0] != None:
            return True
        else:
            return False

##### API update HDDT ############
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_Invoice_Electronic(request):
    idcus = str(request.user.cus_id)
    numInvoice = request.GET.get('numInvoice', None)
    symbol = request.GET.get('symbol', None)
    listBody = ['numInvoice', 'symbol']
    listError = []
    for iBody in listBody:
        if (eval(iBody) is None) or (eval(iBody) == []):
            listError.append(iBody)
    if listError != []:
        return JsonResponse({"message": {"Not have keys": str(', '.join(listError))}}, status=400)
    with connection.cursor() as cursor:
        checkExist = cursor.execute("select 1 from dbo.["+idcus+"|bill] where bill_number = '"+str(numInvoice)+"' and symbol='"+str(symbol)+"' and  vendor_number = 'TTPP'").fetchone()
    if checkExist != None:
        return JsonResponse({"message": "Already Exist"}, status=200)
    else:
        return JsonResponse({"message": "Does Not Exist"}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Upload_HDDT_TTPP(request):
    dir_storage = settings.MEDIA_ROOT  # đường dẫn folder lưu ảnh, pdf, xml
    strInvoice = request.POST.get('strInvoice', None)
    pathPDF = request.FILES.get('pathPDF', None)
    pathIMG = request.FILES.get('pathIMG', None)
    pathXML = request.FILES.get('pathXML', None)
    idcus = str(request.user.cus_id)
    listBody = ['strInvoice', 'pathPDF', 'pathIMG', 'pathXML']
    listError = []
    for iBody in listBody:
        if (eval(iBody) is None) or (eval(iBody) == []):
            listError.append(iBody)
    if listError != []:
        return JsonResponse({"message": {"Not have keys": str(', '.join(listError))}}, status=400)
    try:
        arrcon = strInvoice.split('❤')
        imgname = arrcon[0]
        resu = arrcon[1]
        listtong = resu.split('‡')
        mst = listtong[0]
        tencty = listtong[1]
        diachi = listtong[2]
        khhd = listtong[4]
        shd = listtong[5]
        ngayhd = listtong[6]
        listthue = listtong[7:26]
        thue_str = '‡'.join(listthue)
        luoi = arrcon[2]
        mapo = arrcon[3]
        tongtien = arrcon[4]
        mavender = arrcon[5]
        group_hd = arrcon[6]
        upday = arrcon[9]
        #idcus_old = arrcon[10]
        ktd = arrcon[11]
        typehd = "10"
        hddt = arrcon[13]
        # qa = ""
        tickqa = "0"
        status = arrcon[14]
        invoice_Folder = datetime.datetime.strptime(
            ngayhd, '%d/%m/%Y').strftime('%y%m%d')
        fs_PDF = FileSystemStorage(
            location=dir_storage+"/pdf/"+invoice_Folder, base_url=dir_storage+"/pdf/"+invoice_Folder)
        filenamePDF = fs_PDF.save(pathPDF.name, pathPDF)
        fs_XML = FileSystemStorage(
            location=dir_storage+"/pdf/"+invoice_Folder, base_url=dir_storage+"/pdf/"+invoice_Folder)
        filenameXML = fs_XML.save(pathXML.name, pathXML)
        fs_IMG = FileSystemStorage(
            location=dir_storage+"/img/"+invoice_Folder, base_url=dir_storage+"/img/"+invoice_Folder)
        filenameIMG = fs_IMG.save(pathIMG.name, pathIMG)
        with connection.cursor() as cursor:
            status_id = 1
            #idcus = str(cursor.execute("select id from dbo.Service_listcus where id_old ="+idcus_old+"").fetchone()[0])
            cursor.execute("Insert into dbo.["+idcus+"|bill](listcus_id,status_id,type_product_id,group_hd,image_name,po_number,vendor_number,sum_po,tax_number,symbol,bill_number,city_name,city_address,bill_date,ket_thuc_dot_number,upload_date,result_check,result_check_luoi,is_qa,is_hddt,user_id_up,src_pdf,src_xml,src_image) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", [
                        idcus, status_id, typehd, group_hd, imgname.strip(), mapo, mavender, tongtien, mst, khhd, shd, tencty, diachi, ngayhd, ktd, upday, thue_str, luoi, tickqa, hddt, request.user.id, "pdf/"+invoice_Folder+"/"+filenamePDF, "pdf/"+invoice_Folder+"/"+filenameXML, "img/"+invoice_Folder+"/"+filenameIMG]).commit()
    except Exception as Error:
        os.remove(dir_storage+"/pdf/"+invoice_Folder+"/"+filenamePDF)
        os.remove(dir_storage+"/pdf/"+invoice_Folder+"/"+filenameXML)
        os.remove(dir_storage+"/img/"+invoice_Folder+"/"+filenameIMG)
        return JsonResponse({"message": str(Error)}, status=400)
    return JsonResponse({"message": {"strInvoice": str(strInvoice), "filenamePDF": filenamePDF, "filenameXML": filenameXML, "filenameIMG": filenameIMG}}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_bill_for_image(request):
    image_name = request.POST.get('image_name', '')
    status = request.POST.get('status_bill', '')
    vendor_number = request.POST.get('vendor', '')
    status_rpa = request.POST.get('status_rpa', '')
    id_cus = request.user.cus_id
    # id_cus = request.POST.get('id_cus', '')
    user_id = request.user.id

    if '' in [image_name, id_cus]:
        return JsonResponse({'message' : 'missing para require'})

    if status != '':
        status = StatusBill.objects.get(symbol = status).id

    str_update_vendor_number = " vendor_number = N'" + str(vendor_number) + "' ," if vendor_number != '' else ''
    str_update_status = " status_id = N'" + str(status) + "' ," if str(status) != '' else ''
    str_update_status_rpa = " status_rpa = N'" + str(status_rpa) + "' ," if status_rpa != '' else ''

    query_update = "UPDATE ["+str(id_cus)+"|bill]  SET \
                                          " + str_update_vendor_number + " \
                                          " + str_update_status + " \
                                          " + str_update_status_rpa + " \
                                            last_change_date = getdate(), user_id_change = %s \
                                    WHERE image_name = %s and is_po <> 1"
    # with transaction.atomic():
    with connection.cursor() as cursor:
        try:
            find_old_status = cursor.execute("SELECT status_id,vendor_number, status_rpa, id  from ["+str(id_cus)+"|bill] WHERE \
                                              image_name = %s and is_po <> 1 ",[ str(image_name)]).fetchone()
            cursor.execute(query_update, [user_id, image_name])
            old_values_save_log = '❥'.join(str(x) if x != None else '' for x in find_old_status)
            new_values_save_log = '❥'.join([str(status), vendor_number, status_rpa])
            ###lưu log##type = 9 là robot update theo ten anh###
            cursor.execute("INSERT INTO ["+str(id_cus)+"|log_change_status] (listcus_id, user_id, type, date_change, old_status, new_status, bill_id) \
                                             VALUES (%s, %s, %s, getdate(), %s, %s, %s)",
                        [id_cus, user_id, 9, old_values_save_log, new_values_save_log, find_old_status.id])  ###update log
            cursor.commit()
        except Exception as e:
            print(e)
            cursor.rollback()
            return JsonResponse({
                'message': 'have error, please try again'
            })
    return JsonResponse({
        'message': 'success!!'
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_status_hddt(request):
    image_name = request.POST.get('ImageName', None)
    id_cus = request.user.cus_id
    # id_cus = request.POST.get('id_cus', None)

    if None in [image_name, id_cus]:
        return JsonResponse({'message': 'missing param required'}, status=200)

    with connection.cursor() as cur:
        cur.execute("UPDATE ["+str(id_cus)+"|bill] set is_hddt = 1 where image_name = %s", [image_name]).commit()

    return JsonResponse({'message': 'success'}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_pdf_receiver(request):
    myfile = request.FILES.get('file_up', '')
    folder = request.POST.get('folder', '')
    id_cus = request.user.cus_id
    # id_cus = request.POST.get('id_cus', '')
    group_hd = request.POST.get('group_hd')
    if  '' in [myfile, folder] or myfile.name.endswith('.pdf') == False :
        return JsonResponse({'message': 'error : No file send or file send not is pdf, check parameter'})

    folder_save = settings.MEDIA_ROOT + 'pdf_receiver/' + folder
    if not os.path.exists(folder_save):
        os.makedirs(folder_save)
    else:
        if os.path.exists(folder_save + '/' + myfile.name):
            os.remove(folder_save + '/' + myfile.name)

    fs = FileSystemStorage(location=folder_save)  # defaults to   MEDIA_ROOT
    fs.save(myfile.name, myfile)
    with connection.cursor() as cur :
        cur.execute("UPDATE ["+str(id_cus)+"|bill] set src_receiver = %s where group_hd = %s" , ['pdf_receiver/' + folder + '/' + myfile.name, group_hd]).commit()
    return JsonResponse({'message': 'success'}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_check_exist_bill(request):
    id_cus = request.user.cus_id
    tax_number = request.GET.get('tax_number', '')
    bill_number = request.GET.get('bill_number', '')
    if  tax_number == '' or bill_number == '':
        return JsonResponse({
            'message': 'Lỗi, Param gửi lên còn thiếu'
        }, safe=False)
    else:
        with connection.cursor() as cursor:
            try:
                sql_check = cursor.execute("SELECT image_name from ["+str(id_cus)+"|bill] WHERE tax_number = %s and bill_number = %s ",
                                           [tax_number, bill_number]).fetchone()
                if sql_check:
                    return JsonResponse({
                        'message': 'Thành công',
                        'image_name': sql_check[0]
                    }, safe=False)
                else:
                    return JsonResponse({
                        'message': 'Chưa tồn tại tên ảnh'
                    }, safe=False)
            except Exception as e:
                print(e)
                return JsonResponse({
                    'message': 'Error, Chưa tồn tại bảng trên database'
                }, safe=False)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_update_group_bill(request):
    group_hd = request.POST.get('group_hd', None)
    po_number = request.POST.get('po_number', '')
    receiver_number = request.POST.get('receiver_number', '')
    vendor_number = request.POST.get('vendor_number', '')
    status = request.POST.get('status', '')
    status_rpa = request.POST.get('status_rpa', '')
    upload_date = request.POST.get('upload_date', '')  ##format 12/12/2020
    id_cus = request.user.cus_id
    #id_cus = request.POST.get('id_cus', None)
    user_id = request.user.id

    if None in [group_hd, id_cus]:
        return JsonResponse({
            'message': 'Fail, group and id_cus is not None'
        }, safe=False)

    if status != '':
        status = StatusBill.objects.get(symbol = status).id

    str_update_po_number = " po_number = N'" + str(po_number) + "' ," if po_number != '' else ''
    str_update_receiver_number = " receiver_number = N'" + str(receiver_number) + "' ," if receiver_number != '' else ''
    str_update_vendor_number = " vendor_number = N'" + str(vendor_number) + "' ," if vendor_number != '' else ''
    str_update_status = " status_id = N'" + str(status) + "' ," if status != '' else ''
    str_update_status_rpa = " status_rpa = N'" + str(status_rpa) + "' ," if status_rpa != '' else ''

    query_update = "UPDATE ["+str(id_cus)+"|bill]  SET \
                                      " + str_update_po_number + " \
                                      " + str_update_receiver_number + " \
                                      " + str_update_vendor_number + " \
                                      " + str_update_status + " \
                                      " + str_update_status_rpa + " \
                                        last_change_date = getdate(), user_id_change = %s \
                                WHERE group_hd = '" + str(group_hd) + "' and is_po <> 1"
    # with transaction.atomic():
    with connection.cursor() as cursor:
        try:
            find_old_status = cursor.execute(
                "SELECT status_id,po_number,receiver_number,vendor_number, status_rpa  from ["+str(id_cus)+"|bill] WHERE group_hd = %s and is_po <> 1 ", [group_hd]).fetchone()
            cursor.execute(query_update, [user_id])
            old_values_save_log = '❥'.join(str(x) if x != None else '' for x in find_old_status)
            new_values_save_log = '❥'.join([str(status), po_number, receiver_number, vendor_number, status_rpa ])
            ###lưu log##type = 8 là robot update ###
            cursor.execute("INSERT INTO ["+str(id_cus)+"|log_change_status] (listcus_id, user_id, type, date_change, old_status, new_status, group_hd) \
                                         VALUES (%s, %s, %s, getdate(), %s, %s, %s)",
                        [id_cus, user_id, 8, old_values_save_log, new_values_save_log,group_hd])  ###update log
            cursor.commit()
        except Exception as e:
            print(e)
            cursor.rollback()
            return JsonResponse({
                'message': 'have error, please try again'
            })
    return JsonResponse({
        'message': 'success!!'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auto_check_miss_po(request):
    idcus =request.user.cus_id        
    strdateSearch = request.GET.get('dateSearch')
    try:
        dateSearch = datetime.datetime.strptime(strdateSearch, '%d/%m/%Y')
    except:
        return JsonResponse({"message": "dateSearch:dd/mm/yyyy"}, status=400)
    strings = str(dateSearch.strftime('%y%m%d'))
    Day = str(int(strings[4:]))
    txt_miss = ''
    
    foldernow = settings.MEDIA_ROOT + "pdf_receiver/"
    with connection.cursor() as cursor:
        result = cursor.execute(
            "Select group_hd,po_number,Receiver_number from dbo.[" +str(idcus)+"|bill ] where  day(Upload_date) =" + Day + " and ISNULL(Receiver_number,'') !='' ").fetchall()
    for item in result:
        hdprop = item[0]
        dayup = hdprop[2:8]
        path_reciver = foldernow + dayup + '/' + hdprop + '.pdf'
        if os.path.exists(path_reciver) == False:
            if item[1] == '00000000':
                txt_miss = txt_miss + hdprop + '#' + item[2] + '\n'
            else:
                txt_miss = txt_miss + hdprop + '#' + item[1] + '\n'
    
    with connection.cursor() as cursor:
        result = cursor.execute(
            "select Image_Name,po_number from dbo.[" +str(idcus)+"|bk] where Receiver_number is not null and day(Upload_date) =" + Day + " and Receiver_number !=''").fetchall()
    for item in result:
        imagename = item[0]
        dayup = imagename[2:8]
        path_reciver = foldernow + dayup + '/' + imagename.split('.')[0] + '.pdf'
        if os.path.exists(path_reciver) == False:
            txt_miss = txt_miss + imagename + '#' + item[1] + '\n'
    return JsonResponse({"message": txt_miss}, status=200)