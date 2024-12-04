# serializers.py

from rest_framework import serializers
from article.models import Article, Comment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    
    class Meta: 
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class CommentDetailSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at', 'updated_at']

class ArticleListSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    author = serializers.CharField(source='user.username', read_only=True)  # 작성자 이름 추가
    
    class Meta: 
        model = Article
        fields = ('id', 'title', 'content', 'author', 'created_at', 'comment_count', 'visit_count')

class ArticleSerializer(serializers.ModelSerializer):
    comments = CommentDetailSerializer(many=True, read_only=True)  # related_name='comments'에 맞게 변경
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    author = serializers.CharField(source='user.username', read_only=True)  # 작성자 이름 추가
    
    class Meta: 
        model = Article
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at', 'visit_count', 'comments', 'comment_count']
        read_only_fields = ['user', 'visit_count', 'comments', 'comment_count']
