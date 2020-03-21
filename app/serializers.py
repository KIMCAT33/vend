from app.models import Product, VM_Product, Vending_Machine, Account, Video, Notice
from rest_framework import serializers


class ProductSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class VM_ProductSerializer(serializers.HyperlinkedModelSerializer):
    No = serializers.PrimaryKeyRelatedField(read_only='True')

    class Meta:
        model = VM_Product
        fields = '__all__'


class Vending_MachineSerializer(serializers.HyperlinkedModelSerializer):
    Model_Num = serializers.PrimaryKeyRelatedField(read_only='True')

    class Meta:
        model = Vending_Machine
        fields = '__all__'


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class VideoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class NoticeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
