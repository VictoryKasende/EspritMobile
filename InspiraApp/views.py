from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
# Restframework
from rest_framework import status
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime
import random

import InspiraApp.models as inspira_models
import InspiraApp.serializers as inspira_serializers

# Authentication

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Vue pour obtenir un token.
    """
    serializer_class = inspira_serializers.MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    Vue pour enregistrer un utilisateur.
    """
    queryset = inspira_models.User.objects.all()
    serializer_class = inspira_serializers.RegisterSerializer
    permission_classes = (AllowAny,)

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Vue pour afficher et mettre à jour le profil de l'utilisateur.
    """
    serializer_class = inspira_serializers.ProfileSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        user_id = self.kwargs["user_id"]
        return inspira_models.Profile.objects.get(user=user_id)
    
    
def generate_numeric_otp(length=7):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


class PasswordEmailVerify(APIView):

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
    )

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = inspira_models.User.objects.get(email=email)
        except inspira_models.User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        otp = generate_numeric_otp()
        user.otp = otp
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        refresh = RefreshToken.for_user(user)
        reset_token = str(refresh.access_token)

        reset_link = f"http://localhost:5173/create-new-password?uidb64={uidb64}&otp={otp}&token={reset_token}"

        # Envoi de l'email
        subject = "Password Reset Request"
        merge_data = {
            "link": reset_link,
            "username": user.username,
            "otp": otp,
        }
        text_body = render_to_string("email/password_reset.txt", merge_data)
        html_body = render_to_string("email/password_reset.html", merge_data)

        msg = EmailMultiAlternatives(
            subject=subject, from_email=settings.EMAIL_HOST_USER,
            to=[email], body=text_body
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()

        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
    
    
class PasswordChangeView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "otp": openapi.Schema(type=openapi.TYPE_STRING),
                "uidb64": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )

    def post(self, request, *args, **kwargs):
        otp = request.data.get("otp")
        uidb64 = request.data.get("uidb64")
        new_password = request.data.get("password")

        if not otp or not uidb64 or not new_password:
            return Response({"message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = urlsafe_base64_decode(uidb64).decode()
            user = inspira_models.User.objects.get(pk=user_id, otp=otp)
        except (inspira_models.User.DoesNotExist, ValueError, TypeError):
            return Response({"message": "Invalid OTP or user."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.otp = None  # Invalider l'OTP après utilisation
        user.save()

        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)


class CategoryListView(generics.ListAPIView):
    """
    Vue pour lister toutes les catégories.
    """
    queryset = inspira_models.Category.objects.all()
    serializer_class = inspira_serializers.CategoryListSerializer


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Vue pour afficher les détails d'une catégorie.
    """
    queryset = inspira_models.Category.objects.all()
    serializer_class = inspira_serializers.CategoryDetailSerializer
    lookup_field = "slug"

class CitationListView(generics.ListAPIView):
    """
    Vue pour lister toutes les citations.
    """
    queryset = inspira_models.Citation.objects.filter(active=True)
    serializer_class = inspira_serializers.CitationListSerializer

class CitationDetailView(generics.RetrieveAPIView):
    """
    Vue pour afficher les détails d'une citation.
    """
    queryset = inspira_models.Citation.objects.filter(active=True)
    serializer_class = inspira_serializers.CitationDetailSerializer
    lookup_field = "slug"

class ThoughtListView(generics.ListAPIView):
    """
    Vue pour lister toutes les pensées.
    """
    queryset = inspira_models.Thought.objects.filter(active=True)
    serializer_class = inspira_serializers.ThoughtListSerializer

class ThoughtDetailView(generics.RetrieveAPIView):
    """
    Vue pour afficher les détails d'une pensée.
    """
    queryset = inspira_models.Thought.objects.filter(active=True)
    serializer_class = inspira_serializers.ThoughtDetailSerializer
    lookup_field = "slug"

