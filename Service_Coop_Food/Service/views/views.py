from django.shortcuts import render
from django.http import HttpResponse
from django.db import  connection,connections
from django.db.transaction import atomic
from Service.models import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
import datetime
# Create your views here.
@login_required()
def index(request):
    return render(request, 'base.html')


##################VIEWS NÀY SỬ DỤNG ĐỂ BACKUP DỮ LIỆU TỪ DATABASE CŨ SANG DATABASE MỚI #############
def recover_bill(request):
    table_year = request.GET.get('name')
    list_month = [ '04' ,'05' ,'06' ,'07' ,'08' ,'09' ,'10' ,'11' , '12' ]
    # list_month = [ '11']
    return_clean = get_new_from_old()
    dict_cus = return_clean[0]
    dict_user = return_clean[1]
    dict_typr = return_clean[2]
    dict_status = return_clean[3]
    for month in list_month:
        count = 0
        list_id_faid = []
        table_name = str(table_year) + month
        with connections['recover'].cursor() as cur:
            sql = cur.execute("SELECT   Id  \
                  ,ImageDate \
                  ,Center \
                  ,ImageName \
                  ,MA_PO \
                  ,Ma_Vendor \
                  ,TongtienPO \
                  ,Cty_HANGHOA \
                  ,ResultCheck \
                  ,ResultCheckluoi \
                  ,typeHD \
                  ,Loai \
                  ,UploadDate \
                  ,Idcus \
                  ,NameCus \
                  ,IdCty \
                  ,Comment \
                  ,Info \
                  ,DateExport \
                  ,StatusHD \
                  ,Lastchangedate \
                  ,OtherStatus \
                  ,DotPL \
                  ,Ketthucdot \
                  ,SapxepHD \
                  ,HDGroup \
                  ,Export \
                  ,UserIdchange \
                  ,BBcomment \
                  ,NHcomment \
                  ,BBso \
                  ,QA \
                  ,HDDT \
                  ,Receiver \
                  ,CheckPO \
                  ,StatusRPA \
                  ,ThuctrangHD \
                  ,UserIdUp \
                  ,UserIdChangeKho \
                  ,TtppComment \
                  ,UserIdReceiver \
                  ,api_ktt \
                  ,KyHieuHD \
                  ,DatechangeKho \
                  FROM [IFE|"+str(table_name)+"] WHERE  resultcheck is not null and statushd is not null and imagename is not null and idcus in (111,112,113,114,126,127,128,129,130) ").fetchall()

        for item in sql:
            try:
                list_ADD = []
                user_id_up = 1
                status_id = ''
                try:
                    listcus_id = dict_cus[int(item.Idcus)]
                except:
                    listcus_id = 1

                try:
                    if item.UserIdChangeKho is not None:
                        user_id_up = dict_user[int(item.UserIdChangeKho)]
                except:
                    user_id_up = 1

                try:
                    if item.StatusHD != 'PO':
                        status_id = dict_status[item.StatusHD]
                except:
                    status_id = ''

                try:
                    type_product_id = dict_typr[int(item.typeHD)]
                except:
                    type_product_id = 1



                # type_product_id = TypeProduct.objects.filter(name=find_phan_loai).first().id
                # type_product_id = item[10]
                group_hd = item.HDGroup
                image_name = item.ImageName
                po_number = item.MA_PO
                vendor_number = item.Ma_Vendor
                receiver_number = item.Receiver
                sum_po = item.TongtienPO
                tax_number = item.ResultCheck.split('‡')[0]

                symbol = item.ResultCheck.split('‡')[4][:6]
                bill_number = item.ResultCheck.split('‡')[5]
                city_name = item.ResultCheck.split('‡')[1]
                city_address = item.ResultCheck.split('‡')[2]
                status_other = item.OtherStatus
                bill_date = item.ResultCheck.split('‡')[6]
                ket_thuc_dot_number = item.Ketthucdot
                user_id_up = user_id_up
                user_id_change = user_id_up
                upload_date = item.UploadDate

                kt_comment = item.BBcomment
                ttpp_comment = item.TtppComment
                result_check = item.ResultCheck.split(str(item.ResultCheck.split('‡')[6]) + '‡')[1] if item.StatusHD != 'PO' else item.ResultCheck[7:]
                result_check_luoi = item.ResultCheckluoi
                try:
                    check_trung = item.Checktrung
                except:
                    check_trung=''
                is_qa =  1 if(item.QA == 'QA') else  0
                is_po = 1 if(item.StatusHD == 'PO') else  0
                is_hddt = item.HDDT
                is_ttpp = 1 if(item.Ma_Vendor == 'TTPP') else  0

                is_rpa = 0
                has_report = 1 if(item.StatusHD == 'S') else  0
                str_upload_date = str(upload_date)
                forder = str(str_upload_date[2:4]) +  str(str_upload_date[5:7]) + str(str_upload_date[8:10])
                src_image = 'img' + '/' + forder + '/' + item.ImageName
                src_pdf = ('pdf' + '/' + forder + '/' + item.ImageName.replace('.jpg', '') + '_' + str(tax_number) + '.pdf') if item.Ma_Vendor == 'TTPP' else ''
                src_xml = ('pdf' + '/' + forder + '/' + item.ImageName.replace('.jpg', '') + '_' + str(tax_number) + '.xml') if item.Ma_Vendor == 'TTPP' else ''

                if item.Receiver  and  str(po_number).isnumeric() and str(item.typeHD) != '7':
                    src_receiver = 'pdf_receiver' + '/' + str(item.HDGroup)[2:8] + '/' + item.HDGroup + '.pdf'
                else:
                    src_receiver = ''
                api_ktt = item.api_ktt
                report_number = item.BBso if item.BBso else  0
                sql = "INSERT INTO ["+str(listcus_id)+"|bill] (listcus_id \
                                          ,status_id \
                                          ,type_product_id  \
                                          ,group_hd \
                                          ,image_name \
                                          ,po_number \
                                          ,vendor_number \
                                          ,receiver_number \
                                          ,sum_po \
                                          ,tax_number \
                                                        \
                                          ,symbol \
                                          ,bill_number \
                                          ,city_name \
                                          ,city_address \
                                          ,status_other \
                                          ,bill_date \
                                          ,ket_thuc_dot_number \
                                          ,user_id_up \
                                          ,user_id_change \
                                          ,upload_date \
                                                        \
                                          ,kt_comment \
                                          ,ttpp_comment \
                                          ,result_check \
                                          ,result_check_luoi \
                                          ,check_trung \
                                          ,is_qa \
                                          ,is_po \
                                          ,is_hddt \
                                          ,is_ttpp \
                                                        \
                                          ,is_rpa \
                                          ,has_report \
                                          ,src_image \
                                          ,src_pdf \
                                          ,src_xml \
                                          ,src_receiver, report_number, api_ktt) VALUES \
                                     (%s, %s , %s, %s, %s, %s , %s, %s, %s, %s , %s, %s, %s, %s , %s, %s ,%s, %s , %s, %s, \
                                     %s, %s , %s, %s, %s, %s , %s, %s, %s, %s , %s, %s, %s, %s , %s, %s, %s)"
                list_ADD = [listcus_id
                    , status_id
                    , type_product_id
                    , group_hd
                    , image_name
                    , po_number
                    , vendor_number
                    , receiver_number
                    , sum_po
                    , tax_number

                    , symbol
                    , bill_number
                    , city_name
                    , city_address
                    , status_other
                    , bill_date
                    , ket_thuc_dot_number
                    , user_id_up
                    , user_id_change
                    , upload_date

                    , kt_comment
                    , ttpp_comment
                    , result_check
                    , result_check_luoi
                    , check_trung
                    , is_qa
                    , is_po
                    , is_hddt
                    , is_ttpp

                    , is_rpa
                    , has_report
                    , src_image
                    , src_pdf
                    , src_xml
                    , src_receiver
                    , report_number
                    , api_ktt
                ]
                with connections['default'].cursor() as cur:
                    check = cur.execute("Select 1 FROM ["+str(listcus_id)+"|bill] WHERE image_name = '"+str(image_name)+"' ").fetchone()
                    if check is None :
                        sql_insert = cur.execute(sql,list_ADD)
                # count+=1
                # print(count)
            except Exception as e :
                print(e)
                list_id_faid.append(item[0])
        with open("E:\\WEB-SERVICE\\Sgc-2.0\\coopfood_service\\Service_Coop_Food\\log.txt", 'a') as file:
            file.write('\n' + str(table_name) + " : " + str(list_id_faid) + '\n')
    return HttpResponse('OKE')

