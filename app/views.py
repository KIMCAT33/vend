
import json
import requests
import datetime
import socket
import queue
import os
import urllib.request
import datetime
import pprint
import ftplib
import pytz
import csv
import threading
import re

from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.edit import \
    CreateView  # 오브젝트를 생성하는 뷰 (form 혹은 model과 연결되서 새로운 데이터를 넣을 때 CreateView - generic view를 사용)
# from django.contrib.auth.forms import UserCreationForm  >>  장고의 기본 회원가입 폼 (ID, PW만 확인한다 - 뒤에서 이메일 추가 커스터미아징 예정)
from .forms import CreateUserForm  # 장고의 기본 회원가입 폼을 커스터마이징 한 폼
from django.urls import reverse_lazy  # generic view에서는 reverse_lazy를 사용한다.
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User
from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.serializers import ProductSerializer, VM_ProductSerializer, Vending_MachineSerializer, \
    VideoSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pprint import pprint
from pytz import timezone

from app.models import Product, VM_Product, Vending_Machine, Notice, Account, Video
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password,identify_hasher
import pytz
from .toast import get_token, ObjectService, ContainerService
import boto3
from boto3.dynamodb.conditions import Key, Attr


# CBV (Class Based View 작성!)
class CreateUserView(CreateView):  # generic view중에 CreateView를 상속받는다.
    template_name = 'registration/signup.html'  # 템플릿은?
    form_class = CreateUserForm  # 푸슨 폼 사용? >> 내장 회원가입 폼을 커스터마지징 한 것을 사용하는 경우
    # form_class = UserCreationForm >> 내장 회원가입 폼 사용하는 경우
    success_url = reverse_lazy('create_user_done')  # 성공하면 어디로?


class RegisteredView(TemplateView):  # generic view중에 TemplateView를 상속받는다.
    template_name = 'registration/signup_done.html'  # 템플릿은?



@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('VM_No', openapi.IN_QUERY, description="vending_machine's primary key",
                                          type=openapi.TYPE_STRING, required=True)])
@api_view((['GET']))
def vminfo_by_vm_no(request):

    return Response(Vending_Machine.objects.filter(VM_No=request.query_params['VM_No']).values(),
                    status=status.HTTP_202_ACCEPTED, content_type='application/json')




@swagger_auto_schema( method='post', request_body=openapi.Schema(
    type = openapi.TYPE_OBJECT,
    properties={
        'ID' : openapi.Schema(type=openapi.TYPE_STRING, description='ID : primarykey'),
        'Password' : openapi.Schema(type=openapi.TYPE_STRING, description='PW'),
        'Name' : openapi.Schema(type=openapi.TYPE_STRING, description='Name'),
        'Phone' : openapi.Schema(type=openapi.TYPE_STRING, description='Phone Number'),
        'Email' : openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
    }
))
@api_view(['POST']) #account -> auth_user로 join 시도를 해봐야함. ID, Password, Name, Phone, email, IsOwner 전송
def signup(request):
    res = []
    tmp = {}
    num = 1
    flag = False
    #일단 request 정보의 아이디 중복 여부를 확인해야 함.
    for info in User.objects.values():
        if request.data['ID'] == info['username']:
            flag = True
            break
        num = num + 1
    if(flag):
        tmp["ID_Check"] = 1
        res.append(tmp)
    else:
        #중복 여부가 없다면, 회원가입 진행.
        User.objects.create(id = num, username = request.data['ID'], password = make_password(request.data['Password']), email = request.data['Email'], is_active = 1)
        getUsername = User.objects.get(username = request.data['ID'])
        print(getUsername)
        Account.objects.create(Account_Id = getUsername, Name = request.data['Name'], PhoneNumber = request.data['Phone'])
        tmp["ID_Check"] = 0
        auth_url = 'https://127.0.0.1:8000/'                                             # local
        #auth_url = 'https://venduster.com/'                                            # toast cloud
        username = request.data['ID']
        password = request.data['Password']
        token_url = auth_url + 'api-token-auth/'
        body_data = {'username' : username, 'password' : password}
        requests.post(token_url, data = body_data, verify=False)
        res.append(tmp)
    result = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(result, content_type="text/json-comment-filtered")




@swagger_auto_schema( method='post', request_body=openapi.Schema(
    type = openapi.TYPE_OBJECT,
    properties={
        'ID' : openapi.Schema(type=openapi.TYPE_STRING, description='사용자 ID'),
        'Password' : openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호'),
    }, required=['ID', 'Password']
))
@api_view(['POST'])
def app_login(request):    # ID, PW 받고 Error여부와 Token을 보내줌.
    if request.method == 'POST':
        for datas in request.data:
            if request.data[datas] == "":
                return Response(request.data, status=status.HTTP_412_PRECONDITION_FAILED)
    res = []
    tmp = {}
    # 해당 ID가 있는지 탐색, 있으면 비밀번호를 기록해 놓는다.
    flag = False
    _id = 1
    for id in User.objects.values():
        if id['username'] == request.data['ID']:
            break;
        _id = _id + 1
    _password = "hggfghjhghnbghnbvghnbhnbhn"
    inputID = request.data['ID']
    #inputID = request.data['ID']
    No = 1
    for info in User.objects.values():
        if info['username'] == inputID:
            flag = True
            _password = info['password']
            No = info['id']

    #ID를 찾지 못한 경우
    if(flag == False):
        tmp['Error'] = 1
        res.append(tmp)
    else: #ID를 찾은 경우
        # 비밀번호가 맞는 경우 -> make_password 사용 시, 일대일 대응이 아닌 것 같음.
        if check_password(request.data['Password'], _password):
            tmp['Error'] = 0
            #token 넣는 과정 필요, is_active에 따라 다르게 나와야함.
            if(User.objects.filter(username = inputID)[0].is_active == 1):
                auth_url = 'https://127.0.0.1:8000/'                                             # local
                #auth_url = 'https://venduster.com/'                                            # toast cloud
                username = inputID
                password = request.data['Password']
                token_url = auth_url + 'api-token-auth/'
                body_data = {'username': username, 'password': password}
                token = requests.post(token_url, data=body_data, verify=False)
                tmp['Token'] = token.json()['token']
                tmp['User_Status'] = Account.objects.filter(Account_Id=inputID).values()[0]['User_Status']
            else:
                tmp['Token'] = "No agreement"
            res.append(tmp)
        # 비밀번호가 틀린 경우
        else:
            tmp['Error'] = 2
            res.append(tmp)
    result = json.dumps(res, cls=DjangoJSONEncoder)
    #db.close_connections()
    return HttpResponse(result, content_type="text/json-comment-filtered")


@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('ID', openapi.IN_QUERY, description="ID",
                                          type=openapi.TYPE_STRING, required=True)])
@api_view(['GET'])
def totalsales_by_user(request):    # ID를 받고 통해 자판기 별 총 매출 리스트 데이터(VM_No, VM_Name, TotalSales)를 전송해 줌.
    vm = Vending_Machine.objects.filter(Owner_Username_id = request.query_params['ID'])
    res = []
    for info in vm.values():
        tmp = info
        res.append(tmp)
    result = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(result, content_type="text/json-comment-filtered")

@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('ID', openapi.IN_QUERY, description="ID",
                                          type=openapi.TYPE_STRING, required=True)])
@api_view(['GET'])
def get_profile(request):    # ID를 받고 프로필을 전송해줌. (프로필 : 이름, 휴대폰번호)
    _userNo = User.objects.filter(username=request.query_params['ID'])
    userNo = _userNo.values()[0]['id']
    profile = Account.objects.filter(Auth_User_No = userNo)
    res = []
    for info in profile.values():
        tmp = info
        res.append(tmp)
    result = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(result, content_type="text/json-comment-filtered")


@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('ID', openapi.IN_QUERY, description="ID",
                                          type=openapi.TYPE_STRING, required=True)])
