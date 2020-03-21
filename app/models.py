from django.db import models
from django.contrib.auth.models import User
import datetime


# Create your models here.

class Vending_Machine(models.Model):
    No = models.AutoField(primary_key=True)
    VM_No = models.CharField(unique=True, max_length=30)
    VM_Name = models.CharField(max_length=30, default='자판기별명')
    Owner_Username = models.ForeignKey(User, to_field='username', default='iot_vm', on_delete=models.CASCADE
                                       , related_name='Owner_Username')
    Supplier_Username = models.ForeignKey(User, to_field='username', default='iot_vm', on_delete=models.CASCADE
                                          , related_name='Supplier_Username')
    Longitude = models.TextField(null=True, blank=False)
    Latitude = models.TextField(null=True, blank=False)
    Address = models.TextField(null=True, blank=False)
    TotalCount = models.IntegerField(null=False, default=0)
    TotalSales = models.IntegerField(null=False, default=0)
    Firmware_Version = models.FloatField(default=1.00, null=True)
    IsSelling = models.BooleanField(null=False, default=True)
    IsWorking = models.IntegerField(default=0, null=False)
    VM_IsEmpty = models.BooleanField(null=False, default=False)
    StartTime = models.TimeField(default=datetime.time(7, 00))
    EndTime = models.TimeField(default=datetime.time(0, 00))
    UpdateTime = models.DateTimeField(default=datetime.datetime.now())
    Model_Num = models.CharField(max_length=30, null=False, default='1111')
    Error = models.CharField(max_length=20)
    Max_Product_Cell = models.IntegerField(null=True)
    Body_Size = models.TextField(null=True, blank=False)
    ImageURL = models.TextField(null=True, blank=False)
    Display_Size = models.TextField(null=True, blank=False)
    InternetCheck = models.BooleanField(null=False, default=True)
    CityName = models.CharField(null=True, max_length=50, default="경기도")

    class Meta:
        db_table = 'vending_machine'


class Account(models.Model):
    Account_Id = models.ForeignKey(User, primary_key=True, to_field="username", on_delete=models.CASCADE)
    Name = models.CharField(max_length=20, default='홍길동')
    PhoneNumber = models.CharField(max_length=20, default='01000000000')
    User_Status = models.IntegerField(null=True, default=1)
    
    class Meta:
        db_table = 'account'


class Video(models.Model):
    No = models.AutoField(primary_key=True)
    Video_No = models.IntegerField(unique=True)
    Video_URL = models.TextField(null=True, blank=False)
    title = models.CharField(max_length=30, default='제목')
    thumbnail = models.TextField(null=True, blank=False)
    VideoUpdateTime = models.DateTimeField(default=datetime.datetime.now())
    Account_Id = models.ForeignKey(Account, on_delete=models.CASCADE, to_field="Account_Id", default="1111")
    
    class Meta:
        db_table = 'video'


class Product(models.Model):
    No = models.AutoField(primary_key=True)
    Product_No = models.CharField(unique=True, max_length=30)
    Product_Name = models.CharField(max_length=30, default='상품명')
    ImageURL = models.TextField(null=True, blank=False)
    DetailImage = models.TextField(null=True, blank=False)
    Max_Num = models.IntegerField(null=False, blank=False, default=10)
    Size = models.IntegerField(null=False, blank=False, default=36)
    Width_Spring = models.IntegerField(null=False, blank=False, default=6)
    Owner_Username = models.ForeignKey(Account, to_field='Account_Id', on_delete=models.CASCADE, default='manager')
    IsRecommand = models.IntegerField(null=False, default=0)
    Price = models.IntegerField(null=False,default=1000)
    Video_No = models.ForeignKey(Video, on_delete=models.CASCADE, to_field="Video_No", default="1")
    IsPublic = models.IntegerField(null=False, default=1, blank=False)
    Company_Name = models.CharField(null=False, blank=False, max_length=100, default="venduster")
    ##category 추가할것


    #Width_Spring 은 트레이와 관련되어 있는 스프링의 넓이
    class Meta:
        db_table = 'product'

class VM_Product(models.Model):
    No = models.AutoField(primary_key=True)
    VM_No = models.ForeignKey(Vending_Machine, on_delete=models.CASCADE, to_field='VM_No')
    UI_No = models.IntegerField(null=False, default=2, unique=True)
    Current_Num = models.IntegerField(null=False, default=0)
    IsEmpty = models.BooleanField(null=False, default=False)
    DiscountedPrice = models.IntegerField(default=0)
    DueDiscountPrice = models.DateTimeField(null=True, blank=True)
    ProductUpdateTime = models.DateTimeField(null=False, default=datetime.datetime.now())
    IsPromotioned = models.BooleanField(default=0, null=False)
    IsChecked = models.IntegerField(default=0, null=False)
    IsPrivate = models.BooleanField(null=False, blank=False)
    Product_No = models.ForeignKey(Product, null=False, on_delete=models.CASCADE, to_field='Product_No', default="test001")

    class Meta:
        db_table = 'vm_product'


class Notice(models.Model):
    No = models.AutoField(primary_key=True)
    Notice_UpdateTime = models.DateTimeField(null=False, default=datetime.datetime.now())
    Title = models.CharField(max_length=30, default='제목')
    Detail = models.TextField(null=True, blank=False)

    class Meta:
        db_table = 'notice'


class VM_Product_Tray(models.Model):
    No = models.AutoField(primary_key=True)
    VM_No_Id = models.ForeignKey(Vending_Machine, on_delete=models.CASCADE, to_field='VM_No')
    Cell_No_Id = models.ForeignKey(VM_Product, on_delete=models.Case, to_field='UI_No')
    Tray_No = models.TextField(null=False, default="A")
    UpdateTime = models.DateTimeField(default=datetime.datetime.now())
    Quantity = models.IntegerField(default=1, null=False)
    #ConstractStatus 가 1이면 계약전, 2면 계약중 3이면 계약종

    class Meta:
        db_table = 'vm_product_tray'