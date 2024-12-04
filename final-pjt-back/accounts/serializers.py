from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import User
from finlife.models import DepositProducts
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    profile_image = serializers.ImageField(use_url=True, required=False, allow_null=True)
    subscribed_products = serializers.SlugRelatedField(
        slug_field='fin_prdt_cd',  # fin_prdt_cd를 slug 필드로 사용
        queryset=DepositProducts.objects.all(),
        many=True,
        required=False
    )
    birth = serializers.DateField(required=True)
    phone = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    income = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    job = serializers.CharField(required=False)
    main_bank = serializers.CharField(required=False)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update({
            'phone': self.validated_data.get('phone', ''),
            'birth': self.validated_data.get('birth', ''),
            'income': self.validated_data.get('income', None),
            'job': self.validated_data.get('job', ''),
            'main_bank': self.validated_data.get('main_bank', ''),
            'profile_image': self.validated_data.get('profile_image', None),
            'subscribed_products': self.validated_data.get('subscribed_products', []),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
        })
        return data

    def save(self, request):
        user_data = self.get_cleaned_data()
        
        # 사용자 생성 시 모든 필수 필드를 함께 전달
        user = UserModel.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password1'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            birth=user_data['birth'],
            income=user_data.get('income', None),
            job=user_data.get('job', ''),
            main_bank=user_data.get('main_bank', ''),
        )
        
        # 프로필 이미지가 제공된 경우 설정
        profile_image = user_data.get('profile_image', None)
        if profile_image:
            user.profile_image = profile_image
            user.save()

        # 가입한 상품 설정
        subscribed_products = user_data.get('subscribed_products', [])
        if subscribed_products:
            user.subscribed_products.set(subscribed_products)

        return user

class CustomUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = [
            'pk',
            UserModel.USERNAME_FIELD,
            UserModel.EMAIL_FIELD,
            'first_name',
            'last_name',
            'profile_image',
            'phone',
            'birth',
            'income',
            'job',
            'main_bank',
            'subscribed_products',
            'is_active',
            'is_staff',
            'last_login'
        ]


class SubscribedProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fin_prdt_nm = serializers.CharField()
    fin_prdt_cd = serializers.CharField()

class UserProfileSerializer(serializers.ModelSerializer):
    subscribed_products = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = '__all__'
        read_only_fields = ('username', 'email')

    def get_subscribed_products(self, obj):
        products = obj.subscribed_products.all()
        serializer = SubscribedProductSerializer(products, many=True)
        return serializer.data