@api_view(['GET'])
def vmlist_by_id(request):    # ID를 받고 통해 자판기 별 총 매출 리스트 데이터(VM_No, VM_Name, TotalSales)를 전송해 줌.


    res = []
    if Vending_Machine.objects.filter(Owner_Username_id = request.query_params['ID']):
        vm = Vending_Machine.objects.filter(Owner_Username_id = request.query_params['ID'])
        for info in vm.values():
            tmp = info
            vm_product = VM_Product.objects.filter(VM_No=info['VM_No'])
            empty = False
            _datetime = datetime.datetime(2018,1,1,1,1,1)
            for info2 in vm_product.values():
                if(info2['IsEmpty'] and empty == False):
                    empty = True
                if(info2['ProductUpdateTime'] > _datetime.replace(tzinfo=pytz.UTC)):
                    _datetime = info2['ProductUpdateTime']
            tmp['VM_Soldout'] = empty
            tmp['VM_OpenDate'] = _datetime
            res.append(tmp)
        result = json.dumps(res, cls=DjangoJSONEncoder)
    elif Vending_Machine.objects.filter(Supplier_Username_id = request.query_params['ID']):
        vm = Vending_Machine.objects.filter(Supplier_Username_id=request.query_params['ID'])
        for info in vm.values():
            tmp = info
            vm_product = VM_Product.objects.filter(VM_No=info['VM_No'])
            empty = False
            _datetime = datetime.datetime(2018,1,1,1,1,1)
            for info2 in vm_product.values():
                if(info2['IsEmpty'] and empty == False):
                    empty = True
                if(info2['ProductUpdateTime'] > _datetime.replace(tzinfo=pytz.UTC)):
                    _datetime = info2['ProductUpdateTime']
            tmp['VM_Soldout'] = empty
            tmp['VM_OpenDate'] = _datetime
            res.append(tmp)
        result = json.dumps(res, cls=DjangoJSONEncoder)
    else:
        result = {"message" : "해당 아이디가 존재하지 않습니다.", "result" : "Failed"}
        result = json.dumps(result, cls=DjangoJSONEncoder)

    return HttpResponse(result, content_type="text/json-comment-filtered")


@api_view(['GET'])
def notice(request):    # 공지사항 모든 내용을 출력해줌.
    res = []
    for info in Notice.objects.values():
        tmp = {}
        tmp['No'] = info['No']
        tmp['Time'] = info['Notice_UpdateTime']
        tmp['Title'] = info['Title']
        tmp['Content'] = info['Detail']
        res.append(tmp)
    result = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(result, content_type="text/json-comment-filtered")


@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('VM_No', openapi.IN_QUERY, description="vending_machine's primary key",
                                          type=openapi.TYPE_STRING, required=True)])
@api_view((['GET']))
def sales_by_vm_no(request):    #VM_No에 해당하는 매출 데이터 전송(한달)
    res = []
    _month = datetime.datetime.now().month
    if os.environ['DJANGO_SETTINGS_MODULE'] == 'Venduster.settings.local' or os.environ[
        'DJANGO_SETTINGS_MODULE'] == 'Venduster.settings.development':
        for item in Dev_IotSellingData.scan(Dev_IotSellingData.VM_No == request.query_params['VM_No']):
            if _month == item.SoldTime.month:
                tproduct = Product.objects.filter(Product_No=item.Product_No).values()
                vproduct = VM_Product.objects.filter(VM_No_id=request.query_params['VM_No'],
                                                     Product_No_id=item.Product_No).values()
                tmp_json = {"No": item.No, "Product_No": item.Product_No, "VM_No" : item.VM_No, "Price": item.Price,
                          "DiscountedPrice": item.DiscountedPrice, "SoldTime": item.SoldTime,
                         "Product_Name" : tproduct[0]['Product_Name'], "Product_img" : vproduct[0]['CustomImageURL']}
                res.append(tmp_json)
    elif os.environ['DJANGO_SETTINGS_MODULE'] == 'Venduster.settings.production':
        for item in Prod_IotSellingData.scan(Prod_IotSellingData.VM_No == request.query_params['VM_No']):
            if _month == item.SoldTime.month:
                tproduct = Product.objects.filter(Product_No=item.Product_No).values()
                vproduct = VM_Product.objects.filter(VM_No_id=request.query_params['VM_No'],
                                                     Product_No_id=item.Product_No).values()
                tmp_json = {"No": item.No, "Product_No": item.Product_No, "VM_No" : item.VM_No, "Price": item.Price,
                          "DiscountedPrice": item.DiscountedPrice, "SoldTime": item.SoldTime,
                         "Product_Name" : tproduct[0]['Product_Name'], "Product_img" : vproduct[0]['CustomImageURL']}
                res.append(tmp_json)

    if(len(res) == 0):
        return Response("Empty")
    else:
        return Response(res, status=status.HTTP_202_ACCEPTED, content_type='application/json')



@swagger_auto_schema( method='post', request_body=openapi.Schema(
    type = openapi.TYPE_OBJECT,
    properties={
        'Product_No' : openapi.Schema(type=openapi.TYPE_STRING, description='기존 상품 엔티티에서 가져와서 vm_product에 삽입할 상품'),
        'CellNo' : openapi.Schema(type=openapi.TYPE_STRING, description='트레이 번호 예) A,B,C...'),
        'Current_Num': openapi.Schema(type=openapi.TYPE_INTEGER, description="트레이에 넣을 최대 상품 갯수"),
        'DiscountedPrice': openapi.Schema(type=openapi.TYPE_INTEGER, description="할인 적용된 판매가"),
        'DueDiscountPrice': openapi.Schema(type=openapi.TYPE_STRING, description="할인 기간"),
        'VM_No_id': openapi.Schema(type=openapi.TYPE_STRING, description="vending machine no")
    }, required=['Product_No', 'Current_Num', 'DiscountedPrice']
))
@api_view(['POST']) # Product 에 POST
def create_new_product_to_vm_product(request):
    
    if not VM_Product.objects.filter(CellNo = request.data['CellNo'], VM_No_id=request.data['VM_No_id'] ).values('CellNo').exists():

        if Product.objects.filter(Product_No=request.data['Product_No']).values('Product_No').exists():
            getProductNo = Product.objects.filter(Product_No = request.data['Product_No']).values()[0]['Product_No']
            print(getProductNo)
            VM_Product.objects.create(CellNo=request.data['CellNo'], Current_Num=request.data['Current_Num'],
                            DiscountedPrice=request.data['DiscountedPrice'],Product_No_id=getProductNo, IsPrivate = 0,
                            DueDiscountPrice=request.data['DueDiscountPrice'], ProductUpdateTime=datetime.datetime.now(), VM_No_id =request.data['VM_No_id'])

            result = {"message": "상품 입력이 성공적으로 진행되었습니다.", "result": "Success"}

            return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')

        else:
            return Response({"message:" : "등록되지 않은 상품 정보입니다"}, status=status.HTTP_412_PRECONDITION_FAILED, content_type='application/json')
    else:
        return Response({"message:" : "CellNo가 중복됩니다"}, status=status.HTTP_412_PRECONDITION_FAILED, content_type='application/json')

# remove_product_from_vm_product
@swagger_auto_schema( method='patch', request_body=openapi.Schema(
    type = openapi.TYPE_OBJECT,
    properties={
        'No' : openapi.Schema(type=openapi.TYPE_STRING, description='vm_product에서 삭제하고 싶은 상품 식별번호'),
    }, required=['No']
))
@api_view(['PATCH']) # Product 에 POST
def remove_product_from_vm_product(request):
    
    
    if VM_Product.objects.filter(No=request.data['No']).values('No').exists():
        
        queryset = VM_Product.objects.filter(No = request.data['No'])

        queryset.update(Current_Num=0, IsEmpty=1, DiscountedPrice=0, ProductUpdateTime=datetime.datetime.now(), IsPromotioned=0,
                        IsChecked=0, IsPrivate=0)

        result = {"message": "해당 상품이 성공적으로 VM_Product에서 삭제된 후 초기화되었습니다.", "result": "Success"}

        return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')

    else:
        return Response({"message:" : "등록되지 않은 상품 정보입니다"}, status=status.HTTP_412_PRECONDITION_FAILED, content_type='application/json')





# update_product_from_vm_product
@swagger_auto_schema( method='patch', request_body=openapi.Schema(
    type = openapi.TYPE_OBJECT,
    properties={
        'No' :openapi.Schema(type=openapi.TYPE_STRING, description="검색할 vm_product"),
        'Product_No' : openapi.Schema(type=openapi.TYPE_STRING, description='바꾸고싶은 상품'),
        'CellNo' : openapi.Schema(type=openapi.TYPE_STRING, description='변경할 트레이'),
        'Current_Num': openapi.Schema(type=openapi.TYPE_INTEGER, description="변경할 상품 수"),
        'DiscountedPrice': openapi.Schema(type=openapi.TYPE_INTEGER, description="할인 적용된 판매가"),
        'DueDiscountPrice': openapi.Schema(type=openapi.TYPE_STRING, description="할인 기간"),
        'VM_No_id': openapi.Schema(type=openapi.TYPE_STRING, description="자판기 정보"),
        'IsEmpty' : openapi.Schema(type=openapi.TYPE_BOOLEAN, description="매진 여부"),
        'IsPromotioned' : openapi.Schema(type=openapi.TYPE_BOOLEAN, description="홍보 비디오 재생 여부"),
        'IsPrivate' : openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Private 여부"),

    }, required=['No', 'Product_No', 'CellNo', 'Current_Num', 'DiscountedPrice', 'DueDiscountPrice', 'VM_No_id', 'IsEmpty',
        'Is_Promotioned', 'IsPrivate']
    )
)   
@api_view(['PATCH']) # Product 에 POST
def update_product_from_vm_product(request):
    
    
    if VM_Product.objects.filter(No=request.data['No']).values('No').exists():
        
        queryset = VM_Product.objects.filter(No=request.data['No'])

        queryset.update(Current_Num=request.data['Current_Num'], DiscountedPrice=request.data['DiscountedPrice'],Product_No=request.data['Product_No'],
                        DueDiscountPrice=request.data['DueDiscountPrice'], VM_No_id=request.data['VM_No_id'], IsEmpty=request.data['IsEmpty'],
                        IsPromotioned=request.data['IsPromotioned'], IsPrivate=request.data['IsPrivate'])

        result = {"message": "해당 상품이 성공적으로 VM_Product에서 수정되었습니다.", "result": "Success"}

        return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')

    else:
        return Response({"message:" : "등록되지 않은 vm_product 정보입니다"}, status=status.HTTP_412_PRECONDITION_FAILED, content_type='application/json')





