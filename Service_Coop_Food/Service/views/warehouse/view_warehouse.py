from django.shortcuts import render
from django.views import View
from django.http import HttpResponse,HttpResponseRedirect
from Service.decorators import allowed_user, allowed_permission
from django.utils.decorators import method_decorator
from Service.models import *
import datetime
from datetime import timedelta
# Create your views here.

class WareHouseView(View):
    @method_decorator(allowed_permission(allowed_per = 'Xem biên bản'))
    def get(self, request):
        len_get = len(request.GET)
        list_per = request.user.role.role_permission.all().values_list('name', flat =True)
        request.session['list_per'] = list(list_per)
        date = datetime.datetime.now().date()
        cus_chosed = None
        list_cus = None
        cus_ttpp = request.user.cus_id
        if len_get:
            cus_chosed = request.GET.get('selectbranch', None)
            date_from = request.GET.get('timeStart', date) ##dd/mm/Y
            date_to = request.GET.get('timeEnd', date)
            date_from_search = datetime.date(int(date_from[6:]), int(date_from[3:5]), int(date_from[0:2])) - timedelta(days=1)
            date_to_search = datetime.date(int(date_to[6:]), int(date_to[3:5]), int(date_to[0:2])) + timedelta(days=1)
        else:
            date_from_search = date - timedelta(days=1)
            date_to_search = date + timedelta(days=1)
            date_from =  date_to = date.strftime('%d/%m/%Y')

        cus_have_reports = Report.objects.filter(created_at__gte=date_from_search, created_at__lte=date_to_search,
                                                 cus_ttpp_id=cus_ttpp).values_list('cus_id', flat=True).distinct()

        if cus_have_reports.exists():
            if not cus_chosed:
                cus_chosed = cus_have_reports[0]
            list_cus =ListCus.objects.filter(pk__in = cus_have_reports)

        ## save old url search
        request.session['url_old_search_warse_house'] = request.get_full_path_info()
        context = {
            'date_from' :  date_from,
            'date_to' : date_to,
            'list_cus' : list_cus,
            'list_per' : list_per,
            'cus_chosed' : cus_chosed,
        }
        return render(request, 'home/warehouse.html', context)