class LikeCitationView(APIView):
    """
    Vue pour gérer les likes sur les citations.
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "citation_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "user_id": openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request, *args, **kwargs):
        # Récupération des données du client
        citation_id = request.data.get("citation_id")
        user_id = request.data.get("user_id")

        # Validation des données entrées
        if not citation_id or not user_id:
            return Response(
                {"message": "Citation ID and User ID are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérification de l'existence de la citation
        try:
            citation = inspira_models.Citation.objects.get(id=citation_id)
        except inspira_models.Citation.DoesNotExist:
            return Response(
                {"message": f"Citation with ID {citation_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérification de l'existence de l'utilisateur
        try:
            user = inspira_models.User.objects.get(id=user_id)
        except inspira_models.User.DoesNotExist:
            return Response(
                {"message": f"User with ID {user_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Gestion du like (ajout/suppression)
        content_type = ContentType.objects.get_for_model(citation)  # Type de contenu pour la citation
        like = inspira_models.Like.objects.filter(
            user=user,
            content_type=content_type,
            object_id=citation.id,
        ).first()

        if like:
            # Si un like existe, le supprimer
            like.delete()
            return Response(
                {"message": "You have unliked this citation."},
                status=status.HTTP_200_OK
            )
        else:
            # Si aucun like n'existe, en créer un nouveau
            inspira_models.Like.objects.create(
                user=user,
                content_type=content_type,
                object_id=citation.id,
            )
            return Response(
                {"message": "You have liked this citation."},
                status=status.HTTP_201_CREATED
            )

class FavoriteCitationView(APIView):
    """
    Vue pour gérer les favoris sur les citations.
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "citation_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "user_id": openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request, *args, **kwargs):
        # Récupération des données du client
        citation_id = request.data.get("citation_id")
        user_id = request.data.get("user_id")

        # Validation des données entrées
        if not citation_id or not user_id:
            return Response(
                {"message": "Citation ID and User ID are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérification de l'existence de la citation
        try:
            citation = inspira_models.Citation.objects.get(id=citation_id)
        except inspira_models.Citation.DoesNotExist:
            return Response(
                {"message": f"Citation with ID {citation_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérification de l'existence de l'utilisateur
        try:
            user = inspira_models.User.objects.get(id=user_id)
        except inspira_models.User.DoesNotExist:
            return Response(
                {"message": f"User with ID {user_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Gestion du favori (ajout/suppression)
        content_type = ContentType.objects.get_for_model(citation)  # Type de contenu pour la citation
        favorite = inspira_models.Favorite.objects.filter(
            user=user,
            content_type=content_type,
            object_id=citation.id,
        ).first()

        if favorite:
            # Si un favori existe, le supprimer
            favorite.delete()
            return Response(
                {"message": "You have removed this citation from favorites."},
                status=status.HTTP_200_OK
            )
        else:
            # Si aucun favori n'existe, en créer un nouveau
            inspira_models.Favorite.objects.create(
                user=user,
                content_type=content_type,
                object_id=citation.id,
            )
            return Response(
                {"message": "You have added this citation to favorites."},
                status=status.HTTP_201_CREATED  
            )
        
class LikeThoughtView(APIView):
    """
    Vue pour gérer les likes sur les pensées.
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "thought_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "user_id": openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request, *args, **kwargs):
        # Récupération des données du client
        thought_id = request.data.get("thought_id")
        user_id = request.data.get("user_id")

        # Validation des données entrées
        if not thought_id or not user_id:
            return Response(
                {"message": "Thought ID and User ID are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérification de l'existence de la pensée
        try:
            thought = inspira_models.Thought.objects.get(id=thought_id)
        except inspira_models.Thought.DoesNotExist:
            return Response(
                {"message": f"Thought with ID {thought_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérification de l'existence de l'utilisateur
        try:
            user = inspira_models.User.objects.get(id=user_id)
        except inspira_models.User.DoesNotExist:
            return Response(
                {"message": f"User with ID {user_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Gestion du like (ajout/suppression)
        content_type = ContentType.objects.get_for_model(thought)  # Type de contenu pour la pensée
        like = inspira_models.Like.objects.filter(
            user=user,
            content_type=content_type,
            object_id=thought.id,
        ).first()

        if like:
            # Si un like existe, le supprimer
            like.delete()
            return Response(
                {"message": "You have unliked this thought."},
                status=status.HTTP_200_OK
            )
        else:
            # Si aucun like n'existe, en créer un nouveau
            inspira_models.Like.objects.create(
                user=user,
                content_type=content_type,
                object_id=thought.id,
            )
            return Response(
                {"message": "You have liked this thought."},
                status=status.HTTP_201_CREATED
            )
        
class FavoriteThoughtView(APIView):
    """
    Vue pour gérer les favoris sur les pensées.
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "thought_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "user_id": openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request, *args, **kwargs):
        # Récupération des données du client
        thought_id = request.data.get("thought_id")
        user_id = request.data.get("user_id")

        # Validation des données entrées
        if not thought_id or not user_id:
            return Response(
                {"message": "Thought ID and User ID are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérification de l'existence de la pensée
        try:
            thought = inspira_models.Thought.objects.get(id=thought_id)
        except inspira_models.Thought.DoesNotExist:
            return Response(
                {"message": f"Thought with ID {thought_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Vérification de l'existence de l'utilisateur
        try:
            user = inspira_models.User.objects.get(id=user_id)
        except inspira_models.User.DoesNotExist:
            return Response(
                {"message": f"User with ID {user_id} not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Gestion du favori (ajout/suppression)
        content_type = ContentType.objects.get_for_model(thought)  # Type de contenu pour la pensée
        favorite = inspira_models.Favorite.objects.filter(
            user=user,
            content_type=content_type,
            object_id=thought.id,
        ).first()

        if favorite:
            # Si un favori existe, le supprimer
            favorite.delete()
            return Response(
                {"message": "You have removed this thought from favorites."},
                status=status.HTTP_200_OK
            )
        else:
            # Si aucun favori n'existe, en créer un nouveau
            inspira_models.Favorite.objects.create(
                user=user,
                content_type=content_type,
                object_id=thought.id,
            )
            return Response(
                {"message": "You have added this thought to favorites."},
                status=status.HTTP_201_CREATED
            )

class FavoriteListView(generics.ListAPIView):
    """
    Vue pour lister tous les favoris d'un utilisateur.
    """
    #serializer_class = inspira_serializers.FavoriteListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return inspira_models.Favorite.objects.filter(user=user)