@swagger_auto_schema( method='post', request_body=openapi.Schema(
    type = openapi.TYPE_OBJECT,
    properties={
        'VM_No' : openapi.Schema(type=openapi.TYPE_STRING, description='Vending Machine Number'),
        'Product_No' : openapi.Schema(type=openapi.TYPE_INTEGER, description = 'Product Number'),
        'Description' : openapi.Schema(type=openapi.TYPE_STRING, description='Custom Description'),
        'Price' : openapi.Schema(type=openapi.TYPE_INTEGER, description='Price'),
        'DiscountedPrice' : openapi.Schema(type=openapi.TYPE_INTEGER, description = 'Discounted Price'),
        'DueDiscountPrice' : openapi.Schema(type=openapi.TYPE_STRING, description = 'Due date of Discounting'),
        'CustomImageURL' : openapi.Schema(type=openapi.TYPE_STRING, description='CustomImageURL'),
        'CustomDetailImageURLs' : openapi.Schema(type=openapi.TYPE_STRING, description='Custom Detail Image URLs'),
        'CellNo' : openapi.Schema(type=openapi.TYPE_INTEGER, description = 'Where want to insert (-50)'),
        'Max_Num' : openapi.Schema(type=openapi.TYPE_INTEGER, description = 'product\'s max number'),
        'Current_Num' : openapi.Schema(type=openapi.TYPE_INTEGER, description = 'product\'s current number'),
    }
))
@api_view(['POST']) # VM_Product에 POST
def product_add(request):
    flag = True
    if Product.objects.filter(No = request.data['Product_No']).values()[0]['Owner_Username_id'] == 'venduster':
        flag = False

    if VM_Product.objects.filter(VM_No=request.data['VM_No'], CellNo=request.data['CellNo']+50).values('CellNo').exists():
        VM_Product.objects.filter(VM_No=request.data['VM_No'], CellNo=request.data['CellNo']+50).update(VM_No_id = request.data['VM_No'], Product_No_id = request.data['Product_No'], CustomDescription = request.data['Description'],
                                Price = request.data['Price'], DiscountedPrice=request.data['DiscountedPrice'], DueDiscountPrice = request.data['DueDiscountPrice'],
                              CustomImageURL = request.data['CustomImageURL'], CustomDetailImageURLs = request.data['CustomDetailImageURLs'],
                              Max_Num = request.data['Max_Num'], Current_Num = request.data['Current_Num'],
                              IsEmpty = True, CellNo = request.data['CellNo']+50, CellSize = 1, IsPrivate = flag)
    else:
        VM_Product.objects.create(VM_No_id = request.data['VM_No'], Product_No_id = request.data['Product_No'], CustomDescription = request.data['Description'],
                                  Price = request.data['Price'], DiscountedPrice=request.data['DiscountedPrice'], DueDiscountPrice = request.data['DueDiscountPrice'],
                                  CustomImageURL = request.data['CustomImageURL'], CustomDetailImageURLs = request.data['CustomDetailImageURLs'],
                                  Max_Num = request.data['Max_Num'], Current_Num = request.data['Current_Num'],
                                  IsEmpty = True, CellNo = request.data['CellNo']+50, CellSize = 1, IsPrivate = flag)

    VM_Product.objects.filter(VM_No=request.query_params['VM_No']).update(IsChecked=0)

    res = []
    tmp = {}
    tmp['Error'] = 0
    res.append(tmp)
    result = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(result, content_type="text/json-comment-filtered")



@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('VM_No', openapi.IN_QUERY, description="vending_machine's primary key",
                                          type=openapi.TYPE_STRING, required=True)])
@api_view(['GET'])
def promotion_list(request):
    if request.method == 'GET':
        return Response(Video.objects.filter(VM_No=request.query_params['VM_No']).values(), status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema( method='patch', request_body=openapi.Schema(
    type = openapi.TYPE_OBJECT,
    properties={
        'VM_No' : openapi.Schema(type=openapi.TYPE_STRING, description='Vending Machine Number'),
        'StartTime' : openapi.Schema(type=openapi.TYPE_STRING, description = 'VM Start Time in one day'),
        'EndTime' : openapi.Schema(type=openapi.TYPE_STRING, description = 'VM End Time in one day'),
    }
))
@api_view(['PATCH']) #현재 프로모션 리스트를 get && 프로모션 아닌 동영상을 프로모션 상태로 변경!
def nightmode_update(request):
    Vending_Machine.objects.filter(VM_No = request.data['VM_No']).update(StartTime=request.data['StartTime'], EndTime = request.data['EndTime'])
    res = []
    tmp = {}
    tmp['Error'] = 0
    res.append(tmp)
    result = json.dumps(res, cls=DjangoJSONEncoder)
    return HttpResponse(result, content_type="text/json-comment-filtered")

 
@api_view(['GET'])
def all_product_list(request):
    return Response(Product.objects.all().values(), status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='patch', request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                 properties={
                                                                     'ID': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                          description=
                                                                                          'identified username')
                                                                 }, required=['ID']))
@api_view(['PATCH'])
def confirm_account_register(request):
    user = User.objects.get(username=request.data['ID'])
    user.is_active = 1
    user.save()

    token = get_token()
    token_id = token['access']['token']['id']
    container_name = request.data['ID']
    storage_url = 'https://api-storage.cloud.toast.com/v1/'
    con_service = ContainerService(storage_url, token_id)
    con_service.create(container_name)
    con_service.set_read_acl(container_name, True)
    result = {"message": "회원가입이 승인되었습니다.", "result": "Success"}
    return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='patch', request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                 properties={
                                                                    'VM_No': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        description='vending machine\'s serial number'),
                                                                    'VM_Name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        description='vending machine\'s nickname'),
                                                                    'Owner_Username': openapi.Schema(
                                                                        type=openapi.TYPE_STRING,
                                                                        description='vending machine\'s owner username(ID)'),
                                                                    'Supplier_Username': openapi.Schema(
                                                                        type=openapi.TYPE_STRING,
                                                                        description='vending machine\'s suppiler username(ID)'),
                                                                    'GPS': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        description='vending machine\'s Gps'),
                                                                    'Address': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        description='vending machine\'s Address'),
                                                                     'Firmware_Version': openapi.Schema(
                                                                        type=openapi.TYPE_NUMBER,
                                                                        description='vending machine\'s firmware version'),
                                                                     'StartTime': openapi.Schema(
                                                                        type=openapi.TYPE_STRING,
                                                                        description='vending machine\'s firmware version'),
                                                                     'EndTime': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        description='vending machine\'s firmware version')
                                                                 }, required=['VM_No', 'VM_Name', 'Owner_Username',
                                                                              'Supplier_Username', 'GPS', 'Address',
                                                                              'Firmware_Version', 'StartTime',
                                                                              'EndTime']
                                                                 ))
@api_view(['PATCH'])
def confirm_iot_vm_register(request):
    Vending_Machine.objects.filter(VM_No_id=request.data['VM_No']).update(VM_Name=request.data['VM_Name'],
                                                                          Owner_Username_id=request.data[
                                                                              'Owner_Username'],
                                                                          Supplier_Username_id=request.data[
                                                                              'Supplier_Username'],
                                                                          GPS=request.data['GPS'],
                                                                          Firmware_Version=request.data[
                                                                              'Firmware_Version'],
                                                                          IsWorking=1,
                                                                          StartTime=request.data['StartTime'],
                                                                          EndTime=request.data['EndTime'])
    # 자판기를 키오스크 단에서 등록하는 경우
    token = get_token()
    token_id = token['access']['token']['id']
    container_name = request.data['Owner_Username']
    storage_url = 'https://api-storage.cloud.toast.com/v1/'
    con_service = ContainerService(storage_url, token_id)
    con_service.create(container_name)
    con_service.set_read_acl(container_name, True)
    requests.put(con_service._get_url(container_name) + "/%s/VM" % request.data['VM_No'],
                 headers=con_service._get_request_header(), data="Vending Machine folder")
    

    result = {"message": "자판기가 데이터베이스에 성공적으로 등록되었습니다.", "result": "Success"}
    return Response(result, status=status.HTTP_201_CREATED, content_type='application/json')


