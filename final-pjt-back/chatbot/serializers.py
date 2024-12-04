from rest_framework import serializers
from .models import InvestmentStyleType, UserInvestmentStyle, Portfolio, PortfolioItem

class InvestmentStyleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentStyleType
        fields = '__all__'

class UserInvestmentStyleSerializer(serializers.ModelSerializer):
    style = InvestmentStyleTypeSerializer()  # Nested serialization

    class Meta:
        model = UserInvestmentStyle
        fields = '__all__'

class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = ['item_type', 'name', 'ratio', 'order']

class PortfolioSerializer(serializers.ModelSerializer):
    types = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    ratios = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Portfolio
        fields = ['id', 'created_at', 'types', 'products', 'ratios']

    def get_types(self, obj):
        return PortfolioItemSerializer(
            obj.items.filter(item_type='TYPE').order_by('order'),
            many=True
        ).data

    def get_products(self, obj):
        return PortfolioItemSerializer(
            obj.items.filter(item_type='PRODUCT').order_by('order'),
            many=True
        ).data

    def get_ratios(self, obj):
        return PortfolioItemSerializer(
            obj.items.filter(item_type='RATIO').order_by('order'),
            many=True
        ).data