from django.core.management.base import BaseCommand
from chatbot.models import InvestmentStyleType

class Command(BaseCommand):
    help = "Populate investment styles into the database"

    def handle(self, *args, **kwargs):
        data = [
            {
                "type_of": "안정형",
                "feature": "예금이나 적금 수준의 수익률을 기대하며, 투자원금에 손실이 발생하는 것을 원하지 않습니다.",
                "strategy": "원금 손실의 우려가 없는 상품에 투자하는 것이 바람직하며 CMA와 MMF가 좋습니다."
            },
            {
                "type_of": "안정추구형",
                "feature": "투자원금의 손실위험을 최소화하고, 이자 소득이나 배당소득 수준의 안정적인 투자를 목표로 합니다.",
                "strategy": "채권형펀드가 적당하며, 그중에서도 장기채권형펀드 등이 좋습니다."
            },
            {
                "type_of": "위험중립형",
                "feature": "투자에는 그에 상응하는 투자위험이 있음을 충분히 인식하고 있으며, 예·적금보다 높은 수익을 기대할 수 있다면 일정수준의 손실위험을 감수할 수 있습니다.",
                "strategy": "적립식펀드나 주가연동상품처럼 중위험 펀드로 분류되는 상품을 선택하는 것이 좋습니다."
            },
            {
                "type_of": "적극투자형",
                "feature": "투자원금의 보전보다는 위험을 감내하더라도 높은 수준의 투자수익을 추구합니다.",
                "strategy": "국내외 주식형펀드와 원금비보장형 주가연계증권(ELS) 등 고수익·고위험 상품에 투자할 수 있습니다."
            },
            {
                "type_of": "공격투자형",
                "feature": "시장평균수익률을 훨씬 넘어서는 높은 수준의 투자수익을 추구하며, 이를 위해 자산가격의 변동에 따른 손실위험을 적극 수용할 수 있습니다.",
                "strategy": "주식 비중이 70% 이상인 고위험 펀드가 적당하고, 자산의 10% 정도는 직접투자(주식)도 고려해볼 만합니다."
            },
        ]

        for item in data:
            InvestmentStyleType.objects.get_or_create(
                type_of=item["type_of"],
                defaults={
                    "feature": item["feature"],
                    "strategy": item["strategy"]
                }
            )
        self.stdout.write(self.style.SUCCESS("Investment styles populated."))