@swagger_auto_schema(method='patch', manual_parameters=[
    openapi.Parameter('VM_No', openapi.IN_QUERY,
                      type=openapi.TYPE_STRING,
                      description='vm\'s serial number',
                      required=True)
],
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                 properties=
                                                 {
                                                     'VM_Name': openapi.Schema(
                                                         description='vending machine\'s name',
                                                         type=openapi.TYPE_STRING,
                                                         required=['VM_Name'])
                                                 }
                                                 )
                     )
@api_view(['PATCH'])
def vm_name(request):
    if request.method == 'PATCH':
        for datas in request.data:
            if request.data[datas] == "":
                return Response(request.data, status=status.HTTP_412_PRECONDITION_FAILED)

        Vending_Machine.objects.filter(VM_No=request.query_params['VM_No']).update(VM_Name=request.data['VM_Name'])
        result = {"VM_No": request.query_params['VM_No'], "VM_Name": request.data['VM_Name']}

    return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='patch', manual_parameters=[
    openapi.Parameter('VM_No', openapi.IN_QUERY,
                      type=openapi.TYPE_STRING,
                      description='vm\'s serial number',
                      required=True)
],
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                 properties=
                                                 {
                                                     'IsSelling': openapi.Schema(
                                                         description='is vending machine on selling or not',
                                                         type=openapi.TYPE_BOOLEAN,
                                                         required=['IsSelling'])
                                                 }
                                                 )
                     )
@api_view(['PATCH'])
def vm_isselling(request):
    if request.method == 'PATCH':
        for datas in request.data:
            if request.data[datas] == "":
                return Response(request.data, status=status.HTTP_412_PRECONDITION_FAILED)

        Vending_Machine.objects.filter(VM_No=request.query_params['VM_No']).update(IsSelling=request.data['IsSelling'])
        result = {"VM_No": request.query_params['VM_No'], "IsSelling": request.data['IsSelling']}

    return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='patch', manual_parameters=[
    openapi.Parameter('VM_No', openapi.IN_QUERY,
                      type=openapi.TYPE_STRING,
                      description='vm\'s serial number',
                      required=True)
],
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                 properties=
                                                 {
                                                     'Supplier_Username': openapi.Schema(
                                                         description='vending machine\'s supplier username',
                                                         type=openapi.TYPE_STRING,
                                                         required=['Supplier_Username'])
                                                 }
                                                 )
                     )
@api_view(['PATCH'])
def supplier_username(request):
    if request.method == 'PATCH':
        for datas in request.data:
            if request.data[datas] == "":
                return Response(request.data, status=status.HTTP_412_PRECONDITION_FAILED)

        Vending_Machine.objects.filter(VM_No=request.query_params['VM_No']).update(
            Supplier_Username=request.data['Supplier_Username'])
        result = {"VM_No": request.query_params['VM_No'], "Supplier_Username": request.data['Supplier_Username']}

    return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('VM_No', openapi.IN_QUERY,
                                                                        description="vending_machine's primary key",
                                                                        type=openapi.TYPE_STRING, required=True)],
                     responses={202: openapi.Response('vm_product table fields', VM_ProductSerializer)})
@swagger_auto_schema(method='patch', request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                 properties={
                                                                     'VM_No': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                             description='vending machine\'s primary key'),
                                                                     'Current_Num': openapi.Schema(
                                                                         type=openapi.TYPE_INTEGER,
                                                                         description='vending machine\'s product current number'),
                                                                     'CellNo': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                              description='vending machine\'s product located cell number'),
                                                                 }, required=['VM_No', 'Current_Num', 'CellNo'])
                     )
@api_view(['GET', 'PATCH'])
def sync_with_vm_product(request):
    if request.method == 'GET':
        if request.query_params['VM_No'] == "":
            return Response(request.query_params['VM_No'], status=status.HTTP_412_PRECONDITION_FAILED)

        vm_products = VM_Product.objects.filter(VM_No=request.query_params['VM_No']).values()
        for item in vm_products:
            # 0: 변경없음
            if item["IsChecked"] == 0:
                VM_Product.objects.filter(VM_No=request.query_params['VM_No']).update(IsChecked=0)

            # 1: 데이터만 변경
            elif item["IsChecked"] == 1:
                VM_Product.objects.filter(VM_No=request.query_params['VM_No']).update(IsChecked=0)

            # 2: 이미지만 변경
            elif item["IsChecked"] == 2:
                VM_Product.objects.filter(VM_No=request.query_params['VM_No']).update(IsChecked=0)

            # 3: 이미지 비디오 모두 변경
            elif item["IsChecked"] == 3:
                VM_Product.objects.filter(VM_No=request.query_params['VM_No']).update(IsChecked=0)

        return Response(vm_products, status=status.HTTP_202_ACCEPTED, content_type='application/json')
    elif request.method == 'PATCH':
        for datas in request.data:  
            if request.data[datas] == "":
                return Response(request.data, status=status.HTTP_412_PRECONDITION_FAILED)

        if request.data['Current_Num'] <= 0:
            isempty = 1
        else:
            isempty = 0

        VM_Product.objects.filter(VM_No=request.data['VM_No'], CellNo=request.data['CellNo']).update(
            Current_Num=request.data['Current_Num'], IsEmpty=isempty)

        return Response(request.data, status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('VM_No', openapi.IN_QUERY, description="vm no",
                                                                        type=openapi.TYPE_STRING, required=True)])
@api_view((['GET']))
def sync_images_and_videos(request):
    if request.method == 'GET':
        if request.query_params['VM_No'] == "":
            return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)

        vm_product = VM_Product.objects.filter(VM_No=request.query_params['VM_No']).values()
        vm_products = sorted(vm_product.values(), key=lambda k: k['CellNo'])
        result = []
        for vm_product in vm_products:
            tmp_dict = vm_product
            if Video.objects.filter(VM_No=tmp_dict['VM_No_id'], CellNo=tmp_dict['CellNo']).exists():
                video_url = Video.objects.filter(VM_No=tmp_dict['VM_No_id'], CellNo=tmp_dict['CellNo'])[0]
                tmp_dict['Video_URL'] = video_url.Video_URL
            else:
                tmp_dict['Video_URL'] = "null"
            result.append(tmp_dict)

        return Response(result, content_type='application/json')


@swagger_auto_schema(method='patch', request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                 properties={
                                                                     'VM_No': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                             description='vending machine\'s primary key'),
                                                                     'CellNo': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                              description='vending machine\'s cell number'),
                                                                     'PayMethod': openapi.Schema(
                                                                         type=openapi.TYPE_STRING,
                                                                         description='customer payment method')
                                                                 }
                                                                 ))
@api_view(['PATCH'])
def sell_product_onetime(request):
    if request.method == 'PATCH':
        for datas in request.data:
            if request.data[datas] == "":
                return Response(request.data, status=status.HTTP_412_PRECONDITION_FAILED)

        if request.data['CellNo'] < 1 or request.data['CellNo'] > 16:
            return Response({"message": f"{request.data['CellNo']}번칸은 등록할 수 없는 칸입니다.",
                             "result": "Failed"},
                            status=status.HTTP_412_PRECONDITION_FAILED)

        try:
            vending_machine = Vending_Machine.objects.get(VM_No=request.data['VM_No'])
            vm_product = VM_Product.objects.get(VM_No=request.data['VM_No'], CellNo=request.data['CellNo'])
            if vm_product.Current_Num <= 0:
                return Response({"message": f"{request.data['CellNo']}번칸은 현재 재고가 0개 이하입니다. 더이상 판매될 수 없습니다.",
                                "result": "Failed"},
                                status=status.HTTP_412_PRECONDITION_FAILED)
        except VM_Product.DoesNotExist:
            return Response({"message": "해당 자판기의 트레이에 현재 등록된 상품이 없습니다.",
                             "result": "Failed"},
                            status=status.HTTP_412_PRECONDITION_FAILED)
        except Vending_Machine.DoesNotExist:
            return Response({"message": "해당 자판기가 존재하지 않습니다.",
                             "result": "Failed"},
                            status=status.HTTP_412_PRECONDITION_FAILED)

        vm_products = VM_Product.objects.filter(VM_No=request.data['VM_No'], CellNo=request.data['CellNo'])
        vm_products.update(Current_Num=F('Current_Num') - 1)
        maxidx = 0
        if os.environ['DJANGO_SETTINGS_MODULE'] == 'Venduster.settings.local' or os.environ[
            'DJANGO_SETTINGS_MODULE'] == 'Venduster.settings.development':
            for item in Dev_IotSellingData.scan():
                if item.No > maxidx:
                    maxidx = item.No
            iotsellingdata = Dev_IotSellingData(No=maxidx + 1, VM_No=request.data['VM_No'],
                                                Product_No=vm_product.Product_No_id,
                                                Product_Name=vm_product.Product_Name,
                                                Price=vm_product.Price, DiscountedPrice=vm_product.DiscountedPrice,
                                                PayMethod=request.data['PayMethod'],
                                                SoldTime=datetime.datetime.now(), GPS=vending_machine.GPS)
            iotsellingdata.save()
        elif os.environ['DJANGO_SETTINGS_MODULE'] == 'Venduster.settings.production':
            for item in Prod_IotSellingData.scan():
                if item.No > maxidx:
                    maxidx = item.No
            iotsellingdata = Prod_IotSellingData(No=maxidx + 1, VM_No=request.data['VM_No'],
                                                 Product_No=vm_product.Product_No_id,
                                                 Product_Name=vm_product.Product_Name,
                                                 Price=vm_product.Price, DiscountedPrice=vm_product.DiscountedPrice,
                                                 PayMethod=request.data['PayMethod'],
                                                 SoldTime=datetime.datetime.now(), GPS=vending_machine.GPS)
            iotsellingdata.save()

        vm_product = VM_Product.objects.get(VM_No=request.data['VM_No'], CellNo=request.data['CellNo'])
        if vm_product.Current_Num <= 0:
            vm_product.IsEmpty = 0

        return Response(vm_products.values(), status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='patch', request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                 properties={
                                                                     'VM_No': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                             description='vending machine\'s primary key'),
                                                                     'CellNo': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                              description='vending machine\'s cell number')
                                                                 }
                                                                 ))
