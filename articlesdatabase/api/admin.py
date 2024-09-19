
from django.contrib import admin
from .models import Article, Tag , Comment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'title', 'publication_date')
    search_fields = ('title', 'abstract')
    list_filter = ('publication_date', 'tags')
    filter_horizontal = ('authors', 'tags')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('identifiercomment', 'article', 'user', 'content', 'created_at', 'updated_at')
    

    