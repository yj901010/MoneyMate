from django.db import models

class DepositProducts(models.Model):
    fin_prdt_cd = models.CharField(max_length=255, unique=True)#금융상품코드
    kor_co_nm=models.TextField()#금융회사명
    fin_prdt_nm=models.TextField()#금융 상품명
    etc_note=models.TextField()# 금융 상품 설명
    join_deny=models.IntegerField()# 가입 제한(1: 제한 없음, 2: 서민 전용, 3: 일부 제한)
    join_member=models.TextField()# 가입 대상
    join_way=models.TextField()#가입 방법
    spcl_cnd=models.TextField()#우대 조건

class DepositOptions(models.Model):
    product=models.ForeignKey(DepositProducts,related_name='options',on_delete=models.CASCADE)
    fin_prdt_cd=models.CharField(max_length=50)# 금융 상품 코드
    intr_rate_type_nm=models.CharField(max_length=100) #저축금리 유형명
    intr_rate=models.FloatField() #저축금리3
    intr_rate2=models.FloatField()#최고우대금리
    save_trm=models.IntegerField()#저축기간

class Change(models.Model):
    cur_unit=models.CharField(unique=True,max_length=50)
    cur_nm=models.CharField(max_length=50)
    ttb=models.TextField()#송금 받을 때
    tts=models.TextField()#송금 보낼 때
    deal_bas_r=models.TextField()#매매기준율