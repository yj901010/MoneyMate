from django.core.management.base import BaseCommand
from finlife.models import Change

class Command(BaseCommand):
    help = "Populate exchange rates into the database"

    def handle(self, *args, **kwargs):
        data = [
    {"cur_unit": "AED", "cur_nm": "아랍에미리트 디르함", "ttb": 376.83, "tts": 384.44, "deal_bas_r": 380.64},
    {"cur_unit": "AUD", "cur_nm": "호주 달러", "ttb": 900.98, "tts": 919.19, "deal_bas_r": 910.09},
    {"cur_unit": "BHD", "cur_nm": "바레인 디나르", "ttb": 3672.08, "tts": 3746.27, "deal_bas_r": 3709.18},
    {"cur_unit": "BND", "cur_nm": "브루나이 달러", "ttb": 1028.2, "tts": 1048.97, "deal_bas_r": 1038.59},
    {"cur_unit": "CAD", "cur_nm": "캐나다 달러", "ttb": 990.38, "tts": 1010.39, "deal_bas_r": 1000.39},
    {"cur_unit": "CHF", "cur_nm": "스위스 프랑", "ttb": 1561.06, "tts": 1592.59, "deal_bas_r": 1576.83},
    {"cur_unit": "CNH", "cur_nm": "위안화", "ttb": 190.92, "tts": 194.77, "deal_bas_r": 192.85},
    {"cur_unit": "DKK", "cur_nm": "덴마아크 크로네", "ttb": 194.38, "tts": 198.31, "deal_bas_r": 196.35},
    {"cur_unit": "EUR", "cur_nm": "유로", "ttb": 1449.86, "tts": 1479.15, "deal_bas_r": 1464.51},
    {"cur_unit": "GBP", "cur_nm": "영국 파운드", "ttb": 1742.26, "tts": 1777.45, "deal_bas_r": 1759.86},
    {"cur_unit": "HKD", "cur_nm": "홍콩 달러", "ttb": 177.83, "tts": 181.42, "deal_bas_r": 179.63},
    {"cur_unit": "IDR(100)", "cur_nm": "인도네시아 루피아", "ttb": 8.69, "tts": 8.86, "deal_bas_r": 8.78},
    {"cur_unit": "JPY(100)", "cur_nm": "일본 옌", "ttb": 896.94, "tts": 915.06, "deal_bas_r": 906},
    {"cur_unit": "KRW", "cur_nm": "한국 원", "ttb": 0, "tts": 0, "deal_bas_r": 1},
    {"cur_unit": "KWD", "cur_nm": "쿠웨이트 디나르", "ttb": 4498.56, "tts": 4589.45, "deal_bas_r": 4544.01},
    {"cur_unit": "MYR", "cur_nm": "말레이지아 링기트", "ttb": 309.98, "tts": 316.25, "deal_bas_r": 313.12},
    {"cur_unit": "NOK", "cur_nm": "노르웨이 크로네", "ttb": 124.99, "tts": 127.52, "deal_bas_r": 126.26},
    {"cur_unit": "NZD", "cur_nm": "뉴질랜드 달러", "ttb": 811.02, "tts": 827.41, "deal_bas_r": 819.22},
    {"cur_unit": "SAR", "cur_nm": "사우디 리얄", "ttb": 368.64, "tts": 376.09, "deal_bas_r": 372.37},
    {"cur_unit": "SEK", "cur_nm": "스웨덴 크로나", "ttb": 125.15, "tts": 127.68, "deal_bas_r": 126.42},
    {"cur_unit": "SGD", "cur_nm": "싱가포르 달러", "ttb": 1028.2, "tts": 1048.97, "deal_bas_r": 1038.59},
    {"cur_unit": "THB", "cur_nm": "태국 바트", "ttb": 39.85, "tts": 40.66, "deal_bas_r": 40.26},
            {"cur_unit": "USD", "cur_nm": "미국 달러", "ttb": 1384.11, "tts": 1412.08, "deal_bas_r": 1398.1}
        ]

        for item in data:
            Change.objects.update_or_create(
            cur_unit=item["cur_unit"],
            defaults={
                "cur_nm": item["cur_nm"],
                "ttb": item["ttb"],
                "tts": item["tts"],
                "deal_bas_r": item["deal_bas_r"],
            },
        )

        self.stdout.write(self.style.SUCCESS('Successfully populated exchange rates'))


