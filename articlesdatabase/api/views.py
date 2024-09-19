from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article, Tag, Comment
from .serializers import ArticleSerializer, TagSerializer, UserSerializer, RegisterSerializer ,CommentSerializer
from .permissions import IsOwnerOrReadOnly
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from django_filters import rest_framework as df_filters
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
import pandas as pd
from io import StringIO
from django.db.models import F
from django.http import HttpResponse
import csv
import uuid
from .permissions import IsCommentOwnerOrReadOnly

class UserDetailAPI(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

class RegisterUserAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

class ArticleFilter(df_filters.FilterSet):
    year = df_filters.NumberFilter(field_name='publication_date', lookup_expr='year')
    month = df_filters.NumberFilter(field_name='publication_date', lookup_expr='month')
    authors = df_filters.CharFilter(method='filter_authors')
    tags = df_filters.CharFilter(method='filter_tags')
    keywords = df_filters.CharFilter(method='filter_keywords')

    class Meta:
        model = Article
        fields = ['year', 'month', 'authors', 'tags', 'keywords']

    def filter_authors(self, queryset, name, value):
        author_names = [name.strip() for name in value.split(',')]
        return queryset.filter(authors__username__in=author_names)

    def filter_tags(self, queryset, name, value):
        tag_names = [name.strip() for name in value.split(',')]
        return queryset.filter(tags__name__in=tag_names)

    def filter_keywords(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(abstract__icontains=value))

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ['title', 'abstract']
    ordering_fields = ['publication_date', 'title']
    ordering = ['-publication_date']  # Default ordering
    pagination_class = PageNumberPagination
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    lookup_field = 'identifier'

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

   
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    
    @action(detail=False, methods=['delete'])
    def delete_by_identifier(self, request, *args, **kwargs):
        identifier = request.query_params.get('identifier')
        if not identifier:
            return Response({'detail': 'Identifier parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            article = Article.objects.get(identifier=identifier)
        except Article.DoesNotExist:
            return Response({'detail': 'Article not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check permissions
        if article.owner != request.user and not request.user.is_superuser:
            return Response({'detail': 'You do not have permission to delete this article.'}, status=status.HTTP_403_FORBIDDEN)

        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def download_csv(self, request):
        # Get query parameters
        identifiers = request.query_params.get('identifiers', '').split(',')
        
        # Use the existing filterset to apply filters
        queryset = self.filter_queryset(self.get_queryset())
        
        # If identifiers are provided, filter by them
        if identifiers and identifiers[0]:  # Check if the list is not empty
            queryset = queryset.filter(identifier__in=identifiers)
        
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="articles.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header
        writer.writerow(['Identifier', 'Title', 'Authors', 'Abstract', 'Publication Date', 'Tags'])
        
        # Write data
        for article in queryset:
            writer.writerow([
                article.identifier,
                article.title,
                ', '.join([author.username for author in article.authors.all()]),
                article.abstract,
                article.publication_date,
                ', '.join([tag.name for tag in article.tags.all()])
            ])
        
        return response
    @action(detail=True, methods=['get'])
    def comments(self, request, identifier=None):
        article = self.get_object()
        comments = article.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    




class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentOwnerOrReadOnly]
    lookup_field = 'identifiercomment'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user__username', 'article__identifier']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, identifiercomment=f"comment_{uuid.uuid4()}")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def article_comments(self, request):
        article_identifier = request.query_params.get('article_identifier', None)
        if article_identifier is None:
            return Response({'error': 'article_identifier is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        comments = Comment.objects.filter(article__identifier=article_identifier)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