@api_view(['PATCH'])
def tray_get_in(request):
    if request.method == 'PATCH':
        for datas in request.data:
            if request.data[datas] == "":
                return Response(request.data, status=status.HTTP_412_PRECONDITION_FAILED)

        try:
            current_vm_tray_product = VM_Product.objects.get(VM_No=request.data['VM_No'], CellNo=request.data['CellNo'])
        except VM_Product.DoesNotExist:
            return Response({"message": f"{request.data['CellNo']}번칸의 트레이에 현재 등록된 상품이 존재하지 않습니다",
                             "result": "Failed"})
        '''
        if current_vm_tray_product.Current_Num > 0:
            return Response({"message": f"{request.data['CellNo']}번칸의 상품은 현재 트레이가 제거된 상태가 아닙니다.",
                             "result": "Failed"},
                            status=status.HTTP_412_PRECONDITION_FAILED)
        '''

        # 상품 변경 요청이 QR 테이블에 들어와 있을 경우
        try:
            request_product_change_column = Temporary_Product.objects.get(CellNo=request.data['CellNo'],
                                                                          VM_No=request.data['VM_No'],
                                                                          IsActive=1)
            current_vm_tray_product.Product_Name = request_product_change_column.Product_Name
            current_vm_tray_product.CellNo = request_product_change_column.CellNo
            current_vm_tray_product.Current_Num = request_product_change_column.Current_Num
            current_vm_tray_product.Max_Num = request_product_change_column.Max_Num
            current_vm_tray_product.IsEmpty = request_product_change_column.IsEmpty
            current_vm_tray_product.Price = request_product_change_column.Price
            current_vm_tray_product.DiscountedPrice = request_product_change_column.DiscountedPrice
            current_vm_tray_product.DueDiscountPrice = request_product_change_column.DueDiscountPrice
            current_vm_tray_product.ProductUpdateTime = datetime.datetime.now()
            current_vm_tray_product.CustomDescription = request_product_change_column.CustomDescription
            current_vm_tray_product.CustomHashTag = request_product_change_column.CustomHashTag
            current_vm_tray_product.IsPromotioned = request_product_change_column.IsPromotioned
            current_vm_tray_product.IsChecked = request_product_change_column.IsChecked
            current_vm_tray_product.save()

            request_product_change_column.IsActive = 0
            request_product_change_column.save()

            result = {"message": "상품 변경 요청 트레이 장착이 성공적으로 진행되었습니다.", "result": "Success"}
        except Temporary_Product.DoesNotExist:
            # 트레이 잘못 제거 or 재고 보충후 재 장착일 경우
            try:
                request_product_replace_column = Temporary_Product.objects.get(CellNo=0, VM_No=request.data['VM_No'],
                                                                               IsActive=1)
                current_vm_tray_product.Current_Num = request_product_replace_column.Current_Num
                request_product_replace_column.IsActive = 0
                request_product_replace_column.save()
                current_vm_tray_product.save()
                result = {"message": "제고 보충 트레이 장착이 성공적으로 진행되었습니다.", "result": "Success"}
            except Temporary_Product.DoesNotExist:
                # 트레이를 잘못된 칸에 장착했을 경우이거나 QR 코드를 찍지 않은 상태로 트레이를 장착한 경우
                mismatch_or_no_qr_process_tray = Temporary_Product.objects.get(VM_No=request.data['VM_No'],
                                                                               IsActive=1)
                mismatch_or_no_qr_process_tray.IsActive = 2
                mismatch_or_no_qr_process_tray.save()
                result = {"message": "트레이가 현재 일치하지 않는 칸에 장착되었거나 QR 코드를 찍지 않은 상태로 "
                                     "장착되었습니다.", "result": "Failed"}

    return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='patch', request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                 properties={
                                                                     'VM_No': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                             description='vending machine\'s primary key'),
                                                                     'CellNo': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                              description='vending machine\'s cell number')
                                                                 }
                                                                 ))
@api_view(['PATCH'])
def tray_get_out(request):
    if request.method == 'PATCH':
        for datas in request.data:
            if request.data[datas] == "":
                return Response(request.data, status=status.HTTP_412_PRECONDITION_FAILED)

        current_vm_tray_product = VM_Product.objects.get(VM_No=request.data['VM_No'], CellNo=request.data['CellNo'])
        current_vm_tray_product.Current_Num = 0
        current_vm_tray_product.IsEmpty = 1
        current_vm_tray_product.save()
        result = {"message": "트레이 제거가 성공적으로 진행되었습니다.", "result": "Success"}

        # 트레이를 잘못된 칸에 장착했을 경우이거나 QR 코드를 찍지 않은 상태로 트레이를 장착한 경우에 트레이 제거
        try:
            mismatch_or_no_qr_process_tray = Temporary_Product.objects.get(IsActive=2)
            mismatch_or_no_qr_process_tray.IsActive = 0
            mismatch_or_no_qr_process_tray.save()
        except Temporary_Product.DoesNotExist:
            pass

    return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('Product_No', openapi.IN_QUERY, description="원하는 비디오와 연결된 Product_No",
                      type=openapi.TYPE_STRING, required=True)])
@api_view((['GET']))
def video_list(request):
    
    getVideoNo = Product.objects.filter(Product_No = request.query_params['Product_No']).values('Video_No_id')[0]
    getVideoURL = Video.objects.filter(Video_No = getVideoNo['Video_No_id']).values('Video_URL')[0]['Video_URL']

    return Response({"message": "해당되는 상품의 비디오 URL입니다", "result": getVideoURL}, status=status.HTTP_202_ACCEPTED,
                    content_type='application/json')


@api_view((['POST']))
def testsocket(request):
    return Response(socket_send(0, "Get", "/iot_vm/sync_with_vm_product"), content_type='application/json')


@api_view((['GET']))
def get_toast_api_params(request):
    token = get_token()
    token_id = token['access']['token']['id']

    toast_params_json = {
        "Storage_URL": "https://api-storage.cloud.toast.com/v1/AUTH_2426bc68736b4ca186199174c5d570bc",
        "X_Auth_Token": token_id
    }

    return Response(toast_params_json, content_type='application/json')


@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('VM_No_id', openapi.IN_QUERY,
                                                                        description="VM_Product 상품 검색",
                                                                        type=openapi.TYPE_STRING, required=True)])
@api_view((['GET']))
def products_by_vm_no(request):

    getProductNo = VM_Product.objects.filter(VM_No_id = request.query_params['VM_No_id']).values('Product_No_id')[0]
    print(getProductNo)
    getProductAll = Product.objects.filter(Product_No = getProductNo['Product_No_id']).values()
    print(getProductAll)
    return Response({"message" : "VM_No를 통한 상품 정보 검색", "result":getProductAll}, content_type="application/json")


# vm_product 상품 검색
@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('VM_No_id', openapi.IN_QUERY,
                                                                        description="VM_Product 상품 검색",
                                                                        type=openapi.TYPE_STRING, required=True)])
