from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from openai import OpenAI
import logging
from openai import AuthenticationError, RateLimitError, OpenAIError
from .models import InvestmentStyleType, UserInvestmentStyle, Portfolio, PortfolioItem
from .serializers import InvestmentStyleTypeSerializer, UserInvestmentStyleSerializer, PortfolioSerializer

# 로깅 설정
logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.CHATBOT_API_KEY)


@api_view(['POST'])
def chat(request):
    if request.method == "POST":
        try:
            # 요청 데이터 가져오기
            data = request.data
            user_message = data.get("message", "").strip()
            messages = data.get("messages", [])

            if not user_message:
                return JsonResponse({"error": "메시지가 비어 있습니다."}, status=400)
            if not isinstance(messages, list):
                return JsonResponse({"error": "'messages'는 리스트여야 합니다."}, status=400)

            # 사용자 메시지를 추가
            messages.append({"role": "user", "content": user_message})

            completion = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages
            )

            assistant_content = completion.choices[0].message.content.strip()
            messages.append({"role": "assistant", "content": assistant_content})

            return JsonResponse({"response": assistant_content, "messages": messages})

        
        except AuthenticationError:
            # 인증 실패 처리
            logger.error("OpenAI 인증 실패: API 키를 확인하세요.")
            return JsonResponse({"error": "OpenAI 인증 실패. API 키를 확인하세요."}, status=401)
        except OpenAIError as e:
            # 기타 OpenAI API 에러 처리
            logger.error(f"OpenAI API 에러 발생: {str(e)}")
            return JsonResponse({"error": f"OpenAI API 에러: {str(e)}"}, status=500)
        except RateLimitError:
            # 쿼터 초과 에러 처리
            logger.error("OpenAI API 요청 제한 초과.")
            return JsonResponse(
                {"error": "OpenAI API 요청 한도를 초과했습니다. 플랜을 확인하거나 결제 정보를 업데이트하세요."},
                status=429
            )
        except Exception as e:
            # 서버 내부 에러 처리
            logger.error(f"서버 에러 발생: {str(e)}")
            return JsonResponse({"error": f"서버 에러: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

# @permission_classes([IsAuthenticated])
@api_view(['GET'])
def make_portfolio(request):
    try:
        # 사용자 확인
        if not request.user.is_authenticated:
            return JsonResponse({"error": "로그인이 필요합니다."}, status=401)

        # 사용자의 투자 성향 가져오기
        try:
            user_style = UserInvestmentStyle.objects.get(user=request.user)
            type_of = user_style.style.type_of
        except UserInvestmentStyle.DoesNotExist:
            return JsonResponse({"error": "투자 성향 정보가 필요합니다."}, status=400)

        # 사용자의 income 정보 확인
        if not request.user.income:
            return JsonResponse({"error": "소득 정보가 필요합니다."}, status=400)
        
        # 연소득을 만원 단위로 변환
        income = int(request.user.income)

        messages = [
            {
                "role": "user",
                "content": (
                    f"투자 성향이 '{type_of}'이야. "
                    f"연수입은 {income}만원이고, "
                    "이럴 때 너가 추천해줄만한 투자 종류가 있을까? "
                    "그리고 그 상품 중에서 수익이 좋은 상품들을 5가지 정도 추천해줄래? "
                    "또한 투자 비율을 알려줘. 대신 범위를 설정하지 말고 명확히 알려줘야 해."
                    "대답 형식은"
                    "투자 종류"
                    "(넘버링 하여 하나씩 나열)"
                    "수익 좋은 상품 5가지"
                    "(넘버링 하여 하나씩 나열)"
                    "투자 비율"
                    "(투자 종류 이름): ~%"
                    "이런식으로 해볼래?"
                )
            }
        ]
        
        # OpenAI API 호출
        completion = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages
        )

        assistant_content = completion.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": assistant_content})

        # 기존 포트폴리오 삭제
        Portfolio.objects.filter(user=request.user).delete()

        # 새 포트폴리오 생성
        portfolio = Portfolio.objects.create(
            user=request.user,
            investment_style=user_style
        )

        # 응답 파싱 및 PortfolioItem 생성
        content_lines = assistant_content.split('\n')
        current_section = None
        order = 0

        for line in content_lines:
            line = line.strip()
            
            # 섹션 식별 (### 또는 ** 또는 일반 텍스트로 시작하는 섹션 헤더 처리)
            if '### 투자 종류' in line or '**투자 종류**' in line or '투자 종류:' in line:
                current_section = 'TYPE'
                order = 0
                continue
            elif '### 수익' in line or '**수익 좋은 상품' in line or '수익 좋은 상품:' in line:
                current_section = 'PRODUCT'
                order = 0
                continue
            elif '### 투자 비율' in line or '**투자 비율**' in line or '투자 비율:' in line:
                current_section = 'RATIO'
                order = 0
                continue

            # 항목 저장
            try:
                if current_section == 'TYPE' and line.strip() and line[0].isdigit():
                    name = line.split('.')[1].strip()
                    if name:  # 빈 문자열이 아닌 경우에만 저장
                        PortfolioItem.objects.create(
                            portfolio=portfolio,
                            item_type='TYPE',
                            name=name,
                            order=order
                        )
                        order += 1
                    
                elif current_section == 'PRODUCT' and line.strip() and (line[0].isdigit() or line.startswith('-')):
                    # 주 상품만 저장 (하위 상품 제외)
                    if line[0].isdigit():
                        name = line.split('.')[1].strip()
                        if name:
                            PortfolioItem.objects.create(
                                portfolio=portfolio,
                                item_type='PRODUCT',
                                name=name,
                                order=order
                            )
                            order += 1
                    
                elif current_section == 'RATIO' and (line.startswith('-') or ':' in line):
                    if ':' in line:
                        name, ratio_part = line.replace('-', '').split(':')
                        name = name.strip()
                        ratio = int(ratio_part.replace('%', '').strip())
                        PortfolioItem.objects.create(
                            portfolio=portfolio,
                            item_type='RATIO',
                            name=name,
                            ratio=ratio,
                            order=order
                        )
                        order += 1
            except Exception as e:
                logger.error(f"항목 저장 중 에러: {str(e)} - Line: {line}")
                continue

        # 저장 결과 로깅
        types_count = PortfolioItem.objects.filter(portfolio=portfolio, item_type='TYPE').count()
        products_count = PortfolioItem.objects.filter(portfolio=portfolio, item_type='PRODUCT').count()
        ratios_count = PortfolioItem.objects.filter(portfolio=portfolio, item_type='RATIO').count()
        
        logger.info(f"=== 포트폴리오 저장 결과 ===")
        logger.info(f"포트폴리오 ID: {portfolio.id}")
        logger.info(f"투자 종류: {types_count}개")
        logger.info(f"추천 상품: {products_count}개")
        logger.info(f"투자 비율: {ratios_count}개")

        # 응답 데이터 구성
        serializer = PortfolioSerializer(portfolio)
        return Response({
            "message": "포트폴리오가 성공적으로 생성되었습니다.",
            "portfolio": serializer.data,
            "raw_content": assistant_content
        })

    except AuthenticationError:
        logger.error("OpenAI 인증 실패: API 키를 확인하세요.")
        return JsonResponse({"error": "OpenAI 인증 실패. API 키를 확인하세요."}, status=401)

    except RateLimitError:
        logger.error("OpenAI API 요청 제한 초과.")
        return JsonResponse({"error": "OpenAI API 요청 한도를 초과했습니다."}, status=429)

    except OpenAIError as e:
        logger.error(f"OpenAI API 에러 발생: {str(e)}")
        return JsonResponse({"error": f"OpenAI API 에러: {str(e)}"}, status=500)

    except Exception as e:
        logger.error(f"서버 에러 발생: {str(e)}")
        if settings.DEBUG:
            import traceback
            logger.error(traceback.format_exc())
        return JsonResponse({"error": f"서버 에러: {str(e)}"}, status=500)

@api_view(['GET'])
def get_portfolio(request, portfolio_id):
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        serializer = PortfolioSerializer(portfolio)
        return Response(serializer.data)
    except Portfolio.DoesNotExist:
        return Response({"error": "포트폴리오를 찾을 수 없습니다."}, status=404)
    
@api_view(['GET', 'POST'])
def investment_style_type_view(request):
    if request.method == 'GET':
        # 모든 투자 성향 데이터 조회
        investment_styles = InvestmentStyleType.objects.all()
        serializer = InvestmentStyleTypeSerializer(investment_styles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # 새 투자 성향 데이터 추가
        serializer = InvestmentStyleTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def save_user_investment_style(request):
    try:
        user = request.user
        style_type = request.data.get("style")  # style 값만 전달받음

        if not style_type:
            return Response({"error": "투자 성향 타입이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # InvestmentStyleType에서 style이 존재하는지 확인
        try:
            style_instance = InvestmentStyleType.objects.get(type_of=style_type)
        except InvestmentStyleType.DoesNotExist:
            return Response({"error": "유효하지 않은 투자 성향 타입입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 기존 투자 성향 삭제 후 새로 저장 (중복 방지)
        UserInvestmentStyle.objects.filter(user=user).delete()
        user_investment_style = UserInvestmentStyle.objects.create(user=user, style=style_instance)

        return Response(
            {
                "message": f"투자 성향 '{style_type}'이 성공적으로 저장되었습니다.",    
                "style": user_investment_style.style.type_of,
            },
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_investment_style(request):
    user = request.user
    try:
        # 해당 유저의 투자 성향 가져오기
        user_investment_style = UserInvestmentStyle.objects.get(user=user)
        return Response(
            {
                "style": user_investment_style.style.type_of, 
                "feature": user_investment_style.style.feature,
                "strategy": user_investment_style.style.strategy,
            }, 
            status=status.HTTP_200_OK
        )
    except UserInvestmentStyle.DoesNotExist:
        # 투자 성향 정보가 없을 경우
        return Response(
            {"error": "투자 성향 정보가 존재하지 않습니다. 먼저 설문을 진행해주세요."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        # 기타 예외 처리
        return Response(
            {"error": f"서버 오류가 발생했습니다: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_latest_portfolio(request):
    try:
        # 사용자의 가장 최근 포트폴리오 가져오기
        portfolio = Portfolio.objects.filter(
            user=request.user
        ).order_by('-created_at').first()
        
        if portfolio:
            serializer = PortfolioSerializer(portfolio)
            return Response(serializer.data)
        else:
            return Response(None)
    except Exception as e:
        logger.error(f"최근 포트폴리오 조회 중 에러 발생: {str(e)}")
        return Response({"error": "포트폴리오를 불러오는데 실패했습니다."}, status=500)