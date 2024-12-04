from django.shortcuts import render
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.db.models.signals import post_save
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import User, DepositProducts
from .serializers import UserProfileSerializer, CustomUserDetailsSerializer
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

def check_username(request):
    try:
        username = request.GET.get('username')
        User = get_user_model()
        if username is None:
            return JsonResponse({'error': 'Username is required'}, status=400)

        # 사용자 이름이 이미 존재하는지 체크
        if User.objects.filter(username=username).exists():
            return JsonResponse({'isAvailable': False})
        return JsonResponse({'isAvailable': True})
    except Exception as e:
        # 예외가 발생하면 로깅하고 500 에러를 반환
        print(f"Error in check_username view: {str(e)}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)
    
@api_view(['POST'])
def find_id(request):
    email = request.POST.get('email', '').strip()
    response = {'User_Id': '이메일을 다시 확인하세요'}

    if not email:
        return Response({'User_Id': '이메일을 입력해주세요'}, status=400)

    try:
        user = User.objects.get(email=email)
        response['User_Id'] = user.username
    except User.DoesNotExist:
        response['User_Id'] = '이메일을 다시 확인하세요'

    return Response(response)
    
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user

    if request.method == 'GET':
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserProfileSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_user_profile(request):
    user = request.user  # 현재 요청한 사용자 가져오기

    # 수정 가능한 필드만 추출
    editable_fields = ['profile_image', 'email', 'income', 'job', 'phone', 'main_bank']
    update_data = {field: request.data.get(field) for field in editable_fields if field in request.data}
    print('update_data',update_data)
    print('user',user)
    
    # 부분 업데이트
    serializer = CustomUserDetailsSerializer(user, data=update_data, partial=True)

    if serializer.is_valid():
        try:
            serializer.save()
            return Response({
                "message": "프로필이 성공적으로 업데이트되었습니다.",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "error": "프로필 업데이트 중 오류가 발생했습니다.",
                "details": str(e),
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            "error": "유효성 검증 실패",
            "details": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_to_account(request):
    print(f"User: {request.user}")  # 사용자 확인
    print(f"Headers: {request.headers}")  # 요청 헤더 출력

    if not request.user.is_authenticated:
        return Response({"error": "인증되지 않은 사용자입니다."}, status=status.HTTP_401_UNAUTHORIZED)

    product_id = request.data.get('product_id')
    if not product_id:
        return Response({"error": "상품 ID가 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = DepositProducts.objects.get(fin_prdt_cd=product_id)
        request.user.subscribed_products.add(product)
        return Response({"message": f"상품 '{product.fin_prdt_nm}'이(가) 추가되었습니다."}, status=status.HTTP_200_OK)
    except DepositProducts.DoesNotExist:
        return Response({"error": "해당 상품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_product_from_account(request):
    if not request.user.is_authenticated:
        return Response({"error": "인증되지 않은 사용자입니다."}, status=status.HTTP_401_UNAUTHORIZED)

    product_id = request.data.get('product_id')
    if not product_id:
        return Response({"error": "상품 ID가 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = DepositProducts.objects.get(fin_prdt_cd=product_id)
        request.user.subscribed_products.remove(product)
        return Response({"message": f"상품 '{product.fin_prdt_nm}'이(가) 해지되었습니다."}, status=status.HTTP_200_OK)
    except DepositProducts.DoesNotExist:
        return Response({"error": "해당 상품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@ensure_csrf_cookie
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrftoken': csrf_token})