@api_view((['GET']))
def vm_products_by_vm_no(request):


    getProductAll = VM_Product.objects.filter(VM_No_id = request.query_params['VM_No_id']).values()
    print(getProductAll)
    return Response({"message" : "VM_No를 통한 상품 정보 검색", "result":getProductAll}, content_type="application/json")



@swagger_auto_schema(method='patch', manual_parameters=[openapi.Parameter('ID', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_STRING,
                                                                          description='owner id', required=True),
                                                        openapi.Parameter('VM_No', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_STRING,
                                                                          description='vm\'s serial number',
                                                                          required=True),
                                                        openapi.Parameter('Product_No', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_INTEGER,
                                                                          description='product\'s primary key number',
                                                                          required=True)
                                                        ]
                     )
@swagger_auto_schema(method='delete', manual_parameters=[openapi.Parameter('ID', openapi.IN_QUERY,
                                                                           type=openapi.TYPE_STRING,
                                                                           description='owner id', required=True),
                                                         openapi.Parameter('VM_No', openapi.IN_QUERY,
                                                                           type=openapi.TYPE_STRING,
                                                                           description='vm\'s serial number',
                                                                           required=True),
                                                         openapi.Parameter('Product_No', openapi.IN_QUERY,
                                                                           type=openapi.TYPE_INTEGER,
                                                                           description='product\'s primary key number',
                                                                           required=True)
                                                         ]
                     )
@api_view(['PATCH', 'DELETE'])
def vm_product_image(request):
    if request.method == 'PATCH':
        for datas in request.query_params:
            if request.query_params[datas] == "":
                return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)

        token = get_token()
        token_id = token['access']['token']['id']
        container_name = request.query_params['ID']
        storage_url = 'https://api-storage.cloud.toast.com/v1/'
        object_path = request.query_params['VM_No'] + '/ProductImages/'
        obj_service = ObjectService(storage_url, token_id)

        VM_Product.objects.filter(VM_No_id=request.query_params['VM_No'], Product_No_id=request.query_params
        ['Product_No']).update(
            CustomImageURL=obj_service._get_url(container_name,
                                                object_path + request.query_params['Product_No'] + ".jpg"))


        result = {
            "ImageURL": obj_service._get_url(container_name, object_path + request.query_params['Product_No'] + ".jpg"),
            "message": "업로드가 성공적으로 진행되었습니다.", "result": "Success"}
        return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')
    elif request.method == 'DELETE':
        for datas in request.query_params:
            if request.query_params[datas] == "":
                return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)

        token = get_token()
        token_id = token['access']['token']['id']
        container_name = request.query_params['ID']
        storage_url = 'https://api-storage.cloud.toast.com/v1/'
        object_path = request.query_params['VM_No'] + '/ProductImages/'
        obj_service = ObjectService(storage_url, token_id)
        obj_service.delete(container_name, object_path + request.query_params['Product_No'] + ".jpg")
        VM_Product.objects.filter(VM_No_id=request.query_params['VM_No'], Product_No_id=request.query_params
        ['Product_No']).update(
            CustomImageURL="null")


        result = {"ImageURL": "null",
                  "message": "삭제가 성공적으로 진행되었습니다.", "result": "Success"}
        return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='patch', manual_parameters=[openapi.Parameter('ID', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_STRING,
                                                                          description='owner id', required=True),
                                                        openapi.Parameter('VM_No', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_STRING,
                                                                          description='vm\'s serial number',
                                                                          required=True),
                                                        openapi.Parameter('Product_No', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_INTEGER,
                                                                          description='product\'s primary key number',
                                                                          required=True),
                                                        ]
                     )
@swagger_auto_schema(method='delete', manual_parameters=[openapi.Parameter('ID', openapi.IN_QUERY,
                                                                           type=openapi.TYPE_STRING,
                                                                           description='owner id', required=True),
                                                         openapi.Parameter('VM_No', openapi.IN_QUERY,
                                                                           type=openapi.TYPE_STRING,
                                                                           description='vm\'s serial number',
                                                                           required=True),
                                                         openapi.Parameter('Product_No', openapi.IN_QUERY,
                                                                           type=openapi.TYPE_INTEGER,
                                                                           description='product\'s primary key number',
                                                                           required=True)
                                                         ]
                     )
@api_view(['PATCH', 'DELETE'])
def vm_product_detailimages(request):
    if request.method == 'PATCH':
        for datas in request.query_params:
            if request.query_params[datas] == "":
                return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)

        token = get_token()
        token_id = token['access']['token']['id']
        container_name = request.query_params['ID']
        storage_url = 'https://api-storage.cloud.toast.com/v1/'
        object_path = request.query_params['VM_No'] + '/ProductDetailImages/'
        obj_service = ObjectService(storage_url, token_id)

        detailImageURLs = obj_service._get_url(container_name,
                                               object_path + request.query_params['Product_No'] + ".jpg")

        VM_Product.objects.filter(VM_No_id=request.query_params['VM_No'], Product_No_id=request.query_params
        ['Product_No']).update(
            CustomDetailImageURLs=detailImageURLs)


        if not detailImageURLs:
            result = {"DetailImageURLs": detailImageURLs, "message": "이미지를 선택 해주세요!", "result": "Failed"}
        else:
            result = {"DetailImageURLs": detailImageURLs, "message": "업로드가 성공적으로 진행되었습니다.", "result": "Success"}

        return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')
    elif request.method == 'DELETE':
        for datas in request.query_params:
            if request.query_params[datas] == "":
                return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)

        token = get_token()
        token_id = token['access']['token']['id']
        container_name = request.query_params['ID']
        storage_url = 'https://api-storage.cloud.toast.com/v1/'
        object_path = request.query_params['VM_No'] + '/ProductDetailImages/'
        obj_service = ObjectService(storage_url, token_id)
        obj_service.delete(container_name, object_path + request.query_params['Product_No'] + ".jpg")

        detailImageURLs = "null"

        VM_Product.objects.filter(VM_No_id=request.query_params['VM_No'], Product_No_id=request.query_params
        ['Product_No']).update(
            CustomDetailImageURLs=detailImageURLs)


        if not detailImageURLs:
            result = {"DetailImageURLs": detailImageURLs, "message": "이미지를 선택 해주세요!", "result": "Failed"}
        else:
            result = {"DetailImageURLs": detailImageURLs, "message": "삭제가 성공적으로 진행되었습니다.", "result": "Success"}

        return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='post', manual_parameters=[openapi.Parameter('ID', openapi.IN_QUERY,
                                                                         type=openapi.TYPE_STRING,
                                                                         description='owner id', required=True),
                                                       openapi.Parameter('VM_No', openapi.IN_QUERY,
                                                                         type=openapi.TYPE_STRING,
                                                                         description='vm\'s serial number',
                                                                         required=True),
                                                       openapi.Parameter('CellNo', openapi.IN_QUERY,
                                                                         type=openapi.TYPE_INTEGER,
                                                                         description='product\'s primary key number',
                                                                         required=True),
                                                       openapi.Parameter('Product_Name', openapi.IN_QUERY,
                                                                         type=openapi.TYPE_STRING,
                                                                         description='product\'s name',
                                                                         required=True),
                                                       openapi.Parameter('title', openapi.IN_QUERY,
                                                                         type=openapi.TYPE_STRING,
                                                                         description='video\'s title', required=True),
                                                       ]
                     )
@swagger_auto_schema(method='delete', manual_parameters=[openapi.Parameter('ID', openapi.IN_QUERY,
                                                                           type=openapi.TYPE_STRING,
                                                                           description='owner id', required=True),
                                                         openapi.Parameter('VM_No', openapi.IN_QUERY,
                                                                           type=openapi.TYPE_STRING,
                                                                           description='vm\'s serial number',
                                                                           required=True),
                                                         openapi.Parameter('CellNo', openapi.IN_QUERY,
                                                                           type=openapi.TYPE_INTEGER,
                                                                           description='product\'s primary key number',
                                                                           required=True)
                                                         ]
                     )
