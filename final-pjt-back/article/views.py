from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from django.shortcuts import render
from .serializers.serializer import ArticleListSerializer, ArticleSerializer, CommentSerializer
from .models import Article, Comment
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from django.db.models import F
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def article_list(request):#게시글 리스트 출력
    if request.method == 'GET':
        articles = Article.objects.all()
        serializers = ArticleListSerializer(articles, many=True)
        return Response(serializers.data)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def article_create(request):  # 게시글 작성
    if request.method == 'POST':
        print(request.data)
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)  # 현재 로그인한 사용자 정보 저장
            return Response(serializer.data)
        
@api_view(['GET'])
def article_detail(request, article_pk):
    try:
        article = Article.objects.get(pk=article_pk)
    except Article.DoesNotExist:
        raise NotFound(detail="게시글을 찾을 수 없습니다.")
    
    if request.method == 'GET':
        cookie_name = f'viewed_article_{article_pk}'
        last_view_time_str = request.COOKIES.get(cookie_name)
        current_time = timezone.now()
        
        should_increment = False

        logger.debug(f"Request to view article {article_pk}. Cookie '{cookie_name}': {last_view_time_str}")

        if last_view_time_str:
            try:
                last_view_time = timezone.datetime.fromisoformat(last_view_time_str)
                if timezone.is_naive(last_view_time):
                    last_view_time = timezone.make_aware(last_view_time, timezone.get_current_timezone())
                time_diff = current_time - last_view_time
                logger.debug(f"Time since last view: {time_diff}")
                if time_diff > timedelta(minutes=5):
                    should_increment = True
            except ValueError:
                # 쿠키 파싱 오류 시 조회수 증가
                logger.warning(f"Failed to parse cookie '{cookie_name}': {last_view_time_str}. Incrementing view count.")
                should_increment = True
        else:
            # 쿠키가 없으면 조회수 증가
            logger.debug(f"No cookie '{cookie_name}' found. Incrementing view count.")
            should_increment = True

        if should_increment:
            # 조회수 증가
            Article.objects.filter(pk=article_pk).update(visit_count=F('visit_count') + 1)
            article.refresh_from_db()
            logger.debug(f"Incremented view count for article {article_pk}. New visit_count: {article.visit_count}")
            # 응답에 쿠키 설정 (유효기간 5분)
            response = Response(ArticleSerializer(article).data)
            max_age = 5 * 60  # 5분
            response.set_cookie(
                key=cookie_name,
                value=current_time.isoformat(),
                max_age=max_age,
                httponly=True,  # JavaScript에서 쿠키 접근 불가
                secure=False,    # HTTPS 사용 시 True로 설정
                samesite='Lax',  # 'Strict' 또는 'None' (HTTPS 사용 시)
                path='/',        # 모든 경로에서 쿠키 접근 가능
            )
            logger.debug(f"Set cookie '{cookie_name}' with value {current_time.isoformat()}")
            return response
        else:
            # 조회수 증가 없이 데이터 반환
            logger.debug(f"Not incrementing view count for article {article_pk}.")
            serializer = ArticleSerializer(article)
            return Response(serializer.data)
    
# @permission_classes([IsAuthenticated])
@api_view(['DELETE', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def article_modify(request, article_pk):  # 게시글 수정 및 삭제
    try:
        article = Article.objects.get(pk=article_pk)
    except Article.DoesNotExist:
        raise NotFound(detail="Article not found")
    
    # 게시글 작성자만 수정 및 삭제 가능
    if request.method in ['DELETE', 'PUT', 'PATCH']:
        if article.user != request.user:
            return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'DELETE':
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    elif request.method in ['PUT', 'PATCH']:
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_create(request, article_pk):
    try:
        article = Article.objects.get(pk=article_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(
                article=article,
                user=request.user
            )
            # 댓글이 추가된 전체 게시글 데이터를 반환
            article_serializer = ArticleSerializer(article)
            return Response(article_serializer.data, status=status.HTTP_201_CREATED)
    except Article.DoesNotExist:
        return Response({'error': 'Article not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def comment_update(request, comment_pk, article_pk):
    try:
        comment = Comment.objects.get(pk=comment_pk)
    except Comment.DoesNotExist:
        raise NotFound(detail="Comment not found")
    
    # 댓글 작성자만 수정 가능
    if comment.user != request.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method in ['PUT', 'PATCH']:
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
    
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def comment_delete(request, comment_pk,article_pk):
    try:
        comment = Comment.objects.get(pk=comment_pk)
    except Comment.DoesNotExist:
        raise NotFound(detail="Comment not found")
    
    # 댓글 작성자만 삭제 가능
    if comment.user != request.user:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'DELETE':
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def article_delete(request, article_pk):
    try:
        article = Article.objects.get(pk=article_pk)
    except Article.DoesNotExist:
        raise NotFound(detail="Article not found")
    
    # 게시글 작성자만 삭제 가능
    if article.user != request.user:
        raise PermissionDenied(detail="You do not have permission to delete this article.")
    
    article.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)