
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import Article, Tag, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username"]

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    article = serializers.SlugRelatedField(slug_field='identifier', queryset=Article.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'identifiercomment', 'article', 'user', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'identifiercomment', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ArticleSerializer(serializers.ModelSerializer):
    authors = serializers.ListField(child=serializers.CharField(), write_only=True)
    tags = serializers.ListField(child=serializers.CharField(), write_only=True)
    author_names = serializers.SerializerMethodField(read_only=True)
    tag_names = serializers.SerializerMethodField(read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'identifier', 'title', 'abstract', 'publication_date', 'authors', 'tags', 'author_names', 'tag_names', 'owner', 'comments']

    def get_author_names(self, obj):
        return [user.username for user in obj.authors.all()]

    def get_tag_names(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def create(self, validated_data):
        authors_data = validated_data.pop('authors', [])
        tags_data = validated_data.pop('tags', [])
        
        article = Article.objects.create(**validated_data)
        
        # Handle authors
        authors = User.objects.filter(username__in=authors_data)
        article.authors.set(authors)
        
        # Handle tags
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            article.tags.add(tag)
        
        return article

    def update(self, instance, validated_data):
        authors_data = validated_data.pop('authors', None)
        tags_data = validated_data.pop('tags', None)
        
        instance = super().update(instance, validated_data)
        
        if authors_data is not None:
            authors = User.objects.filter(username__in=authors_data)
            instance.authors.set(authors)
        
        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        
        return instance