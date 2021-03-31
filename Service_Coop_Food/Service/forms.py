from django import forms
from Service.models import *
from django.core.exceptions import ValidationError
import re
from django.db.models.functions import Concat
from django.db.models import Value

class ListCusCreateForm(forms.Form):
    # CHOICE_SITE = Site.objects.all().values_list('id', 'name')
    # CHOICE_SITE = []
    site = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={
                'class': 'form-control select-add-site'
            }
        ),
        queryset= Site.objects.all(),
        required=True
    )
    name = forms.CharField(
        label= "Tên chi nhánh",
        max_length=500,
        widget=forms.TextInput(
        attrs={
            'class': 'form-control input-name-cus', 'id': 'input_name',
            'required': 'required'
        }))
    address = forms.CharField(required=False, max_length=500, widget=forms.TextInput(
        attrs={
            'class': 'form-control input-adress-cus',
        }))
    company_name = forms.CharField(required=False, max_length=255, widget=forms.TextInput(
        attrs={
            'class': 'form-control input-company-name-cus',
        }))
    tax_number = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={
            'class': 'form-control input-tax-number-cus',
        }))
    gl_number = forms.CharField(required=False, max_length=255, widget=forms.TextInput(
        attrs={
            'class': 'form-control input-gl-number-cus',
        }))
    email_ktt = forms.EmailField(required=False, max_length=255, widget=forms.EmailInput(
        attrs={
            'class': 'form-control input-email-ktt-cus',
        }))
    email_hddt = forms.EmailField(required=False, max_length=255, widget=forms.EmailInput(
        attrs={
            'class': 'form-control input-email-hddt-cus',
        }))
    store_number = forms.IntegerField(required=True,  widget=forms.NumberInput(
        attrs={
            'class': 'form-control input-store-number-cus',
        }))
    sod_number = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={
            'class': 'form-control input-store-number-cus',
        }))
    description = forms.CharField(
        required=False,
        max_length=2000,
        widget=forms.TextInput(
        attrs={
            'class': 'form-control  input-description-profile-cus',
        }))

    ttpp = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class': 'form-control select-add-type-ttpp'
            }
        ),
        choices=[[0, 'Không phải Trung Tâm Phân Phối'], [1, 'Là Trung Tâm Phân Phối']]
    )


    def clean_name(self):
        name = self.cleaned_data['name']
        if ListCus.objects.filter(name=name).exists():
            raise ValidationError('Tên chi nhánh này đã tồn tại !!')
        return name

    def clean_store_number(self):
        store_number = self.cleaned_data['store_number']
        if len(str(store_number)) > 8:
            raise ValidationError('Mã cửa hàng lớn hơn quy định')
        if ListCus.objects.filter(store_number=store_number).exists():
            raise ValidationError('Mã cửa hàng là duy nhất, không được trùng lặp')
        return store_number

class ListCusEditForm(forms.Form):
    site = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={
                'class': 'form-control select-add-site'
            }
        ),
        queryset=Site.objects.all(),
        required=True
    )
    name = forms.CharField(
        max_length=500,
        widget=forms.TextInput(
        attrs={
            'class': 'form-control input-edit-name-cus', 'id': 'input_name',
            'required': 'required'
        }))
    address = forms.CharField(required=False,max_length=500, widget=forms.TextInput(
        attrs={
            'class': 'form-control input-edit-adress-cus'
        }))
    company_name = forms.CharField(required=False,max_length=255, widget=forms.TextInput(
        attrs={
            'class': 'form-control input-edit-company-name-cus'
        }))
    tax_number = forms.IntegerField(required=False,widget=forms.NumberInput(
        attrs={
            'class': 'form-control input-edit-tax-number-cus'
        }))
    gl_number = forms.CharField(required=False, max_length=255, widget=forms.TextInput(
        attrs={
            'class': 'form-control input-edit-gl-number-cus'
        }))
    email_ktt = forms.EmailField(required=False, max_length=255, widget=forms.EmailInput(
        attrs={
            'class': 'form-control input-edit-email-ktt-cus'
        }))
    email_hddt = forms.EmailField(required=False, max_length=255, widget=forms.EmailInput(
        attrs={
            'class': 'form-control input-edit-email-hddt-cus'
        }))
    store_number = forms.IntegerField( required=True, widget=forms.NumberInput(
        attrs={
            'class': 'form-control input-edit-store-number-cus'
        }))
    sod_number = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={
            'class': 'form-control input-edit-store-number-cus'
        }))
    description = forms.CharField(
        required=False,
        max_length=2000,
        widget=forms.TextInput(
        attrs={
            'class': 'form-control  input-edit-description-profile-cus',
        }))
    ttpp = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class': 'form-control select-add-type-ttpp'
            }
        ),
        choices=[[0, 'Không phải Trung Tâm Phân Phối'], [1, 'Là Trung Tâm Phân Phối']]
    )


