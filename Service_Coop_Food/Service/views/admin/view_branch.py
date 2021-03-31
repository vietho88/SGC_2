from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from Service.decorators import allowed_user
from django.utils.decorators import method_decorator
from Service.models import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from Service.forms import *
from django.urls import reverse
import  json
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import  connection, connections
from django.contrib.auth.decorators import user_passes_test
import pyodbc
from django.conf import settings
# @method_decorator(user_passes_test(lambda u: u.is_superuser))
class BranchAddView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request):
        form_add_branch = ListCusCreateForm
        context = {
            'form_add_branch': form_add_branch,
        }
        return  render(request, 'admin/add_branch.html' , context)

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request):
        data_add = ListCusCreateForm(request.POST)
        if data_add.is_valid():
            with transaction.atomic():
                site = Site.objects.get(id=data_add.cleaned_data['site'].id)
                data = data_add.cleaned_data
                data.pop("site")
                new_cus = ListCus.objects.create(**data, site=site)
                create_table_cus(str(new_cus.id))
                ##create database old để chạy //
                with connections['recover'].cursor() as cur:
                    cur.execute("Insert into dbo.[ListCus] (Ctyid, CusName, Other,IdTTPP, TenCongTy, MaSoThue, GL, [Store],SodNumber, EmailKTT, EmailHDDT, Description, id_new)"
                                " values ('1', N'"+str(new_cus.name)+"', N'"+str(new_cus.address)+"', '1', N'"+str(new_cus.company_name)+"', N'"+str(new_cus.tax_number)+"', N'"+str(new_cus.gl_number)+"', N'"+str(new_cus.store_number)+"', '"+str(new_cus.sod_number)+"', N'"+str(new_cus.email_ktt)+"', N'"+str(new_cus.email_hddt)+"', N'"+str(new_cus.description)+"', '"+str(new_cus.id)+"')")
                    id_old = cur.execute("SELECT id FrOM listcus where cusname = N'"+str(new_cus.name)+"' ").fetchone()[0]
                    ListCus.objects.filter(id = new_cus.id).update(id_old = id_old)
            messages.success(request, 'success')
            return redirect(reverse('admin_branch'))

        else:
            for err in data_add.errors:
                messages.error(request, data_add.errors[err])
            form_add_branch_error = ListCusCreateForm(request.POST)
            return render(request, 'admin/add_branch.html', {
                'form_add_branch': form_add_branch_error,
                'message_error': data_add.errors
            })


class BranchView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request):
        find_name_cus = ''
        find_site = [Site.objects.first().id]
        form_add_branch = ListCusCreateForm
        form_edit_branch = ListCusEditForm
        # list_cus = ListCus.objects.filter(site__in = find_site)
        list_site = Site.objects.all()
        if len(request.GET) > 1 or (len(request.GET) == 1 and request.GET.get('page', '') == ''):
            find_name_cus = request.GET.get('input_search_branch', '')
            find_site = request.GET.getlist('select_site')

        list_cus = ListCus.objects.filter(name__contains=find_name_cus, site__in=find_site).select_related('site').order_by('-id')
        page_list_cus = Paginator(list_cus, settings.PAGINATOR_NUMBER)
        page_number = request.GET.get('page', 1)
        page_return = page_list_cus.get_page(page_number)
        context = {
            'list_cus': page_return,
            'list_site': list_site,
            'name_search': find_name_cus,
            'find_site': list(map(int, find_site)),
            'form_add_branch': form_add_branch,
            'form_edit_branch': form_edit_branch,
            'message_success': ''
        }
        return render(request, 'admin/branch.html', context)

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request):
        data_add = ListCusCreateForm(request.POST)
        if data_add.is_valid():
            site = Site.objects.get(id=data_add.cleaned_data['site'])
            data = data_add.cleaned_data
            data.pop("site")
            new_cus = ListCus.objects.create(**data, site=site)
            messages.success(request, 'success')
            return redirect(reverse('admin_branch'))

        else:
            print(data_add.errors)
            print(type(data_add.errors))
            form_add_branch_error = ListCusCreateForm(initial=data_add.cleaned_data)
            return render(request, 'admin/branch.html', {
                'form_add_branch': form_add_branch_error,
                'message_error': data_add.errors
            })


class BranchEditView(View):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request, id):
        # cus_id = request.GET.get('cus_id','')
        # if cus_id is not None:
        #     find_cus = ListCus.objects.filter(id=cus_id)
        #     if find_cus.exists():
        #         return JsonResponse({
        #             'message' : 'success',
        #             'data' : list(find_cus.values())
        #         },safe=False)
        # return JsonResponse({'message': 'error'}, safe=False)

        branch = ListCus.objects.filter(pk=id).values()[0]
        branch['site'] = ListCus.objects.filter(pk=id).first().site_id
        form_edit_branch = ListCusEditForm(initial=branch)
        context = {
            'form_edit_branch': form_edit_branch,
            'id_branch': id
        }
        return render(request, 'admin/edit_branch.html', context)

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def post(self, request, id):
        data_add = ListCusEditForm(request.POST)
        # cus_id = request.POST.get('input-diden-id')
        message_error = []
        if data_add.is_valid():
            name = data_add.cleaned_data['name']
            store_number = data_add.cleaned_data['store_number']

            current_cus = ListCus.objects.filter(id=id)
            edit_cus_name = ListCus.objects.filter(name=name)
            edit_cus_store = ListCus.objects.filter(store_number=store_number)

            if edit_cus_name.exists():
                if current_cus[0].name != edit_cus_name[0].name:
                    message_error.append('Chi nhánh này đã tồn tại !')
                    messages.error(request, 'Chi nhánh này đã tồn tại !')

            if len(str(store_number)) > 8:
                message_error.append('Mã cửa hàng này lớn hơn so với quy định !')
                messages.error(request, 'Mã cửa hàng này lớn hơn so với quy định !')
            else:
                if edit_cus_store.exists():
                    if current_cus[0].store_number != edit_cus_store[0].store_number:
                        message_error.append('Mã cửa hàng này đã tồn tại !')
                        messages.error(request, 'Mã cửa hàng này đã tồn tại !')

            if message_error:
                return HttpResponseRedirect(self.request.path_info)
            else:
                cus_updated = current_cus.update(**data_add.cleaned_data)
                messages.success(request, "Sửa thành công")
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        else:
            messages.error(request, data_add.errors)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

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

    """
       @type table log 
        1 : chuyển trạng thái hóa đơn
        2 : Sửa thông tin hóa đơn
        3 : Sửa thông tin biên bản, chuyển trạng thái biên bả
        4 : 
        5 : Sửa thông tin bảng kê
        6 : chuyển trạng thái hàng loạt  
        7 : update bằng api 
    """
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