# Generated by Django 4.2.11 on 2024-11-24 18:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chatbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvestmentStyleType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_of', models.CharField(max_length=100, unique=True)),
                ('feature', models.TextField()),
                ('strategy', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='UserInvestmentStyle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('style', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatbot.investmentstyletype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Portfolio',
        ),
    ]
