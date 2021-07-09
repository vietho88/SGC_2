from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,HttpResponseRedirect
from Service.decorators import allowed_user, allowed_permission, allowed_cus_manager
from django.utils.decorators import method_decorator
from Service.models import *
import datetime
from Service.common import common_function
from django.db import connection
# Create your views here.

class Statistical(View):
    def get(self, request):
        list_cus_manager = request.user.manager_cus.all().values('id', 'name', 'store_number')
        cus_chosed = request.GET.get('selectbranch', list_cus_manager[0]['id'])                     ### chọn chi nhánh
        date_from = request.GET.get('timeStart', datetime.datetime.now().strftime('%d/%m/%Y'))
        date_to = request.GET.get('timeEnd', datetime.datetime.now().strftime('%d/%m/%Y'))
        list_per = request.user.role.role_permission.all().values_list('name', flat=True)
        request.session['list_per'] = list(list_per)
        date_from_convert = date_from[6:10] + '/' + date_from[3:5] + '/'+date_from[0:2] + ' 00:00:00'
        date_to_convert = date_to[6:10] + '/' + date_to[3:5] + '/'+date_to[0:2] + ' 23:59:59'
        ## save old url search

        query2 = " SELECT CONCAT(N'Trạng thái ',tb.status_symbol) , count (tb.group_hd) FROM \
                 (SELECT\
                    tb2.symbol as status_symbol, tb1.group_hd as group_hd \
                FROM \
                    [dbo].[" + str(cus_chosed) + "|bill] as tb1 \
                INNER JOIN \
                    [dbo].[service_statusbill] as tb2 \
                ON \
                    tb1.status_id = tb2.id \
                WHERE \
                    tb1.listcus_id = " + str(cus_chosed) + "  \
                    and upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'  \
                    and tb1.is_po <> 1 \
                GROUP BY \
                    tb2.symbol, tb1.group_hd) tb GROUP BY tb.status_symbol "
        with connection.cursor() as cursor:
            statistical = cursor.execute(query2).fetchall()

        data = [ list(x) for x in statistical]
        total = sum([ int(x[1]) for x in statistical ])
        data.insert(0, ['SỐ HÓA ĐƠN', '4444'])

        query3 = "SELECT  [pom] = (SELECT count(DISTINCT group_hd) FROM  [dbo].[" + str(cus_chosed) + "|bill] where  upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'   and  src_receiver !='' and ISNUMERIC(po_number)=1),\
                    [inv] = (SELECT count(DISTINCT group_hd) FROM  [dbo].[" + str(cus_chosed) + "|bill] where  upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'      and  src_receiver !='' and ISNUMERIC(po_number)=0)"
        # query_pom ="SELECT count(DISTINCT group_hd)   FROM  [dbo].[" + str(cus_chosed) + "|bill] where  upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'    and  ISnull(src_receiver,'') !='' and ISNUMERIC(po_number)=1       "
        # query_inv ="SELECT count(DISTINCT group_hd)   FROM  [dbo].[" + str(cus_chosed) + "|bill] where  upload_date > '" + date_from_convert + "' and upload_date < '" + date_to_convert + "'    and  ISnull(src_receiver,'') !='' and ISNUMERIC(po_number)=0       "
        pom = 0
        inv = 0
        with connection.cursor() as cursor:
            pom_ = cursor.execute(query3).fetchone()
        pom = int(pom_[0]) 
        inv = int(pom_[1]) 
      
        data_pom=[['POM',pom],['INV',inv]]
        data_pom.insert(0, ['SỐ HÓA ĐƠN', '4444'])
        total_pom = (pom+inv)
        # data1 = [ list(x) for x in statistical_po]
        # total_po = sum([ int(x[1]) for x in statistical_po ])
        # data1.insert(0, ['SỐ HÓA ĐƠN', '4444'])

        context = {
            'date_from': date_from,
            'date_to': date_to,
            'list_cus': list_cus_manager,
            'list_per': list_per,
            'cus_chosed': int(cus_chosed),
            'total': total,
            'data' : data,
            'total_pom': total_pom,
            'data_pom': data_pom,
            
        }
        return render(request, 'statistical/statistical_home.html', context=context)

    def post(self, request):
        pass