@api_view(['POST', 'DELETE'])
def vm_product_promotion_videos(request):
    if request.method == 'POST':
        for datas in request.query_params:
            if request.query_params[datas] == "":
                return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)

        token = get_token()
        token_id = token['access']['token']['id']
        container_name = request.query_params['ID']
        storage_url = 'https://api-storage.cloud.toast.com/v1/'
        object_path = request.query_params['VM_No'] + '/PromotionVideos/'
        obj_service = ObjectService(storage_url, token_id)
        video = Video.objects.last()
        video_no = str(video.Video_No + 1)
        Video.objects.filter(VM_No=request.query_params['VM_No'], CellNo=request.query_params['CellNo']).delete()
        Video(Video_URL=obj_service._get_url(container_name, object_path + video_no + '.mp4'),
              title=request.query_params['title'], VM_No_id=request.query_params['VM_No'],
              CellNo=request.query_params['CellNo'], Product_Name=request.query_params['Product_Name'],
              VideoUpdateTime=datetime.datetime.now(), Video_No=video_no).save()


        return Response(Video.objects.order_by('-Video_No')[:1].values(), status=status.HTTP_202_ACCEPTED,
                        content_type='application/json')
    elif request.method == 'DELETE':
        for datas in request.query_params:
            if request.query_params[datas] == "":
                return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)

        token = get_token()
        token_id = token['access']['token']['id']
        container_name = request.query_params['ID']
        storage_url = 'https://api-storage.cloud.toast.com/v1/'
        object_path = request.query_params['VM_No'] + '/PromotionVideos/'
        obj_service = ObjectService(storage_url, token_id)
        Video.objects.filter(VM_No=request.query_params['VM_No'], CellNo=request.query_params['CellNo']).delete()


        result = {"message": "삭제가 성공적으로 완료되었습니다.", "result": "Success"}

        return Response(result, status=status.HTTP_202_ACCEPTED,
                        content_type='application/json')


@swagger_auto_schema(method='patch', manual_parameters=[openapi.Parameter('ID', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_STRING,
                                                                          description='owner id', required=True),
                                                        openapi.Parameter('VM_No', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_STRING,
                                                                          description='vm\'s serial number',
                                                                          required=True),
                                                        openapi.Parameter('CellNo', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_INTEGER,
                                                                          description='product\'s primary key number',
                                                                          required=True)
                                                        ]
                     )
@api_view(['PATCH'])
def vm_product_thumbnail(request):
    for datas in request.query_params:
        if request.query_params[datas] == "":
            return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)

    token = get_token()
    token_id = token['access']['token']['id']
    container_name = request.query_params['ID']
    storage_url = 'https://api-storage.cloud.toast.com/v1/'
    obj_service = ObjectService(storage_url, token_id)
    object_path = request.query_params['VM_No'] + '/VideosThumbnail/'
    video = Video.objects.get(VM_No=request.query_params['VM_No'], CellNo=request.query_params['CellNo'])
    video_no = str(video.Video_No)
    Video.objects.filter(VM_No=request.query_params['VM_No'], CellNo=
    request.query_params['CellNo']).update(
        thumbnail=obj_service._get_url(container_name, object_path + video_no + ".jpg"))


    result = {"thumbnailURL": obj_service._get_url(container_name, object_path + video_no + ".jpg"),
              "message": "업로드가 성공적으로 진행되었습니다.", "result": "Success"}

    return Response(Video.objects.order_by('-Video_No')[:1].values(), status=status.HTTP_202_ACCEPTED,
                    content_type='application/json')


#VM_No로 VM정보 조회하는 API
@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('VM_No', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_STRING,
                                                                          description='VM_No', required=True)])    
@api_view(['GET'])
def Request_VM_INFO(request):
    if request.method == 'GET':
        for datas in request.query_params:
            if request.query_params[datas] == "":
                return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)
    
    queryset = Vending_Machine.objects.all()
    queryset = queryset.filter(VM_No=request.query_params['VM_No']).values()

    try:
        return Response({"message": "해당하는 VM_No로 검색한 자판기의 정보입니다",
                            "result": queryset})        
    except json.decoder.JSONDecodeError:
        return Response({"message": "해당하는 자판기의 정보가 없습니다",
                           "result": "Failed"})    


#KIOSK ERROR CODE
@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('Error_Code', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_STRING,
                                                                          description='Error_Code', required=True),
                                                        openapi.Parameter('VM_No', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_STRING,
                                                                          description='VM_No', required=True)])  
@api_view(['GET'])
def Request_vm_error_code(request):
    for datas in request.data:
        for datas in request.query_params:
            if request.query_params[datas] == "":
                return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)
    idx = 0
    #dynamo에 저장
    for item in Dev_Error_Code.scan():
        if idx < item.No:
            idx = item.No
    error_code = Dev_Error_Code(No=idx+1, VM_No=request.query_params["VM_No"],  
                    UpdateTime=datetime.datetime.now(), Error_Code=request.query_params["Error_Code"])      
    error_code.save()    
    list_error_code = list(request.query_params["Error_Code"])
    first_letter = list_error_code[0]
    last_letter = list_error_code[-1]
    result = ""
    KST = timezone('Asia/Seoul')    

    if first_letter == "E":
        if re.match("[A-H]",last_letter):
            current_cellNo = ord(last_letter)-64
            VM_Product.objects.filter(VM_No=request.query_params['VM_No'], CellNo=current_cellNo).update(IsEmpty=1, Current_Num=0)
            result = str(current_cellNo) +"번 트레이가 Sold Out 되었습니다"
            ##dynamo 학생데이터 쌓는거 취소
            idx = datetime.datetime(2019,10,3,12,0,0,tzinfo=KST)
            select = None
            for item in Dev_StudentData.scan():  
                if idx < item.SoldTime:
                    idx = item.SoldTime
                    select = item
            print(idx)
            print(select.No)
            if select is not None:
                select.delete()
        else:
            result = "No problem"

    elif first_letter == "O":
        if list_error_code[1] == "N":
            if re.match("[A-H]",last_letter):
                current_cellNo = ord(last_letter)-64
                VM_Product.objects.filter(VM_No=request.query_params['VM_No'], CellNo=current_cellNo).update(IsEmpty=1, Current_Num=0)
                result = str(current_cellNo) +"번 트레이가 Sold Out 되었습니다"
                ##dynamo 학생데이터 쌓는거 취소
            else:
                result = "No problem"
        elif list_error_code[1] == "C":
            result = "No problem"
         
    elif first_letter == "P":
        if last_letter == "F":
            VM_Product.objects.filter(VM_No=request.query_params['VM_No']).update(IsEmpty=1, Current_Num=0)
            result = "전체 트레이가 Sold Out 되었습니다"
            ##dynamo 학생데이터 쌓는거 취소
            idx = datetime.datetime(2019,10,3,12,0,0,tzinfo=KST)
            select = None
            for item in Dev_StudentData.scan():  
                if idx < item.SoldTime:
                    idx = item.SoldTime
                    select = item
            if select is not None:
                select.delete()
            
        else:
            result = "No problem"

    elif first_letter == "C":
        result = "No problem"

    elif first_letter == "T" and list_error_code[1] == "E" and list_error_code[2] == "S" and last_letter == "T":
        VM_Product.objects.filter(VM_No=request.query_params['VM_No']).update(IsEmpty=0, Current_Num=36, Max_Num=36)
        result = "전체 트레이가 다시 보충 되었습니다"
        

    
    #EA ~ EH || ONA ~ ONH -> IsEmpty = True
    #결과출력
    result = {"message": "에러코드가 전송되었습니다", "result": result}
    return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')


##TEST 리뷰 
@swagger_auto_schema( method='post', request_body=openapi.Schema(
    type = openapi.TYPE_OBJECT,
    properties={
        'id' : openapi.Schema(type =openapi.TYPE_STRING, description = 'id'),
        'replies' : openapi.Schema(type =openapi.TYPE_INTEGER, description='replies'),   
    }
))
@api_view(['POST'])
def request_Review_Information(request):
    for datas in request.data:
        if request.data[datas] == "":
            return Response(request.data, status=status.HTTP_412_PRECONDITION_FAILED)
    KST = timezone('Asia/Seoul')    
    idx = 0
    today = datetime.datetime.now()
    today = today.replace(tzinfo=KST) 
    ##한국시간으로 12월1일 오전0시0분0초
    deadline = datetime.datetime(2019, 12, 1, 0, 0, 0, tzinfo=KST)

    #리뷰 데이터 다이나모에 삽입
    for item in Test_Review_Information.scan():
        if item.No > idx:
            idx = item.No     

    reviewData = Test_Review_Information (No=idx+1, Id=request.data["id"],  
                    UpdateTime=datetime.datetime.now(), Replies=request.data["replies"])      
    reviewData.save()

    #결과출력
    result = {"message": "리뷰정보가 성공적으로 삽입되었습니다.", "result": "Success"}
    return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')


@swagger_auto_schema(method='get')

#리뷰 데이터 검색
@api_view(['GET'])
def get_Review_Data(request):
    KST = timezone('Asia/Seoul')    
    idx = datetime.datetime(2019,10,3,12,0,0,tzinfo=KST)
    result = []
    
    for item in Test_Review_Information.scan():  
        queryset = [item.No, item.Id, item.Replies, item.UpdateTime]
        result.append(queryset) 

    print(result)
    result = {"message": "리뷰 전체 정보 조회하기", "result" : result}
    return Response(result, status=status.HTTP_202_ACCEPTED, content_type='application/json')