def recover_cus(request):
    num = 5555
    list_fail = []
    with connections['recover'].cursor() as cur:
        list_cus = cur.execute("SELECT * from listcus ").fetchall()
    for cus in list_cus:
        try:
            name = cus[2]
            address = cus[3]
            tax = cus[6] if cus[6] else str(num)
            gl = cus[7] if cus[7] else str(num)
            store = cus[8] if cus[8] else str(num)
            email_ktt = cus[10] if cus[10] else 'chuacomail@gmail.com'
            email_hddt = cus[11] if cus[11] else 'chuacomail@gmail.com'
            sod = cus[8] if cus[9] else str(num)
            des = cus[13]
            site = 1
            company_name = cus[5] if cus[5] else ''
            # created = ''
            # updated = ''
            ttpp = 0
            with atomic():
                new_cus = ListCus.objects.create(name = name, address = address, ttpp = ttpp, company_name= company_name, tax_number = tax
                                    , gl_number = gl, email_ktt = email_ktt, email_hddt=email_hddt,store_number = store,
                                    sod_number = sod, description = des, site_id = site)
                create_table_cus(str(new_cus.id))
            num +=1
        except Exception as identifier:
            print(identifier)
            list_fail.append(cus[0])
    return HttpResponse("oke")

def recover_user(request):
    list_fail = []
    with connections['recover'].cursor() as cur:
        list_user = cur.execute("SELECT * from allusercoop  where role  in ('NH', 'QL', 'KT', 'KHO')   ").fetchall()
    for user in list_user:
        try:
            name = user[2]
            passw = user[3]
            email = user[5]
            is_actived = 1
            phone = user[17]
            manager_cus_find = []
            type_ttpp = user[14] if user[16] else 0
            if user[1] == 'QL':
                manager_cus = user[16].split(',')
                manager_cus_find = ListCus.objects.filter(name__in=manager_cus).values_list('id', flat=True)
            with connections['recover'].cursor() as cur:
                find_cus = cur.execute("SELECT cusname from listcus  where id = "+str(user[13])+"").fetchone()[0]
            cus_id = ListCus.objects.filter(name=find_cus).first().id
            role_id = Role.objects.filter(symbol = user[1]).first().id
            if manager_cus_find:
                pass
            else:
                manager_cus_find = [int(cus_id)]
            with atomic():
                new_cus = UserCoop.objects.create(username = name, password = make_password(passw), phone_number = phone,
                                                  role_id=role_id, cus_id = cus_id, type_ttpp = type_ttpp)
                manager_cus_add = ListCus.objects.filter(id__in=(manager_cus_find))
                new_cus.manager_cus.add(*manager_cus_add)
        except Exception as e:
            print(e)
            list_fail.append(user[0])
    print(list_fail)
    return HttpResponse("oke")


