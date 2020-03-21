"""api URL Configuration

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

import rest_framework.authtoken.views

from django.conf import settings
from django.contrib import admin
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.urls import path
from rest_framework import routers, permissions, authentication
from app import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

app_name = 'ansana'

router = routers.DefaultRouter()
# router.register(r'UserModel', views.usermodel_list)
# router.register(r'PromotionVideo', views.promotionvideo_list)


schema_patterns = [
    url(r'^api/', include((router.urls, app_name), namespace='ansana')),
    path('api/register/confirm_account[회의필요]', views.confirm_account_register),
    path('api/register/confirm_iot_vm[회의필요]', views.confirm_iot_vm_register),
    path('api/product-management/products/all', views.all_product_list),
    path('api/product-management/products/vms', views.products_by_vm_no),
    path('api/vm-management/vms/vm-no', views.vminfo_by_vm_no),
    path('api/user-management/users/signup', views.signup),
    path('api/user-management/users/login', views.app_login),
    path('api/sales-management/sales/users[회의필요]', views.totalsales_by_user),
    path('api/user-management/users/profile', views.get_profile),  #에러있음
    path('api/vm-management/vms/users', views.vmlist_by_id),
    path('api/vm-management/vms/vm-names', views.vm_name),
    path('api/vm-management/vms/isselling', views.vm_isselling),
    path('api/user-management/users/supplier', views.supplier_username),
    path('api/notice', views.notice),
    path('api/sales-management/sales/vms[회의필요]', views.sales_by_vm_no),
    path('api/vm-product-management/vm-products/products', views.create_new_product_to_vm_product),
    path('api/admin_app/promotion_list[회의필요]', views.promotion_list),
    path('api/vm-management/nightmode', views.nightmode_update),
    path('api/admin_app/get_toast_api_params[회의필요]', views.get_toast_api_params),
    path('api/vm-product-management/vm-products/image', views.vm_product_image),
    path('api/vm-product-management/vm_products/detailimages', views.vm_product_detailimages),
    path('api/video-management/videos/vm-products', views.vm_product_promotion_videos),
    path('api/vm-product-management/thumbnail[토스트에 썸네일 업로드하는 API로 회의필요]', views.vm_product_thumbnail),
    path('api/video-management/videos', views.video_list),
    path('api/vm-management/vms/vm-no', views.Request_VM_INFO),
    path('api/vm-management/vms', views.create_vending_machine),
    path('api/iot_vm/sync_with_vm_product[회의필요]', views.sync_with_vm_product),
    path('api/iot_vm/sell_product_onetime[회의필요]', views.sell_product_onetime),
    path('api/iot_vm/sync_images_and_videos[회의필요]', views.sync_images_and_videos),
    path('api/vm-management/error-code', views.Request_vm_error_code),
    path('api/TEST/request_Review_Information[회의필요]', views.request_Review_Information),
    path('api/TEST/get_Review_Data[회의필요]', views.get_Review_Data),
    path('api/vm-management/vms/all', views.Request_VM_ALL_INFO),
    path('api/product-management/products/update', views.update_product),
    path('api/product-management/products/delete', views.remove_Product),
    path('api/product-management/products/create', views.create_product),
    path('api/vm-product-management/products/delete', views.remove_product_from_vm_product),
    path('api/vm-product-management/products/update', views.update_product_from_vm_product),
    path('api/vm-product-management/vms/vm-no',views.vm_products_by_vm_no)
]

schema_view = get_schema_view(
    openapi.Info(
        title="Ansana API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=schema_patterns,
)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api/endpoint(?P<format>\.json|\.yaml)/$', schema_view.with_ui(cache_timeout=0), name='schema-json'),
    url(r'^api/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^api/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    url(r'^admin/', admin.site.urls),
    url(r'^api-token-auth/', rest_framework.authtoken.views.obtain_auth_token),
    url(r'^api/accounts/signup$', views.CreateUserView.as_view(), name='signup'),
    url(r'^api/accounts/login/$', auth_views.LoginView.as_view(template_name="registration/login.html"),
        {'template_name': 'registration/login.html'}, name='login'),
    url(r'^api/accounts/login/done$', views.RegisteredView.as_view(), name='create_user_done'),
    url(r'^api/accounts/logout/$', auth_views.LogoutView.as_view(template_name="registration/logout.html"),
        {'template_name': 'registration/logout.html'}, name='logout'),
    path('api/register/confirm_account', views.confirm_account_register),
    path('api/register/confirm_iot_vm', views.confirm_iot_vm_register),
    path('api/product-management/products/all', views.all_product_list),
    path('api/product-management/products/vms', views.products_by_vm_no),
    path('api/vm-management/vms/vm-no', views.vminfo_by_vm_no),
    path('api/user-management/users/signup', views.signup),
    path('api/user-management/users/login', views.app_login),
    path('api/sales-management/sales/users', views.totalsales_by_user),
    path('api/user-management/users/profile', views.get_profile),  #에러있음
    path('api/vm-management/vms/users', views.vmlist_by_id),
    path('api/vm-management/vms/vm-names', views.vm_name),
    path('api/vm-management/vms/isselling', views.vm_isselling),
    path('api/user-management/users/supplier', views.supplier_username),
    path('api/notice', views.notice),
    path('api/sales-management/sales/vms', views.sales_by_vm_no),
    path('api/vm-product-management/vm-products/products', views.create_new_product_to_vm_product),
    path('api/admin_app/promotion_list', views.promotion_list),
    path('api/vm-management/nightmode', views.nightmode_update),
    path('api/admin_app/get_toast_api_params', views.get_toast_api_params),
    path('api/vm-product-management/vm-products/image', views.vm_product_image),
    path('api/vm-product-management/vm_products/detailimages', views.vm_product_detailimages),
    path('api/video-management/videos/vm-products', views.vm_product_promotion_videos),
    path('api/vm-product-management/thumbnail[토스트에 썸네일 업로드하는 API로 회의필요]', views.vm_product_thumbnail),
    path('api/video-management/videos', views.video_list),
    path('api/vm-management/vms/vm-no', views.Request_VM_INFO),
    path('api/vm-management/vms', views.create_vending_machine),
    path('api/iot_vm/sync_with_vm_product', views.sync_with_vm_product),
    path('api/iot_vm/sell_product_onetime', views.sell_product_onetime),
    path('api/iot_vm/sync_images_and_videos', views.sync_images_and_videos),
    path('api/vm-management/error-code', views.Request_vm_error_code),
    path('api/TEST/request_Review_Information', views.request_Review_Information),
    path('api/TEST/get_Review_Data', views.get_Review_Data),
    path('api/vm-management/vms/all', views.Request_VM_ALL_INFO),
    path('api/product-management/products/update', views.update_product),
    path('api/product-management/products/delete', views.remove_Product),
    path('api/product-management/products/create', views.create_product),
    path('api/vm-product-management/products/delete', views.remove_product_from_vm_product),
    path('api/vm-product-management/products/update', views.update_product_from_vm_product),
    path('api/vm-product-management/vms/vm-no',views.vm_products_by_vm_no)



]
'''
if settings.DEBUG:
    urlpatterns = [

    ] + urlpatterns
'''