#TEST 전체 자판기 데이터
@swagger_auto_schema(method='get')    
@api_view(['GET'])
def Request_VM_ALL_INFO(request):
    queryset = Vending_Machine.objects.values()
    try:
        return Response({"message": "모든 자판기의 정보입니다",
                            "result": queryset})        
    except json.decoder.JSONDecodeError:
        return Response({"message": "자판기의 정보가 없습니다",
                           "result": "Failed"})    


@swagger_auto_schema(method='patch', request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                 properties={
                                                                'Product_No': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='검색을 위한 상품 식별 번호'),
                                                                'Product_Name': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='상품 이름'),
                                                                'ImageURL': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='상품 이미지 URL'),
                                                                'DetailImage': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='상품 상세 이미지 URL'),
                                                                'Size': openapi.Schema(
                                                                    type=openapi.TYPE_INTEGER,
                                                                    description='상품 크기 변경'),
                                                                'Width_Spring': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                    description='상품의 스프링 규격 변경'),
                                                                'IsRecommand': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                    description='추천 상품 여부 변경'),
                                                                'Price': openapi.Schema(
                                                                    type=openapi.TYPE_INTEGER,
                                                                    description='가격 변경'),
                                                                'IsPublic': openapi.Schema(
                                                                    type=openapi.TYPE_INTEGER,
                                                                    description='Public 상품인지 여부'),
                                                                'Company_Name': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='상품 제조 회사 정보 변경'),
                                                                'Owner_Username_id': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='상품 소유주 변경'),
                                                                'Video_No_id': openapi.Schema(
                                                                    type=openapi.TYPE_INTEGER,
                                                                    description='상품 홍보 동영상 변경'),
                                                                    
                                                                 }, required=['Product_Name', 'ImageURL', 'DetailImage',
                                                                              'Size', 'Width_Spring', 'IsRecommand',
                                                                              'Price', 'IsPublic', 'Company_Name', 'Owner_Username_id'
                                                                              'Video_No_id']
                                                                 ))
@api_view(['PATCH'])
def update_product(request):
    

    if not Product.objects.filter(Product_No =request.data['Product_No']):
        print("없으면")
        return Response({"message": "Product_No에 해당하는 상품이 존재하지 않습니다.", "result": "NotExist"})       
       
    else:
        print("있으면")   
        Product.objects.filter(Product_No = request.data['Product_No']).update(Product_Name = request.data['Product_Name'], ImageURL = request.data['ImageURL'],
                                            DetailImage = request.data['DetailImage'], Size = request.data['Size'], Width_Spring = request.data['Width_Spring'],
                                            IsRecommand = request.data['IsRecommand'], Price = request.data['Price'], IsPublic = request.data['IsPublic'],
                                            Company_Name = request.data['Company_Name'], Video_No_id = request.data['Video_No_id'])

    result = {"message": "자판기가 성공적으로 업데이트 되었습니다.", "result": "Success"}
    return Response(result, status=status.HTTP_201_CREATED, content_type='application/json')

@swagger_auto_schema(method='post', request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                 properties={
                                                                'VM_No': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='자판기 시리얼 번호'),
                                                                'VM_Name': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='자판기 모델 이름'),
                                                                'Owner_Username': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='자판기 소유주'),
                                                                'Supplier_Username': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='자판기 유통업자'),
                                                                'Longitude': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    description='자판기 위치 위도'),
                                                                'Latitude': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    description='자판기 위치 경도'),
                                                                'Address': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    description='자판기 위치 도로명 주소'),
                                                                'CityName': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    description='특별시, 광역시, 도'),
                                                                'Firmware_Version': openapi.Schema(
                                                                    type=openapi.TYPE_NUMBER,
                                                                    description='펌웨어 버전'),
                                                                'StartTime': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='자판기 운용 시작 시간'),
                                                                'EndTime': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='자판기 운용 마감 시간')
                                                                    
                                                                 }, required=['VM_No', 'VM_Name', 'Owner_Username',
                                                                              'Supplier_Username',  'Address', 'CityName'
                                                                              'Firmware_Version', 'StartTime',
                                                                              'EndTime', 'Latitude']
                                                                 ))
@api_view(['POST'])
def create_vending_machine(request):
    # 직접 자판기 등록
    num = 1
    for info in Vending_Machine.objects.values():
        print(info)

        if info['No'] >= num:
            num = info['No']


    get_Owner_Username = User.objects.get(username = request.data['Owner_Username'])
    get_Supplier_username = User.objects.get(username = request.data['Supplier_Username'])
    print(num)
    Vending_Machine.objects.create(No = num+1, VM_No = request.data['VM_No'], VM_Name = request.data['VM_Name'], Address = request.data['Address'], CityName = request.data['CityName'],
                            Longitude = request.data['Longitude'], Latitude = request.data['Latitude'], Firmware_Version = request.data['Firmware_Version'], IsSelling = 1, IsWorking = 1, VM_IsEmpty=1,
                            StartTime = request.data['StartTime'], EndTime = request.data['EndTime'], UpdateTime = datetime.datetime.now(),
                            Owner_Username = get_Owner_Username, Supplier_Username = get_Supplier_username)

    result = {"message": "자판기가 데이터베이스에 성공적으로 등록되었습니다.", "result": "Success"}
    return Response(result, status=status.HTTP_201_CREATED, content_type='application/json')


#상품 삭제 처리
#vm_no 받아와서 처리
@swagger_auto_schema(method='delete', manual_parameters=[openapi.Parameter('Product_No', openapi.IN_QUERY,
                                                                           type=openapi.TYPE_STRING,
                                                                           description='삭제할 상품 No', required=True)
                                                         ]
                     )
@api_view(['DELETE'])
def remove_Product(request):
    
    if request.method == 'DELETE':
        for datas in request.query_params:
            if request.query_params[datas] == "":
                return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)

        #queryset.delete() ==> 삭제 처리방식
        
        Product.objects.filter(Product_No=request.query_params['Product_No']).delete()

    return Response({"message:":"상품 삭제가 성공적으로 진행되었습니다"}, status=status.HTTP_202_ACCEPTED, content_type='application/json')

@swagger_auto_schema(method='post', request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                 properties={
                                                                'Product_No': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='상품 정보'),
                                                                'ImageURL': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='이미지 URL'),
                                                                'DetailImage': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='상세보기 '),
                                                                'Max_Num': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='최대 수량'),
                                                                'Size': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    description='트레이 차지 하는 크기'),
                                                                'Width_Spring': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    description='스프링 간격'),
                                                                'Price': openapi.Schema(type=openapi.TYPE_STRING,
                                                                    description='상품 가격'),
                                                                'Company_Name': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='상품 제조사'),
                                                                'Owner_Username_id': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='자판기 소유주'),
                                                                'Video_No_id': openapi.Schema(
                                                                    type=openapi.TYPE_STRING,
                                                                    description='광고영상 식별값')
                                                                    
                                                                 }, required=['Product_No', 'ImageURL', 'DetailImage',
                                                                              'Max_Num', 'Size', 'Width_Spring',
                                                                              'Price', 'Company_Name','Owner_Username_id',
                                                                              'Video_No_id']
                                                                 ))
@api_view(['POST'])
def create_product(request):
    
    #상품등록
    num = 1
    for info in Product.objects.values():
        if info['No'] == num:
            flag = True
            break
        num += 1

    #비디오 가져오는 절차

    queryset = Product.objects.create(Product_No=request.data['Product_No'], ImageURL=request.data['ImageURL'],
                                    DetailImage=request.data['DetailImage'], Max_Num=request.data['Max_Num'],
                                    Size=request.data['Size'], Width_Spring=request.data['Width_Spring'],
                                    Price=request.data['Price'],Company_Name=request.data['Company_Name'],
                                    Owner_Username_id=request.data['Owner_Username_id'],Video_No_id=request.data['Video_No_id'])

    result = {"message": "Product가 성공적으로 등록되었습니다.", "result": "Success"}
    return Response(result, status=status.HTTP_201_CREATED, content_type='application/json')


# 자판기 지역별 보유량
@swagger_auto_schema(method='get', manual_parameters=[openapi.Parameter('VM_No', openapi.IN_QUERY,
                                                                          type=openapi.TYPE_STRING,
                                                                          description='VM_No', required=True)])    
@api_view(['GET'])
def Request_VM_INFO(request):
    if request.method == 'GET':
        for datas in request.query_params:
            if request.query_params[datas] == "":
                return Response(request.query_params, status=status.HTTP_412_PRECONDITION_FAILED)
    
    queryset = Vending_Machine.objects.all()
    queryset = queryset.filter(VM_No=request.query_params['VM_No']).values()

    try:
        return Response({"message": "해당하는 VM_No로 검색한 자판기의 정보입니다",
                            "result": queryset})        
    except json.decoder.JSONDecodeError:
        return Response({"message": "해당하는 자판기의 정보가 없습니다",
                           "result": "Failed"})    