from rest_framework import serializers
import InspiraApp.models as inspira_models 
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class CitationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = inspira_models.Citation
        fields = ('id', 'title', 'slug', 'author', 'description', 'image', 'active', 'created_at', 'updated_at')

class CitationDetailSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    favorite_count = serializers.SerializerMethodField()

    class Meta:
        model = inspira_models.Citation
        fields = ('id', 'title', 'slug', 'author', 'description', 'image', 'active', 'like_count', 'favorite_count', 'created_at', 'updated_at')

    def get_like_count(self, obj):
        return obj.like_count()

    def get_favorite_count(self, obj):
        return obj.favorite_count()

class ThoughtListSerializer(serializers.ModelSerializer):
    class Meta:
        model = inspira_models.Thought
        fields = ('id', 'title', 'slug', 'author', 'description', 'image', 'active', 'created_at', 'updated_at')


class ThoughtDetailSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    favorite_count = serializers.SerializerMethodField()
    paragraphs = serializers.StringRelatedField(many=True)  

    class Meta:
        model = inspira_models.Thought
        fields = ('id', 'title', 'slug', 'author', 'description', 'image', 'active', 'like_count', 'favorite_count', 'paragraphs', 'created_at', 'updated_at')

    def get_like_count(self, obj):
        return obj.like_count()

    def get_favorite_count(self, obj):
        return obj.favorite_count()


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = inspira_models.Category
        fields = ('id', 'name', 'slug', 'description', 'created_at', 'updated_at')

class CategoryDetailSerializer(serializers.ModelSerializer):
    citations = CitationListSerializer(many=True, read_only=True)  # Relation inversée pour Citation
    thoughts = ThoughtListSerializer(many=True, read_only=True)    # Relation inversée pour Thought

    class Meta:
        model = inspira_models.Category
        fields = ('id', 'name', 'slug', 'description', 'citations', 'thoughts', 'created_at', 'updated_at')



    

      