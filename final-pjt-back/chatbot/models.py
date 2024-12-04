from django.db import models
from django.conf import settings

class InvestmentStyleType(models.Model):
    type_of = models.CharField(max_length=100, unique=True)  # 투자 성향
    feature = models.TextField()  # 투자 성향별 특징
    strategy = models.TextField()  # 투자 전략

    def __str__(self):
        return self.type_of

class UserInvestmentStyle(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    style = models.ForeignKey(InvestmentStyleType, on_delete=models.CASCADE)  # 투자 성향 타입 참조
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.style.type_of}"
    
class Portfolio(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    investment_style = models.ForeignKey(UserInvestmentStyle, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Portfolio - {self.created_at.strftime('%Y-%m-%d')}"

class PortfolioItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('TYPE', '투자 종류'),
        ('PRODUCT', '추천 상품'),
        ('RATIO', '투자 비율'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    ratio = models.IntegerField(null=True, blank=True)
    order = models.IntegerField()

    class Meta:
        ordering = ['item_type', 'order']

    def __str__(self):
        return f"{self.portfolio.user.username} - {self.item_type}: {self.name}"