def recover_invoice_list(request):
    if request.method == "GET":
        list_fail = []
        table_year = request.GET.get('name')
        list_month = ['02', '03', '04', '05', '06', '07', '08', '09', '10', '11' ,'12']
        for month in list_month:
            table_name = table_year + month
            with connections['recover'].cursor() as cur:
                list_invoice = cur.execute(
                    "SELECT id, [ImageName] \
                    ,[TypeBK] \
                      ,[NhaCungCap] \
                      ,[SoBangKe] \
                      ,[SoPO] \
                      ,[Receiver] \
                      ,[Vender] \
                      ,[ResultCheckLuoi] \
                      ,[Status] \
                      ,[ThucTrang] \
                      ,[Uploaddate] \
                      ,[LastChangeDate] \
                      ,[IdCus] \
                      ,[UserIdChange] \
                    ,[UserIdUp] \
                    from [BK|" + str(table_name) + "] where idcus in (111,112,113,114,126,127,128,129,130) ").fetchall()

            for invoice in list_invoice:
                try:
                    with connections['recover'].cursor() as cur:
                        a = cur.execute("SELECT phanloai from phanloai where id = "+str(invoice.TypeBK)+"").fetchone()[0]
                        type_bk = TypeProduct.objects.filter(name = a).first().id
                    number = invoice.SoBangKe
                    po_number = invoice.SoPO
                    rece_number = invoice.Receiver
                    vendor_number =invoice.Vender
                    is_qa = 1 if invoice.ThucTrang  == 'QA' else 0
                    upload_date  = invoice.Uploaddate
                    last_change  = invoice.LastChangeDate
                    src_image = 'img' + '/' + str(invoice.ImageName)[2:8] + '/' + invoice.ImageName

                    # user_id_up = invoice.UserIdUp


                    with connections['recover'].cursor() as cur:
                        ma = cur.execute("SELECT name from allusercoop where  id = "+str(invoice.UserIdUp)+"").fetchone()[0]
                    user = UserCoop.objects.filter(username=ma)
                    if user.exists():
                        user_id_up = user.first().id
                        cus = user.first().cus.id
                    else:
                        user_id_up = 1

                    sql = "INSERT INTO dbo.["+str(cus)+"|bk] (listcus_id, image_name, type_bk, bk_number, po_number, receiver_number, is_qa, user_id_up, result_check, upload_date, src_img)" \
                                                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    with connection.cursor() as cur:
                        check = cur.execute("Select 1 FROM dbo.["+str(cus)+"|bk] WHERE image_name = '"+str(invoice.ImageName)+"' ").fetchone()
                    list_add = [cus,invoice.ImageName, type_bk, number, po_number, rece_number, is_qa, user_id_up, invoice.ResultCheckLuoi, invoice.Uploaddate, src_image]
                    if check is None :
                        with connection.cursor() as cur:
                            cur.execute(sql, list_add)
                except Exception as e:
                    print(e)
                    list_fail.append(invoice.id)
            print(list_fail)
            with open("E:\\WEB-SERVICE\\Sgc-2.0\\coopfood_service\\Service_Coop_Food\\log_bk.txt", 'a') as file:
                file.write('\n' + str(table_name) + " : " + str(list_fail) + '\n')
        return HttpResponse("OKE")


