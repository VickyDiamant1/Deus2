from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Article(models.Model):
    identifier = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    publication_date = models.DateField()
    authors = models.ManyToManyField(User, related_name='articles')
    tags = models.ManyToManyField('Tag', related_name='articles') 
    owner = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    identifiercomment = models.CharField(max_length=100, unique=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment {self.identifiercomment} by {self.user.username} on {self.article.title}"