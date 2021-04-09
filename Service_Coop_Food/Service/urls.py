"""Service_Coop_Food URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from Service.views import views, view_auth, view_admin, view_api
from Service.views.admin import view_branch, view_user, view_site, view_permission, view_role, view_status_bill, view_type_product, view_dashboard
from Service.views.home import view_home_ajax, view_home, view_statistical
from Service.views.warehouse import view_warehouse_ajax, view_warehouse
from Service.views.detail import view_detail_ajax, view_detail
from Service.views.report import view_report_ajax, view_report, view_report_warhouse
from Service.views.invoice_list import view_invoice_list, view_invoice_list_ajax
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.generic import TemplateView
urlpatterns = [
    re_path(r'^$', login_required(view_home.HomeView.as_view()), name='index'),
    path('login', view_auth.LoginView.as_view() , name ='login'),
    path('logout', login_required(view_auth.LogoutView.as_view()) , name ='logout'),
    path('changepass', login_required(view_auth.change_password) , name ='change_pass'),

    re_path(r'^home/bill$', login_required(view_home.HomeView.as_view()) , name ='home_bill'),
    re_path(r'^home/warehouse$', login_required(view_warehouse.WareHouseView.as_view()) , name ='home_warehouse'),

    re_path(r'^home/invoice-list$', login_required(view_invoice_list.InvoiceListView.as_view()) , name ='home_invoice_list'),
    re_path(r'^home/invoice_list_detail/(?P<cus_id>[0-9]{1,15})/(?P<id>[0-9]{1,15})$', login_required(view_invoice_list.DetailInvoiceList.as_view()) , name ='invoice_list_detail'),
    re_path(r'^home/print_statistical$', login_required(view_home.PrintStatistical.as_view()) , name ='print_statistical'),

    re_path(r'^detail/(?P<id_cus>[0-9]{1,29})/(?P<id>[0-9]{1,29})/(?P<index>[0-9]{1,9})$', login_required(view_detail.DetailBillView.as_view()) , name ='detail_bill'),

    re_path(r'^bill/report/(?P<id_cus>[0-9]{1,29})/(?P<id>[0-9]{1,29})/(?P<index>[0-9]{1,9})$', login_required(view_report.ReportBillView.as_view()) , name ='report_bill'),
    re_path(r'^bill/report/(?P<id_cus>[0-9]{1,29})/(?P<id>[0-9]{1,29})/(?P<index>[0-9]{1,9})/edit$', login_required(view_report.ReportEditView.as_view()) , name ='report_edit'),
    re_path(r'^bill/report_warehouse/(?P<id_cus>[0-9]{1,29})/(?P<id>[0-9]{1,29})/(?P<index>[0-9]{1,9})$', login_required(view_report_warhouse.ReportBillView.as_view()) , name ='report_edit_warehouse'),
    re_path(r'^bill/report/(?P<id_cus>[0-9]{1,29})/(?P<group>[0-9]{1,29})/print_report$', login_required(view_report.PrintReportPDFView.as_view()) , name ='report_print_pdf'),

    path('admin', login_required(view_dashboard.DashBoardView.as_view()), name='admin'),
    path('admin/role', login_required(view_role.RoleView.as_view()), name='admin_role'),
    path('admin/role/edit/<int:id>', login_required(view_role.RoleEditView.as_view()), name='admin_role_edit'),
    path('admin/role/add', login_required(view_role.RoleAddView.as_view()), name='admin_role_add'),
    path('admin/permission', login_required(view_permission.PermissionView.as_view()), name='admin_permission'),

    path('admin/user', login_required(view_user.UserView.as_view()), name='admin_user'),
    re_path(r'^admin/user/add$', login_required(view_user.UserAddView.as_view()), name='admin_user_add'),
    re_path(r'^admin/user/(?P<id>[0-9]{1,9})/edit$', login_required(view_user.UserEditView.as_view()), name='admin_user_edit'),
    path('admin/user/edit', login_required(view_user.UserEditView.as_view()), name='admin_user_edit'),
    path('admin/user/resetpass', login_required(view_user.reset_pass), name='admin_user_reset_pass'),
    re_path(r'^admin/user/export_excel$', login_required(view_user.export_excel_user), name='admin_user_export_excel'),
    re_path(r'^admin/user/import_excel$', login_required(view_user.import_excel_user), name='admin_user_import_excel'),
    re_path(r'^admin/user/import_excel/dowload_base_file$', login_required(view_user.import_excel_user_dowload_file), name='admin_user_import_excel_dowload_base_file'),

    path('admin/branch', login_required(view_branch.BranchView.as_view()), name='admin_branch'),
    path('admin/branch/edit', login_required(view_branch.BranchEditView.as_view()), name='admin_branch_edit'),
    re_path(r'^admin/branch/add$', login_required(view_branch.BranchAddView.as_view()), name='admin_branch_add'),
    re_path(r'^admin/branch/(?P<id>[0-9]{1,9})/edit$', login_required(view_branch.BranchEditView.as_view()), name='admin_branch_edit'),

    re_path(r'^admin/site$', login_required(view_site.SiteView.as_view()), name = 'admin_site'),
    re_path(r'^admin/site/edit/(?P<id>[0-9]{1,9})$', login_required(view_site.SiteEditView.as_view()), name = 'admin_site_edit'),
    re_path(r'^admin/site/delete/(?P<id>[0-9]{1,9})$', login_required(view_site.SiteDeleteView.as_view()), name = 'admin_site_delete'),
    re_path(r'^admin/site/add$', login_required(view_site.SiteAddView.as_view()), name = 'admin_site_add'),

    re_path(r'^admin/type_product$', login_required(view_type_product.TypeProductListView.as_view()), name = 'admin_type_product'),
    re_path(r'^admin/type_product/add$', login_required(view_type_product.TypeProductCreateView.as_view()), name = 'admin_type_product_add'),
    re_path(r'^admin/type_product/edit/(?P<pk>[0-9]{1,9})$', login_required(view_type_product.TypeProductUpdateView.as_view()), name = 'admin_type_product_edit'),
    re_path(r'^admin/type_product/delete/(?P<pk>[0-9]{1,9})$', login_required(view_type_product.TypeProductDeleteView.as_view()), name = 'admin_type_product_delete'),
    # re_path(r'^admin/site/edit/(?P<id>[0-9]{1,9})$', login_required(view_admin.SiteEditView.as_view()), name = 'admin_site_edit'),
    # re_path(r'^admin/site/delete/(?P<id>[0-9]{1,9})$', login_required(view_admin.SiteDeleteView.as_view()), name = 'admin_site_delete'),


    re_path(r'^ajax/datatable/home$', login_required(view_home_ajax.DataTableHomeView.as_view()), name="ajax_datatable_home"),
    re_path(r'^ajax/datatable/home/warehouse$', login_required(view_warehouse_ajax.DataTableHomeWareHouseView.as_view()), name="ajax_datatable_home_warehouse"),
    re_path(r'^ajax/datatable/home/invoice-list$', login_required(view_invoice_list_ajax.DataTableHomeInvoiceListView.as_view()), name="ajax_datatable_home_invoice_list"),
    re_path(r'^ajax/home/export_excel_report$', login_required(view_home_ajax.export_excel_report_home), name="ajax_home_export_excel_report"),
    re_path(r'^ajax/home/export_statistical$', login_required(view_home_ajax.export_statistical_home), name="ajax_home_export_statistical"),
    re_path(r'^ajax/home/get_batch_type_change_many_status$', login_required(view_home_ajax.get_batch_type_change_many_status), name="ajax_get_batch_type_change_many_status"),
    re_path(r'^ajax/home/get_bill_change_many_status$', login_required(view_home_ajax.get_group_bill_exchange_many_status), name="ajax_get_bill_change_many_status"),
    re_path(r'^ajax/home/print_pdf_pom$', login_required(view_home_ajax.print_pdf_pom), name="ajax_print_pdf_pom"),
    re_path(r'^ajax/home/change_many_status$', login_required(view_home_ajax.change_status_many_bill_one_time), name="ajax_change_many_status"),
    re_path(r'^ajax/detail_bill/update_status_group$', login_required(view_detail_ajax.update_status_group_bill), name="ajax_update_status"),
    re_path(r'^ajax/detail_bill/get_info_detail_bill$', login_required(view_detail_ajax.get_info_detail_bill), name="ajax_get_info_detail_bill"),
    re_path(r'^ajax/report/update_other_status$', login_required(view_report_ajax.update_other_status), name="ajax_update_report"),
    re_path(r'^ajax/invoice_list/find_bill_to_print_pom$', login_required(view_invoice_list_ajax.find_bill_to_print_pom), name="ajax_find_bill_to_print_pom"),
    ### url upload file pdf po
    re_path(r'^ajax/detail_bill/upload_pdf_po$', login_required(view_detail_ajax.upload_pdf_po), name="ajax_upload_pdf_po"),
    ### url get log (change status or edit detail bill)
    re_path(r'^ajax/detail_bill/get_log/(?P<id_cus>[0-9]{1,29})/(?P<group>[0-9]{1,29})/(?P<id>[0-9]{1,29})$', login_required(view_detail_ajax.get_log_to_show), name="ajax_get_log_show_detail"),
    re_path(r'^ajax/detail_bill/get_log_bk/(?P<id_cus>[0-9]{1,29})/(?P<id>[0-9]{1,29})$', login_required(view_invoice_list_ajax.get_log_to_show_bk), name="ajax_get_log_show_bk"),

    re_path(r'^ajax/admin/change_option_site_add_user$', login_required(view_detail_ajax.change_option_site_add_user), name="ajax_change_option_site_add_user"),
    re_path(r'^ajax/clear_mac$', login_required(view_home_ajax.clear_mac), name="ajax_clear_mac"),

    ### url to dowload file
    re_path(r'^dowload_media_file/(?P<type>(\w)+)/(?P<group_hd>[0-9]{1,29})/(?P<bill_id>[0-9]{1,9})/(?P<cus_id>[0-9]{1,9})$', login_required(view_detail.dowload_media_file),name="dowload_media_file"),

    ###recover database
    re_path(r'^recover_database$', login_required(views.recover_report), name="recover_database"),
    re_path(r'^recover_bill$', login_required(views.recover_report), name="recover_bill"),

    ###statitstical
    re_path(r'^home/statistical$', login_required(view_statistical.Statistical.as_view()), name="statistical"),

    ###api###
    re_path(r'^api/test$', view_api.HelloView.as_view(),name="api_test"),
    re_path(r'^api/update_info_group_bill$', view_api.HelloView.as_view(),name="api_update_info_group_bill"),
    re_path(r'^api/check_exist_bill$', view_api.api_check_exist_bill,name="api_check_exist_bill"),
    re_path(r'^api/check_exist_symbol_number$', view_api.api_check_exist_symbol_number,name="api_check_exist_symbol_number"),
    re_path(r'^api/api_update_group_bill$', view_api.api_update_group_bill,name="api_update_group_bill"),
    re_path(r'^api/api_export_excel$', view_api.api_export_excel,name="api_export_excel"),
    re_path(r'^api/api_export_excel_bangke$', view_api.api_export_excel_invoice_list,name="api_export_excel_bangke"),
    re_path(r'^api/upload_hddt_ttpp$', view_api.Upload_HDDT_TTPP, name="upload_hddt_ttpp"),
    re_path(r'^api/upload_hddt_ncc$', view_api.Upload_HDDT_NCC, name="upload_hddt_ncc"),
    re_path(r'^api/check_invoice_electronic$', view_api.check_Invoice_Electronic, name="check_invoice_electronic"),
    re_path(r'^api/change_status_image$', view_api.update_bill_for_image, name="api_change_status_image"),
    re_path(r'^api/update_status_hddt$', view_api.update_status_hddt, name="api_update_status_hddt"),
    re_path(r'^api/upload_pdf_receiver$', view_api.upload_pdf_receiver, name="api_upload_pdf_receiver"),
    re_path(r'^api/api_check_exist_bill$', view_api.api_check_exist_bill, name="api_check_exist_bill"),
    re_path(r'^api/auto_check_miss_po$', view_api.auto_check_miss_po, name="api_auto_check_miss_po"),
    re_path(r'^api/insert_po$', view_api.insert_po, name="insert_po"),
    re_path(r'^api/search_po$', view_api.search_po, name="search_po"),
    re_path(r'^api/update_po$', view_api.update_po, name="update_po"),
    path('.well-known/pki-validation/7FC3AD1E6612DC44F49BBC3AA599A335.txt', TemplateView.as_view(template_name="7FC3AD1E6612DC44F49BBC3AA599A335.txt", content_type='text/plain')),
]

if not settings.DEBUG:
    urlpatterns += [
        ###protected - media file ###
        re_path(r'^media/', view_auth.protected_media, name="protect_media"),
    ]