def recover_report(request):
    if request.method == 'GET':
        table_year = request.GET.get('name')
        thang = request.GET.get('mont')
        cus_from = request.GET.get('cus')
        
        list_month =thang.split(',') #['01','02', '03', '04', '05', '06', '07', '08', '09', '10', '11' , '12']
        for month in list_month:
            list_fail = []
            table_name = table_year + str(month)
            with connections['recover'].cursor() as cur:
                list_report = cur.execute("SELECT sobb,soxe,sohd,sku ,tenhanghoa ,dongia, sl,grouphd, xulyttpp, comment, datecreate,useridcreate,tinhtranghd from [BB|"+str(table_name)+"] as tb1 inner join dbo.AllUserCoop as tb2 on tb1.useridcreate = tb2.name where tb2.IdCty in ("+cus_from+")").fetchall()

            for report in list_report:
                try:
                    number_report = report.sobb
                    number_xe = report.soxe
                    bill_numbers = report.sohd[1:].split('‡')
                    product_codes = report.sku[1:].split('‡')
                    product_names = report.tenhanghoa[1:].split('‡')
                    product_units = report.dongia[1:].split('‡')
                    product_amounts = report.sl[1:].split('‡')
                    status_bills = report.tinhtranghd[1:].split('‡')
                    group_bill = report.grouphd
                    ttpp_executes = report.xulyttpp[1:].split('‡')
                    comment_create = report.comment
                    date = report.datecreate


                    user = UserCoop.objects.filter(username=report.useridcreate).select_related('cus')
                    if user.exists():
                        user_id_create_id = user.first().id
                        id_cus = user.first().cus.id
                    else:
                        user_id_create_id = 1
                        id_cus = 1
                    with atomic():
                        new_report = Report.objects.create(group_bill=group_bill, drive_number=number_xe,
                                                           comment_create=comment_create,
                                                           number=number_report, user_id_create_id=user_id_create_id,
                                                           cus_id_id=id_cus, created_at = date)
                        new_report.created_at = date
                        new_report.save()
                        list_add_result = []
                        for index in range(len(bill_numbers)):
                            Report_ResultCheck.objects.create(report_id=str(new_report.id),
                                                              bill_number=str(bill_numbers[index]),
                                                              sku=str(product_codes[index]),
                                                              name=str(product_names[index]),
                                                              quanty=str(bill_numbers[index]),
                                                              unit=str(product_units[index]),
                                                              status=str(status_bills[index]),
                                                              solution=str(ttpp_executes[index]))
                except Exception as e:
                    print(e)
                    list_fail.append(report.grouphd)
            print(list_fail)
            with open("E:\\WEB-SERVICE\\Sgc-2.0\\coopfood_service\\Service_Coop_Food\\log_report.txt", 'a') as file:
                file.write('\n' + str(table_name) + " : " + str(list_fail) + '\n')
        return HttpResponse("OKE")

