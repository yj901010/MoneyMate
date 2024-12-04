
from rest_framework import serializers
from .models import DepositProducts, DepositOptions,Change

class DepositProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model=DepositProducts
        fields='__all__'
    class OptionListSerializer(serializers.ModelSerializer):
        class Meta:
            model=DepositOptions
            fields='__all__'
    options=OptionListSerializer(many=True, read_only=True)
    

class DepositOptionsSerializer(serializers.ModelSerializer):
    # class ProductSerializer(serializers.ModelSerializer):
    #     class Meta:
    #         model=DepositProducts
    #         fields='__all__'
    # product=ProductSerializer(read_only=True)
    class Meta:
        model=DepositOptions
        fields='__all__'
        # fields=('product', 'intr_rate_type_nm',"intr_rate","intr_rate2", "save_trm",)
       

class ChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Change
        fields='__all__'