class UserCreateForm(forms.Form):
    CHOICE_CUS = []
    CHOICE_ROLE = []
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-add-username',
                'required': 'required'
            }))
    email = forms.EmailField(
        max_length=50,
        widget=forms.EmailInput(
            attrs={
                'class' : 'form-control input-add-email',
            }
        ),
        required=False
    )
    phone_number = forms.DecimalField(
        max_digits=13,
        widget=forms.NumberInput(
            attrs={
                'class' : 'form-control input-add-phone-number',
            }
        ),
        required=False
    )
    role = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class' : 'form-control select-add-role',
                'required': 'true'

            }
        ),
        choices= CHOICE_ROLE
    )
    cus = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class' : 'form-control select-add-cus',
                'required': 'true'
            }
        ),
        choices= []
    )

    cus_manager = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-control select-add-cus-manager selectpicker  ',
                'title' : 'Chọn chi nhánh quản lý',
                'data-selected-text-format' : 'count > 4',
                'data-actions-box' : 'True'
            }
        ),
        choices= CHOICE_CUS

    )

    is_take_photo = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class': 'form-control ',
                'required': 'true'
            }
        ),
        choices=[[True, 'Có chụp hình'], [False, 'Không có chụp hình']]
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if UserCoop.objects.filter(username=username).exists():
            raise ValidationError('Tên người dùng này đã tồn tại trên hệ thống')
        return username


class UserEditForm(forms.Form):
    # CHOICE_CUS = ListCus.objects.all().order_by('id').values_list('id','name')
    # CHOICE_ROLE = Role.objects.all().values_list('id','name')
    # CHOICE_SITE = Site.objects.all().values_list('id', 'name')
    CHOICE_CUS = []
    CHOICE_ROLE = []
    site = forms.ModelChoiceField(
        widget=forms.Select(
            attrs={
                'class': 'form-control select-edit-site'
            }
        ),
        queryset=Site.objects.all()
    )
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-edit-username',
                'required': 'required',
            }))
    email = forms.EmailField(
        max_length=50,
        widget=forms.EmailInput(
            attrs={
                'class' : 'form-control input-edit-email',
            }
        ),
        required=False
    )
    phone_number = forms.DecimalField(
        max_digits=13,
        widget=forms.NumberInput(
            attrs={
                'class' : 'form-control input-edit-phone-number',
            }
        ),
        required=False
    )
    role = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class' : 'form-control select-edit-role',
                'required' : 'required'
            }
        ),
        choices= CHOICE_ROLE
    )
    cus = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class' : 'form-control select-edit-cus',
                'required' : 'required'
            }
        ),
        choices= CHOICE_CUS
    )
    cus_manager = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-control select-edit-cus-manager selectpicker  ',
                'title': 'Chọn chi nhánh quản lý',
                'data-selected-text-format': 'count > 4',
                'data-actions-box': 'True'
            }
        ),
        choices=CHOICE_CUS
    )

    is_take_photo = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                'class': 'form-control ',
                'required': 'true'
            }
        ),
        choices=[[True, 'Có chụp hình'], [False, 'Không có chụp hình']]
    )


    def clean_username(self):
        username = self.cleaned_data['username']
        if UserCoop.objects.filter(username=username).exists():
            raise ValidationError('Tên người dùng này đã tồn tại trên hệ thống')
        return username


class SiteAddForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        data = self.cleaned_data["name"]
        if Site.objects.filter(name=data).exists():
            raise ValidationError("name has exists")
        return data
    
class SiteEditForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