def create_table_cus(id_cus):
    query_create_table_ife = 'CREATE TABLE [dbo].[' + id_cus + '|bill](                                        \
            [id] [int] IDENTITY(1,1) NOT NULL,                                        \
            [listcus_id] [int] NOT NULL,                                        \
            [status_id] [int] NOT NULL,                                        \
            [type_product_id] [int] NULL,                                        \
            [group_hd] [nvarchar](100) NOT NULL,                                        \
            [image_name] [nvarchar](100) NOT NULL,                                        \
            [po_number] [nvarchar](100) NULL,                                        \
            [vendor_number] [nvarchar](100) NULL,                                        \
            [receiver_number] [nvarchar](max) NULL,                                        \
            [sum_po] [nvarchar](100) NULL,                                        \
            [tax_number] [nvarchar](100) NULL,                                        \
            [symbol] [nvarchar](100) NULL,                                        \
            [bill_number] [nvarchar](100) NULL,                                        \
            [city_name] [nvarchar](max) NULL,                                        \
            [city_address] [nvarchar](max) NULL,                                        \
            [status_other] [nvarchar](100) NULL,                                        \
            [bill_date] [nvarchar](100) NULL,                                        \
            [ket_thuc_dot_number] [int] NULL,                                        \
            [user_id_up] [int] NOT NULL,                                        \
            [user_id_change] [int] NULL,                                        \
            [upload_date] [datetime] NOT NULL,                                        \
            [date_change_kho] [datetime]  NULL,                                        \
            [kt_comment] [nvarchar](max) NULL,                                        \
            [ttpp_comment] [nvarchar](max) NULL,                                        \
            [result_check] [nvarchar](max) NULL,                                        \
            [result_check_luoi] [nvarchar](max) NULL,                                        \
            [check_trung] [nvarchar](max) NULL,                                        \
            [is_qa] [bit] NULL DEFAULT 0,                                        \
            [is_po] [bit] NULL DEFAULT 0,                                        \
            [is_hddt] [bit] NULL DEFAULT 0,                                        \
            [is_ttpp] [bit] NULL DEFAULT 0,                                        \
            [is_rpa] [bit] NULL DEFAULT 0,                                        \
            [api_ktt] [nvarchar](100) NULL,                                        \
            [has_report] [bit] NULL DEFAULT 0,                                        \
            [report_number] [nvarchar](100) NULL,                                      \
            [src_image] [nvarchar](max) NULL,                                        \
            [src_pdf] [nvarchar](max) NULL,                                        \
            [src_xml] [nvarchar](max) NULL,                                        \
            [src_receiver] [nvarchar](max) NULL,                                        \
            [nh_comment] [nvarchar](max) NULL,                                        \
            [last_change_date] [datetime] NULL,                                        \
            [status_rpa] [nvarchar](150) NULL,                                        \
            [user_receiver] [nvarchar](150) NULL,                                        \
             CONSTRAINT [PK_' + id_cus + '|bill] PRIMARY KEY CLUSTERED                                         \
            (                                        \
                [id] ASC                                        \
            )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]                                        \
            ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]'
    query_create_table_log = 'CREATE TABLE [dbo].[' + id_cus + '|log_change_status](                                        \
            [id] [int] IDENTITY(1,1) NOT NULL,                                        \
            [listcus_id] [int] NOT NULL,                                        \
            [user_id] [int] NOT NULL,                                        \
            [type] [nvarchar](50) NULL,                                        \
            [old_status] [nvarchar](max) NULL,                                        \
            [new_status] [nvarchar](max) NULL,                                        \
            [other_status] [nvarchar](max) NULL,                                        \
            [date_change] [datetime] NULL,                                        \
            [group_hd] [nvarchar](max) NULL,                                        \
            [bill_id] [int] NULL,                                                     \
        CONSTRAINT [PK_' + id_cus + '|log_change_status] PRIMARY KEY CLUSTERED                                         \
            (                                        \
                [id] ASC                                        \
            )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]                                        \
            ) ON [PRIMARY]'
    query_create_table_bk = 'CREATE TABLE [dbo].[' + id_cus + '|bk](                                        \
            [id] [int] IDENTITY(1,1) NOT NULL,                                        \
            [listcus_id] [int] NOT NULL,                                        \
            [image_name] [nvarchar](100) NULL,                                        \
            [type_bk] [nvarchar](30) NULL,                                        \
            [bk_number] [nvarchar](100) NULL,                                        \
            [po_number] [nvarchar](100) NULL,                                        \
            [receiver_number] [nvarchar](100) NULL,                                        \
            [vendor_number] [nvarchar](100) NULL,                                        \
            [result_check] [nvarchar](max) NULL,                                        \
            [src_img] [nvarchar](max) NULL,                                        \
            [upload_date] [datetime] NULL,                                        \
            [last_change_date] [datetime] NULL,                                        \
            [src_receiver] [nvarchar](max) NULL,                                        \
            [is_qa] [bit] NULL DEFAULT 0,                                        \
            [user_id_up] [int] NOT NULL,                                        \
            [user_id_change] [int] NULL,                                        \
             CONSTRAINT [PK_' + id_cus + '|bk] PRIMARY KEY CLUSTERED                                         \
            (                                        \
                [id] ASC                                        \
            )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]                                        \
            ) ON [PRIMARY]'
    with connection.cursor() as cur:
        cur.execute(query_create_table_ife)
        cur.execute(query_create_table_log)
        cur.execute(query_create_table_bk)


