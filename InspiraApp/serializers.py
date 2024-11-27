from rest_framework import serializers
import InspiraApp.models as inspira_models 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token
 

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = inspira_models.User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = inspira_models.User.objects.create_user(
            username=validated_data['username'], 
            email=validated_data['email'], 
            password=validated_data['password']
        )

        return user 
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = inspira_models.User
        fields = ('id', 'username', 'email')

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = inspira_models.Profile
        fields = "__all__"

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

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



    

      