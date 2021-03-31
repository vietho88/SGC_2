from django.db import models
from django.contrib.auth.models import  AbstractUser

class Site(models.Model):
    name = models.CharField(max_length=500, null=False, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ListCus(models.Model):
    name = models.CharField(
        max_length=500,
        unique=True,
        null=False
    )
    address = models.CharField(
        max_length=500,
        null= True,
        blank=True
    )
    ttpp = models.IntegerField(
        null=True,
        blank=True
    )
    company_name = models.CharField(
        max_length=1000,
        null=False,
        default=''
    )
    tax_number = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )
    gl_number = models.CharField(
        max_length= 50,
        null=True,
        blank=True,
    )
    email_ktt = models.EmailField(
        default='',
        blank=True
    )
    email_hddt = models.EmailField(
        default='',
        blank=True
    )
    store_number = models.IntegerField(
        unique=True,
        null=False,
        blank=False,
    )
    sod_number = models.CharField( #####nên edit lại thành charfield
        max_length= 20,
        null=True,
        blank=True,
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    is_lock = models.BooleanField(
        null=True,
        blank=True,
        default=False
    )
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ###save old id cus from 1.0
    id_old = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    symbol = models.CharField(
        max_length=10,
        default='',
        null=False,
        blank=False
    )
    name = models.CharField(
        max_length=255,
        default='',
        null=False,
        blank=False
    )
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Permission(models.Model):
    name = models.CharField(
        max_length=255,
        default='',
        null=False,
        blank=False
    )
    role = models.ManyToManyField(Role, through='RolePermission', related_name="role_permission")
    type = models.IntegerField(null=True, blank=True, choices=[[1,'Hóa đơn'], [2, 'Bảng kê'], [3, 'Biên bản'], [4, 'Khác']])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StatusBill(models.Model):
    name = models.CharField(
        max_length=500,
    )
    symbol = models.CharField(
        unique=True,
        max_length=10
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class TypeProduct(models.Model):
    name = models.CharField(
        max_length=500,
    )
    symbol = models.CharField(
        unique=True,
        max_length=10
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    type = models.IntegerField(
        null=False,
        default=1, 
        choices=[
            [1,'Hàng khô'],
            [2,'Hàng ướt'],
            [3,'Bảng kê'],
        ]
    )
    is_camera = models.BooleanField(
        default=False
    )
    index = models.IntegerField(
        null=True,
        blank=True
    )
    ###Check những ngnahf hàng được hiển thị
    is_show = models.BooleanField(
        null=True,
        blank=True,
        default=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# class UserManagerCus(models.Model):
#     user = models.ForeignKey(UserCoop, related_name=user, on_delete=models.CASCADE)
#     cus = models.ForeignKey()

class UserCoop(AbstractUser):
    level = models.IntegerField(
        null=True,
        blank=True
    )
    type_ttpp = models.IntegerField(
        null=True,
        blank=True
    )
    manager_cus = models.ManyToManyField(ListCus, related_name='manager_cus')
    is_lock = models.BooleanField(
        default=False,
        blank=True
    )
    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True
    )
    is_take_photo = models.BooleanField(default=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    cus = models.ForeignKey(ListCus, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    type = models.IntegerField(
        default=1,
        null=False,
    )
    detail = models.TextField(
        null= True,
        blank= True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.permission.name
    


class Report(models.Model):
    group_bill = models.CharField(max_length=30, null=True, blank=True)
    drive_number = models.CharField(max_length=25, null=True, blank=True)
    comment_ttpp = models.TextField(
        null=True,
        blank=True
    )
    comment_create = models.TextField(
        null=True,
        blank=True
    )
    number = models.IntegerField(null=True, blank=True)
    user_id_create = models.ForeignKey(UserCoop, on_delete=models.CASCADE, related_name='user_id_create', null=True, blank=True)
    user_id_last_change = models.ForeignKey(UserCoop, on_delete=models.CASCADE, related_name='user_id_last_change', null=True, blank=True)
    cus_id = models.ForeignKey(ListCus, on_delete=models.CASCADE, null=True, blank=True)
    cus_ttpp = models.ForeignKey(ListCus, on_delete=models.CASCADE, null=True, blank=True, related_name='cus_ttpp')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Report_ResultCheck(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True,blank=True)
    bill_number = models.CharField(max_length=25, null=True, blank=True)
    sku = models.CharField(max_length=25, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    quanty = models.CharField(max_length=255, null=True, blank=True)
    unit = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(max_length=500, null=True, blank=True)
    solution = models.CharField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class PermissionChangeStatus(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    site = models.CharField(max_length=20, null=True, blank=True)
    recent_status = models.CharField(max_length=2, null=False, blank=False, default='')
    new_status = models.CharField(max_length=50,null=False,blank=False,default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.recent_status   

class TypeLog(models.Model):
    number = models.IntegerField(
        null=True,
        blank=True
    )
    type = models.CharField(
        max_length=300, null=True, blank=True
    )

    def __str__(self):
        return self.type