def find_new_from_old(old, new , dict_old, dict_new):
    try:
        pass
    except Exception as e:
        return ''

def get_new_from_old():
    with connections['recover'].cursor() as cur:
        sql_old_name_cus = cur.execute("SELECT id, cusname from listcus ").fetchall()
        sql_old_type_product = cur.execute("SELECT id, phanloai from dbo.PhanLoai ").fetchall()
        sql_old_user = cur.execute("SELECT id, name from dbo.AllUserCoop ").fetchall()
    dict_old_name_cus = {}
    dict_old_type_product = {}
    dict_old_user = {}   

    dict_new_name_cus = {}
    dict_new_type_product = {}
    dict_new_user = {}
    dict_new_status = {}

    for cus in sql_old_name_cus:
        dict_old_name_cus[cus.cusname] = cus.id
    for product in sql_old_type_product:
        dict_old_type_product[product.phanloai] = product.id
    for user in sql_old_user:
        dict_old_user[user.name] = user.id

    sql_new_cus = ListCus.objects.all().values('id', 'name')
    sql_new_user = UserCoop.objects.all().values('id', 'username')
    sql_new_type_product = TypeProduct.objects.all().values('id', 'name')
    sql_new_status = StatusBill.objects.all().values('id', 'symbol')

    for cus in sql_new_cus:
        dict_new_name_cus[cus['name']] = cus['id']
    for product in sql_new_type_product:
        dict_new_type_product[product['name']] = product['id']
    for user in sql_new_user:
        dict_new_user[user['username']] = user['id']
    for user in sql_new_status:
        dict_new_status[user['symbol']] = user['id']

    dict_cus_return = {}
    dict_type_product_return = {}
    dict_user_return = {}

    for x, y in dict_old_name_cus.items():
        try:
            dict_cus_return[y] = dict_new_name_cus[x]
        except:
            pass

    for x, y in dict_old_type_product.items():
        try:
            dict_type_product_return[y] = dict_new_type_product[x]
        except:
            pass

    for x, y in dict_old_user.items():
        try:
            dict_user_return[y] = dict_new_user[x]
        except:
            pass
    return [dict_cus_return, dict_user_return, dict_type_product_return,dict_new_status]