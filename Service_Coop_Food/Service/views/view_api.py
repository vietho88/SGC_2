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
from django.db import  connection,connections
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
    #id_cus = request.user.cus_id
    store = request.GET.get('store', None)    
    with connection.cursor() as cursor:
        try:  
            id_cus =  cursor.execute("SELECT Id  from [Service_listcus] WHERE store_number =%s ", [store]).fetchone()[0]
        except:
            return JsonResponse({"message": "store is Error"}, status=400)
    if None in [date_send, status, select_nganh_hang, store]:
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
        # find_dot_sql = cursor.execute(
        #     "SELECT distinct(ket_thuc_dot_number) from dbo.[" + str(id_cus) + "|bill] as tb1 join service_statusbill on tb1.status_id = service_statusbill.id where service_statusbill.symbol = '" + str(
        #         status) + "' and convert(varchar, upload_date, 112) = '" + date + "' ").fetchall()
        # if  len(find_dot_sql) > 0:
        #     str_dots = ','.join([str(x[0]) for x in find_dot_sql])
        # else:
        #     return JsonResponse({
        #         'message': 'No batch found!!'
        #     })
        if str_status ==6:
            sql_list_hdgroup = cursor.execute("SELECT   group_hd  \
                    FROM dbo.[" + str(id_cus) + "|bill] \
                    WHERE is_po <> 1  and status_id = "+str(str_status)+"  and type_product_id in  (" + str(list_nganh_hang_search) + ")  \
                        and convert(varchar, upload_date, 112) = '" + date + "' and result_check is not null ").fetchall()
            list_grouphd = list(map(lambda x: "'"+str(x[0])+"'", sql_list_hdgroup))
            string_grop = ','.join(list_grouphd)
            if string_grop!='':
                sql_list_bill = cursor.execute("SELECT  tb1.result_check, isnull(tb1.result_check_luoi,'') as result_check_luoi, tb1.image_name, tb1.id, tb3.name, \
                        isnull(tb2.name,'') as name, tb1.status_id, tb1.po_number,tb1.sum_po, tb1.group_hd , \
                        convert(varchar, tb1.upload_date, 120) as N'Ngày Tạo', convert(varchar, tb1.last_change_date, 120) as last_change_date, \
                        tb1.status_other, tb1.ket_thuc_dot_number, tb1.is_qa, tb1.tax_number, tb1.is_qa,  tb1.is_hddt, tb1.vendor_number, tb1.symbol, tb1.bill_number, tb1.bill_date, \
                        tb1.city_name, tb1.city_address,  \
                        tb1.status_rpa, tb1.receiver_number,convert(varchar, tb1.upload_date, 103) as upload_date, tb3.address, tb3.name as name_cus FROM dbo.[" + str(id_cus) + "|bill] as tb1 \
                            INNER JOIN service_typeproduct as tb2 ON tb1.type_product_id = tb2.id INNER JOIN service_Listcus as tb3 ON tb3.Id = tb1.listcus_id \
                        WHERE tb1.is_po <> 1  and   tb1.group_hd in  (" + str(string_grop) + ")  \
                        order by tb1.ket_thuc_dot_number, tb1.type_product_id ,tb1.last_change_date, tb1.upload_date").fetchall()
            else:
                sql_list_bill=[]
        else:
            sql_list_bill = cursor.execute("SELECT  tb1.result_check, isnull(tb1.result_check_luoi,'') as result_check_luoi, tb1.image_name, tb1.id, tb3.name, \
                    isnull(tb2.name,'') as name, tb1.status_id, tb1.po_number,tb1.sum_po, tb1.group_hd , \
                    convert(varchar, tb1.upload_date, 120) as N'Ngày Tạo', convert(varchar, tb1.last_change_date, 120) as last_change_date, \
                    tb1.status_other, tb1.ket_thuc_dot_number, tb1.is_qa, tb1.tax_number, tb1.is_qa,  tb1.is_hddt, tb1.vendor_number, tb1.symbol, tb1.bill_number, tb1.bill_date, \
                    tb1.city_name, tb1.city_address,  \
                    tb1.status_rpa, tb1.receiver_number,convert(varchar, tb1.upload_date, 103) as upload_date, tb3.address, tb3.name as name_cus FROM dbo.[" + str(id_cus) + "|bill] as tb1 \
                        INNER JOIN service_typeproduct as tb2 ON tb1.type_product_id = tb2.id INNER JOIN service_Listcus as tb3 ON tb3.Id = tb1.listcus_id \
                    WHERE tb1.is_po <> 1 and   tb1.status_id = "+str(str_status)+"  and tb1.type_product_id in  (" + str(list_nganh_hang_search) + ")  \
                        and convert(varchar, upload_date, 112) = '" + date + "' and result_check is not null  order by tb1.ket_thuc_dot_number, tb1.type_product_id ,tb1.last_change_date, tb1.upload_date").fetchall()

    if len(sql_list_bill) == 0:
        return JsonResponse({
            'message': 'No data to export!!'
        })

    for bill in sql_list_bill:
        list_=bill.result_check_luoi.split('‡') if bill.result_check_luoi  else ['†††††††']  
        lsa1='+'.join(list(map(lambda x: x.split('†')[0], list_)))
        lsa2=list_[0].split('†')[1]
        lsa3=''
        lsa4='+'.join(list(map(lambda x: x.split('†')[3], list_)))
        lsa5='+'.join(list(map(lambda x: x.split('†')[4], list_)))
        lsa6=''
        lsa7=''
        lsa8=''
        tong = '‡'.join([lsa1,lsa2,lsa3,lsa4,lsa5,lsa6,lsa7,lsa8])
        if '|' in bill.result_check:
            temp = [bill.status_rpa, bill.name_cus, bill.name, bill.symbol, bill.bill_number, bill.bill_date, bill.tax_number, bill.city_name, bill.city_address] + tong.split('‡') + bill.result_check.split('|')[0].split('‡')[0:-1]  + ['', bill.po_number, bill.sum_po,'QA' if bill.is_qa else '', bill.vendor_number, bill.group_hd, bill.image_name, bill.receiver_number, bill.upload_date]
        else:
            temp = [bill.status_rpa, bill.name_cus, bill.name, bill.symbol, bill.bill_number, bill.bill_date, bill.tax_number, bill.city_name, bill.city_address] + tong.split('‡') + bill.result_check.split('‡')  + ['', bill.po_number, bill.sum_po,'QA' if bill.is_qa else '', bill.vendor_number, bill.group_hd, bill.image_name, bill.receiver_number, bill.upload_date]
        list_data_bill.append(temp)
        list_group.append(str(bill.group_hd))
    str_list_group = str(','.join(["'" + x + "'" for x in list_group]))
    with connection.cursor() as cursor:
        sql_list_po = cursor.execute("SELECT group_hd,bill_number, result_check_luoi,is_po\
                            ,  is_qa,  po_number  FROM dbo.[" + str(id_cus) + "|bill] WHERE  \
                           group_hd in ("+str_list_group+") and is_po=1   ").fetchall()
    for po in sql_list_po:
        if po.is_po:
            po_number = po.po_number
            is_qa  = po.is_qa
            bill_number = po.bill_number
            for item in  po.result_check_luoi.split('‡'):
                temp = [ po_number ] + item.split('†')[:5] + ['QA' if is_qa == True  else '', bill_number]
                list_data_po.append(temp)
    df_bill = pd.DataFrame(list_data_bill,
                             columns=["Status", "Tên doanh nghiệp", "Số mẫu hóa đơn", "Ký hiệu hóa đơn",
                                      "Số hóa đơn", "Ngày", "Mã số thuế người bán/người mua", "Công Ty",
                                      "Địa chỉ", "Mã hàng hóa/Dịch vụ", "Tên hàng hóa/Dịch vụ/Diễn giải",
                                      "Đơn vị tính", "Số lượng", "Đơn giá", "Thuế VAT Mặt Hàng (%)",
                                      "Tiền thuế VAT Mặt hàng", "Thành tiền", "Thuế VAT hóa đơn (0%)","Cộng tiền HÀng Hóa(0%)",
                                      "Tiền thuế VAT hoá đơn (0%)",  "Tổng tiền thanh toán (0%)", 
                                      "Thuế VAT hóa đơn (5%)","Cộng tiền HÀng Hóa(5%)", "Tiền thuế VAT hoá đơn (5%)",
                                      "Tổng tiền thanh toán (5%)", 
                                      "Thuế VAT hóa đơn (10%)","Cộng tiền HÀng Hóa(10%)", "Tiền thuế VAT hoá đơn (10%)",
                                      "Tổng tiền thanh toán (10%)","Thuế VAT hóa đơn (...%)", "Cộng tiền HÀng Hóa(...%)",
                                       "Tiền thuế VAT hoá đơn (...%)",
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
    #cus_id = request.user.cus_id
    store = request.GET.get('store', None)    
    with connection.cursor() as cursor:
        try:  
            id_cus =  cursor.execute("SELECT Id  from [Service_listcus] WHERE store_number =%s ", [store]).fetchone()[0]
        except:
            return JsonResponse({"message": "store is Error"}, status=400)
    if None in [date, type_invoice_list, store]:
        return JsonResponse({
            'message' : 'missing para require'
        })


    list_cus_manager = request.user.manager_cus.all().values_list('id', flat=True)
    if int(id_cus) not in list_cus_manager:
        return JsonResponse({
            'message' : 'use not permission in cus'
        })
    name_cus = ListCus.objects.get(pk = id_cus).name

    with connection.cursor() as cursor:
        sql_list_invoice = cursor.execute(
            "SELECT tb2.name, tb1.image_name, tb1.is_qa, tb1.vendor_number, tb1.bk_number,  tb1.result_check FROM [dbo].[" + str(id_cus) + "|bk] as tb1 inner join service_typeproduct as tb2 on tb1.type_bk = tb2.id where CONVERT(varchar,tb1.upload_date,103) = '" + date + "'   and tb1.type_bk = " + str(type_invoice_list) + "  ").fetchall()
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
        hddt = 1
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
            cursor.execute("Insert into dbo.["+idcus+"|bill](listcus_id,status_id,type_product_id,group_hd,image_name,po_number,vendor_number,sum_po,tax_number,symbol,bill_number,city_name,city_address,bill_date,ket_thuc_dot_number,upload_date,result_check,result_check_luoi,is_qa,is_hddt,user_id_up,src_pdf,src_xml,src_image,is_ttpp) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", [
                        idcus, status_id, typehd, group_hd, imgname.strip(), mapo, mavender, tongtien, mst, khhd, shd, tencty, diachi, ngayhd, ktd, upday, thue_str, luoi, tickqa, hddt, request.user.id, "pdf/"+invoice_Folder+"/"+filenamePDF, "pdf/"+invoice_Folder+"/"+filenameXML, "img/"+invoice_Folder+"/"+filenameIMG,1]).commit()
    except Exception as Error:
        if os.path.isfile (dir_storage+"/pdf/"+invoice_Folder+"/"+filenamePDF):
            os.remove(dir_storage+"/pdf/"+invoice_Folder+"/"+filenamePDF)
        if os.path.isfile (dir_storage+"/pdf/"+invoice_Folder+"/"+filenameXML):
            os.remove(dir_storage+"/pdf/"+invoice_Folder+"/"+filenameXML)
        if os.path.isfile (dir_storage+"/img/"+invoice_Folder+"/"+filenameIMG):
            os.remove(dir_storage+"/img/"+invoice_Folder+"/"+filenameIMG)
        return JsonResponse({"message": str(Error)}, status=400)
    return JsonResponse({"message": {"strInvoice": str(strInvoice), "filenamePDF": filenamePDF, "filenameXML": filenameXML, "filenameIMG": filenameIMG}}, status=200)
@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def Upload_HDDT_NCC(request):
    dir_storage = settings.MEDIA_ROOT  # đường dẫn folder lưu ảnh, pdf, xml
    pathPDF = request.FILES.get('pathPDF', None)
    pathXML = request.FILES.get('pathXML', None)
    image = request.POST.get('image', '')
    idcus_old = image.split('_')[5]
    ngayhd = image[2:8]
    with connection.cursor() as cursor:
        try:
            idcus = cursor.execute("SELECT  Id from [Service_listcus] WHERE id_old =%s ", [idcus_old]).fetchone()[0]
        except:
            return JsonResponse({"message": "Store Number Error "}, status=400)
    # listBody = ['pathPDF', 'pathXML']
    # listError = []
    # for iBody in listBody:
    #     if (eval(iBody) is None) or (eval(iBody) == []):
    #         listError.append(iBody)
    # if listError != []:
    #     return JsonResponse({"message": {"Not have keys": str(', '.join(listError))}}, status=400)
    try:        
        hddt = 1 

        invoice_Folder = ngayhd
        if pathPDF:
            fs_PDF = FileSystemStorage(
                location=dir_storage+"/pdf/"+invoice_Folder, base_url=dir_storage+"/pdf/"+invoice_Folder)
            filenamePDF = fs_PDF.save(pathPDF.name, pathPDF)
            src_pdf ="pdf/"+invoice_Folder+"/"+filenamePDF
        else:
            src_pdf =None
        if pathXML:
            fs_XML = FileSystemStorage(
                location=dir_storage+"/pdf/"+invoice_Folder, base_url=dir_storage+"/pdf/"+invoice_Folder)
            filenameXML = fs_XML.save(pathXML.name, pathXML)  
            src_xml = "pdf/"+invoice_Folder+"/"+filenameXML
        else:
            src_xml = None
        with connection.cursor() as cursor:
            cursor.execute("update dbo.["+str(idcus)+"|bill] set is_hddt =%s,src_pdf = %s,src_xml=%s where image_name = %s ", [
                        hddt,src_pdf,src_xml,image]).commit()
    except Exception as Error:
        if os.path.isfile (dir_storage+"/pdf/"+invoice_Folder+"/"+filenamePDF):
            os.remove(dir_storage+"/pdf/"+invoice_Folder+"/"+filenamePDF)
        if os.path.isfile (dir_storage+"/pdf/"+invoice_Folder+"/"+filenameXML):
            os.remove(dir_storage+"/pdf/"+invoice_Folder+"/"+filenameXML)        
        return JsonResponse({"message": str(Error)}, status=400)
    return JsonResponse({"message":  "ok"}, status=200)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_bill_for_image(request):
    image_name = request.POST.get('image_name', '')
    status = request.POST.get('status_bill', '')
    vendor_number = request.POST.get('vendor', '')
    status_rpa = request.POST.get('status_rpa', '')
    #id_cus = request.user.cus_id
    log = request.POST.get('log', None)
    rb_name =  request.POST.get('robot_name', '')
    user_id = request.user.id
    store = request.POST.get('store', None)  
    if '' in [image_name, store]:
        return JsonResponse({'message' : 'missing para require'})  
    with connection.cursor() as cursor:
        try:  
            id_cus =  cursor.execute("SELECT Id  from [Service_listcus] WHERE store_number =%s ", [store]).fetchone()[0]
            bill_id = str(cursor.execute("select Id from ["+str(id_cus)+"|bill] where  image_name = %s  ",[image_name]).fetchone().Id)
        except:
            return JsonResponse({"message": "store or image_name is Error"}, status=400)
    

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
                                    WHERE Id = %s and is_po <> 1"
    # with transaction.atomic():
    with connection.cursor() as cursor:
        try:
            if  log==None:
                cursor.execute(query_update, [user_id, bill_id])
            else:
                status_rpa=log
            # find_old_status = cursor.execute("SELECT status_id,vendor_number, status_rpa, id  from ["+str(id_cus)+"|bill] WHERE \
            #                                   image_name = %s and is_po <> 1 ",[ str(image_name)]).fetchone()
            
            # old_values_save_log = '❥'.join(str(x) if x != None else '' for x in find_old_status)
            # new_values_save_log = '❥'.join([str(status), vendor_number, status_rpa])
            # ###lưu log##type = 9 là robot update theo ten anh###
            new_values_save_log= rb_name +' : '+ status_rpa
            cursor.execute("INSERT INTO ["+str(id_cus)+"|log_change_status] (listcus_id, user_id, type, date_change,  new_status, bill_id) \
                                              VALUES (%s, %s, %s, getdate(), %s,  %s)",
                         [id_cus, user_id, 9,  new_values_save_log, bill_id])  ###update log
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
    store = request.POST.get('store', None)    
    with connection.cursor() as cursor:
        try:  
            id_cus =  cursor.execute("SELECT Id  from [Service_listcus] WHERE store_number =%s ", [store]).fetchone()[0]
        except:
            return JsonResponse({"message": "store is Error"}, status=400)
    if None in [image_name, store]:
        return JsonResponse({'message': 'missing param required'}, status=200)

    with connection.cursor() as cur:
        cur.execute("UPDATE ["+str(id_cus)+"|bill] set is_hddt = 1 where image_name = %s", [image_name]).commit()

    return JsonResponse({'message': 'success'}, status=200)

@api_view(['POST'])
#@permission_classes([IsAuthenticated])
def upload_pdf_receiver(request):
    myfile = request.FILES.get('file_up', '')
    folder = request.POST.get('folder', '')
    #user = request.POST.get('user_web', '')
    store = request.POST.get('store', None)    
    with connection.cursor() as cursor:
        try:  
            id_cus =  cursor.execute("SELECT Id  from [Service_listcus] WHERE store_number =%s ", [store]).fetchone()[0]
        except:
            return JsonResponse({"message": "store is Error"}, status=400)
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
    name =myfile.name.split('.pdf')[0]
    if os.stat(folder_save + '/' + myfile.name).st_size<75:
        os.remove(folder_save + '/' + myfile.name)
        return JsonResponse({'message': 'error file'}, status=200)
    with connection.cursor() as cur :
        try:
            if '_'  in name:
                cur.execute("UPDATE ["+str(id_cus)+"|bk] set src_receiver = %s where image_name = %s" , ['pdf_receiver/' + folder + '/' + myfile.name, name+'.jpg']).commit()
            else:
                pathpdf ='pdf_receiver/' + folder + '/' + myfile.name
                cur.execute("UPDATE ["+str(id_cus)+"|bill] set  src_receiver = N'"+pathpdf+"' where group_hd = '"+name+"'" ).commit()   #status_id = case when status_id =4 and ISNUMERIC(po_number) = 1 and po_number!='00000000' then  6 when  status_id = 4 and ISNUMERIC(po_number) = 0 and upper(po_number) not like '%S%' then 8 else status_id end,status_rpa = case when status_id =4 and ISNUMERIC(po_number) = 1 and po_number!='00000000' then  'Receiver' else status_rpa end,
                #cur.execute("UPDATE ["+str(id_cus)+"|bill] set  src_receiver = %s where group_hd = %s" , ['pdf_receiver/' + folder + '/' + myfile.name, name]).commit()
        except:
            return JsonResponse({'message': 'error'}, status=200)
            
    return JsonResponse({'message': 'success'}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_check_exist_bill(request):
    #id_cus = request.user.cus_id
    tax_number = request.GET.get('tax_number', '')
    bill_number = request.GET.get('bill_number', '')
    store = request.GET.get('store', None)    
    with connection.cursor() as cursor:
        try:  
            id_cus =  cursor.execute("SELECT Id  from [Service_listcus] WHERE store_number =%s ", [store]).fetchone()[0]
        except:
            return JsonResponse({"message": "store is Error"}, status=400)
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_check_exist_symbol_number(request):
    #id_cus = request.user.cus_id
    symboy_number = request.GET.get('symbol_number', '')
    bill_number = request.GET.get('bill_number', '')
    store = request.GET.get('store', None)    
    with connection.cursor() as cursor:
        try:  
            id_cus =  cursor.execute("SELECT Id  from [Service_listcus] WHERE store_number =%s ", [store]).fetchone()[0]
        except:
            return JsonResponse({"message": "store is Error"}, status=400)
    if  symboy_number == '' or bill_number == '':
        return JsonResponse({
            'message': 'Lỗi, Param gửi lên còn thiếu'
        }, safe=False)
    else:
        with connection.cursor() as cursor:
            try:
                sql_check = cursor.execute("SELECT image_name,group_hd from ["+str(id_cus)+"|bill] WHERE symbol = %s and bill_number = %s and status_id=6",
                                           [symboy_number, bill_number]).fetchall()
                if sql_check:
                    list_image =list(map(lambda x: x[0], sql_check))
                    count_bill =  cursor.execute("SELECT count( DISTINCT bill_number )  from ["+str(id_cus)+"|bill] WHERE group_hd = %s and is_po =0",
                                           [sql_check[0][1]]).fetchone()[0]
                    return JsonResponse({
                        'message': 'Thành công',
                        'image_name': list_image,
                        'count':str(count_bill)
                    }, safe=False)
                else:
                    return JsonResponse({
                        'message': 'Tên ảnh không ở trạng thái R'
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
    #id_cus = request.user.cus_id
    log = request.POST.get('log', None)
    rb_name =  request.POST.get('robot_name', '')
    store = request.POST.get('store', None)    
    with connection.cursor() as cursor:
        try:  
            id_cus =  cursor.execute("SELECT Id  from [Service_listcus] WHERE store_number =%s ", [store]).fetchone()[0]
        except:
            return JsonResponse({"message": "store is Error"}, status=400)
    user_id = request.user.id

    if None in [group_hd, store]:
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
            # find_old_status = cursor.execute(
            #     "SELECT status_id,po_number,receiver_number,vendor_number, status_rpa  from ["+str(id_cus)+"|bill] WHERE group_hd = %s and is_po <> 1 ", [group_hd]).fetchone()
            if log==None:
                cursor.execute(query_update, [user_id])
            else:
                status_rpa=log
            # old_values_save_log = '❥'.join(str(x) if x != None else '' for x in find_old_status)
            # new_values_save_log = '❥'.join([str(status), po_number, receiver_number, vendor_number, status_rpa ])
            # ###lưu log##type = 8 là robot update ###
            new_values_save_log= rb_name +' : '+ status_rpa
            cursor.execute("INSERT INTO ["+str(id_cus)+"|log_change_status] (listcus_id, user_id, type, date_change,  new_status, group_hd) \
                                         VALUES (%s, %s, %s, getdate(), %s,  %s)",
                        [id_cus, user_id, 8,  new_values_save_log,group_hd])  ###update log
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
    #idcus =request.user.cus_id        
    strdateSearch = request.GET.get('dateSearch')
    try:
        dateSearch = datetime.datetime.strptime(strdateSearch, '%d/%m/%Y')
    except:
        return JsonResponse({"message": "dateSearch:dd/mm/yyyy"}, status=400)
    store = request.GET.get('store', None)    
    with connection.cursor() as cursor:
        try:  
            id_cus =  cursor.execute("SELECT Id  from [Service_listcus] WHERE store_number =%s ", [store]).fetchone()[0]
        except:
            return JsonResponse({"message": "store is Error"}, status=400)
    data = {'reciver':[] }
    foldernow = settings.MEDIA_ROOT + "pdf_receiver/"
    with connection.cursor() as cursor:
        result1 = cursor.execute(
            "Select group_hd,po_number,Receiver_number from dbo.[" +str(id_cus)+"|bill ] where  convert(varchar, Upload_date, 103)='"+strdateSearch+"' and ISNULL(Receiver_number,'') !='' and status_id in(6,8) and ISNUMERIC(po_number) = 1 ").fetchall()
        result2 = cursor.execute(
            "Select group_hd,po_number,Receiver_number from dbo.[" +str(id_cus)+"|bill ] where  convert(varchar, Upload_date, 103)='"+strdateSearch+"' and status_id in(8) and ISNUMERIC(po_number) = 0 ").fetchall()
    result = result1+result2
    for item in result:
        hdprop = item[0]
        dayup = hdprop[2:8]
        path_reciver = foldernow + dayup + '/' + hdprop + '.pdf'
        if os.path.exists(path_reciver) == False:
            if item[1] == '00000000':
                newresult = {'hdgroup':hdprop,'po':item[2]}
                data['reciver'].append(newresult)
            else:
                newresult = {'hdgroup':hdprop,'po':item[1]}
                data['reciver'].append(newresult)
    
    with connection.cursor() as cursor:
        result = cursor.execute(
            "select Image_Name,po_number from dbo.[" +str(id_cus)+"|bk] where Receiver_number is not null and convert(varchar, Upload_date, 103)='"+strdateSearch+"'  and Receiver_number !=''").fetchall()
    for item in result:
        imagename = item[0]
        dayup = imagename[2:8]
        path_reciver = foldernow + dayup + '/' + imagename.split('.')[0] + '.pdf'
        if os.path.exists(path_reciver) == False:
            newresult = {'hdgroup':imagename,'po':item[1]}
            data['reciver'].append(newresult)
    return JsonResponse(data, status=200)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def insert_po(request):
    #idcus =request.user.cus_id   
    store =request.GET.get('store')     
    mapo=request.GET.get('mapo') 
    strdateSearch = request.GET.get('date_up')
    try:
        date_up = datetime.datetime.strptime(strdateSearch, '%d/%m/%Y')
    except:
        return JsonResponse({"message": "dateSearch:dd/mm/yyyy"}, status=400)
    table = str(store)+'|PO'
    with connections['rpa'].cursor() as cur:
        try:
            cur.execute(
                "Insert into dbo.["+table+"](Ma_PO,Date_Up) values (%s ,%s )",[mapo,date_up]).commit()            
        except:
            return JsonResponse({"message":"Error"}, status=200)
    return JsonResponse({"message":"Ok"}, status=200)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_po(request):
    store =request.GET.get('store')  
    date_start=request.GET.get('date_start')
    date_stop = request.GET.get('date_stop')
    try:
        date_start_ = datetime.datetime.strptime(date_start, '%d/%m/%Y')
        date_stop_ = datetime.datetime.strptime(date_stop, '%d/%m/%Y')
    except:
        return JsonResponse({"message": "dateSearch:dd/mm/yyyy"}, status=400)
    table = str(store)+'|PO'
    date_start_str = date_start_.strftime("%Y-%m-%d %H:%M:%S")
    date_stop_str = date_stop_.strftime("%Y-%m-%d %H:%M:%S")
    with connections['rpa'].cursor() as cur:
        try:
            result = cur.execute("Select Ma_PO from dbo.["+table+"] where  [Date_Up] >= %s   AND [Date_Up] <= %s",[date_start_str,date_stop_str]).fetchall() 
            list_po=list(map(lambda x: x[0], result))           
        except:
            return JsonResponse({"message":"Error"}, status=200)
    return JsonResponse({"Ma_PO":list_po}, status=200)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def update_po(request):
    #idcus =request.user.cus_id 
    get_img = request.GET.get('image_name')
    get_SoPO = request.GET.get('So_PO')
    get_SoBK = request.GET.get('So_BK')
    get_SoReceiver = request.GET.get('So_Receiver')
    store = request.GET.get('store', None)
    with connection.cursor() as cursor:
        try:  
            id_cus =  cursor.execute("SELECT Id  from [Service_listcus] WHERE store_number =%s ", [store]).fetchone()[0]
        except:
            return JsonResponse({"message": "store is Error"}, status=400)
    strtable = str(id_cus)+'|bk'    
    with connection.cursor() as cursor:
        try:
            cursor.execute("Update dbo.["+strtable+"] set last_change_date = getdate(), po_number = %s, bk_number = %s, receiver_number = %s  where image_name = %s", [get_SoPO, get_SoBK, get_SoReceiver, get_img]).commit()
        except  :
            return JsonResponse({"message":"Error"}, status=200)
    return JsonResponse({"message":"Ok"}, status=200)