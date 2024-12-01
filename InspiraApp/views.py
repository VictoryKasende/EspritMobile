from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.shortcuts import get_object_or_404
from django.http import Http404
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
import InspiraApp.permissions as inspira_permissions

# Authentication

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Vue pour obtenir un token.
    """
    serializer_class = inspira_serializers.MyTokenObtainPairSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="Obtenir un token d'authentification",
        operation_description="Permet d'obtenir un token JWT en utilisant les identifiants de l'utilisateur.",
        request_body=inspira_serializers.MyTokenObtainPairSerializer,
        responses={
            200: openapi.Response(
                description="Token d'authentification généré avec succès.",
                schema=inspira_serializers.MyTokenObtainPairSerializer
            ),
            400: openapi.Response(
                description="Identifiants invalides."
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Récupère le token d'authentification de l'utilisateur.
        """
        return super().post(request, *args, **kwargs)



class RegisterView(generics.CreateAPIView):
    """
    Vue pour enregistrer un utilisateur.
    """
    queryset = inspira_models.User.objects.all()
    serializer_class = inspira_serializers.RegisterSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="Enregistrement d'un utilisateur",
        operation_description="Permet d'enregistrer un nouvel utilisateur.",
        request_body=inspira_serializers.RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Utilisateur enregistré avec succès.",
                schema=inspira_serializers.RegisterSerializer
            ),
            400: openapi.Response(
                description="Requête invalide."
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Crée un nouvel utilisateur.
        """
        return super().post(request, *args, **kwargs)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Vue pour afficher et mettre à jour le profil de l'utilisateur.
    """
    serializer_class = inspira_serializers.ProfileSerializer
    permission_classes = (IsAuthenticated, inspira_permissions.IsOwnerOrReadOnly)

    def get_object(self):
        return inspira_models.Profile.objects.get(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Afficher le profil utilisateur",
        operation_description="Récupère les informations du profil de l'utilisateur connecté.",
        responses={
            200: openapi.Response(
                description="Profil utilisateur récupéré avec succès.",
                schema=inspira_serializers.ProfileSerializer
            ),
            401: openapi.Response(
                description="Authentification requise."
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',  # Nom de l'en-tête
                openapi.IN_HEADER,  # Indique que c'est un en-tête
                description="Token JWT d'authentification",
                type=openapi.TYPE_STRING,
                required=True,  # Spécifie que l'en-tête est obligatoire
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Récupère le profil utilisateur.
        """
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Mettre à jour le profil utilisateur",
        operation_description="Met à jour les informations du profil de l'utilisateur connecté.",
        request_body=inspira_serializers.ProfileSerializer,
        responses={
            200: openapi.Response(
                description="Profil utilisateur mis à jour avec succès.",
                schema=inspira_serializers.ProfileSerializer
            ),
            400: openapi.Response(
                description="Requête invalide."
            ),
            401: openapi.Response(
                description="Authentification requise."
            ),
        },
        manual_parameters=[
            openapi.Parameter(
                'Authorization',  # Nom de l'en-tête
                openapi.IN_HEADER,  # Indique que c'est un en-tête
                description="Token JWT d'authentification",
                type=openapi.TYPE_STRING,
                required=True,  # Spécifie que l'en-tête est obligatoire
            ),
        ]
    )
    def put(self, request, *args, **kwargs):
        """
        Met à jour le profil utilisateur.
        """
        return super().put(request, *args, **kwargs)

    
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
        operation_summary="Vérification par email pour réinitialiser le mot de passe",
        operation_description="Envoie un email avec un OTP pour vérifier l'identité de l'utilisateur et permettre la réinitialisation du mot de passe.",
        responses={
            200: openapi.Response(
                description="Email de réinitialisation envoyé avec succès."
            ),
            400: openapi.Response(
                description="Email requis."
            ),
            404: openapi.Response(
                description="Utilisateur non trouvé."
            ),
        }
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
        ),
        operation_summary="Changer le mot de passe",
        operation_description="Permet de réinitialiser le mot de passe de l'utilisateur après vérification de l'OTP.",
        responses={
            200: openapi.Response(
                description="Mot de passe réinitialisé avec succès."
            ),
            400: openapi.Response(
                description="OTP ou utilisateur invalide."
            ),
        }
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


# Inspirations

class CategoryListView(generics.ListAPIView):
    """
    Vue pour lister toutes les catégories.
    """
    queryset = inspira_models.Category.objects.all()
    serializer_class = inspira_serializers.CategoryListSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Liste des catégories",
        operation_description="Récupère toutes les catégories disponibles.",
        responses={
            200: openapi.Response(
                description="Liste des catégories récupérée avec succès",
                schema=inspira_serializers.CategoryListSerializer
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Récupère la liste des catégories.
        """
        return super().get(request, *args, **kwargs)


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Vue pour afficher les détails d'une catégorie.
    """
    queryset = inspira_models.Category.objects.all()
    serializer_class = inspira_serializers.CategoryDetailSerializer
    lookup_field = "slug"
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Détails d'une catégorie",
        operation_description="Récupère les détails d'une catégorie par son identifiant unique (slug).",
        responses={
            200: openapi.Response(
                description="Détails de la catégorie récupérés avec succès",
                schema=inspira_serializers.CategoryDetailSerializer
            ),
            404: openapi.Response(description="Catégorie non trouvée.")
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Récupère les détails de la catégorie.
        """
        return super().get(request, *args, **kwargs)

class CitationListView(generics.ListAPIView):
    """
    Vue pour lister toutes les citations.
    """
    queryset = inspira_models.Citation.objects.filter(active=True)
    serializer_class = inspira_serializers.CitationListSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Liste des citations",
        operation_description="Récupère toutes les citations actives disponibles.",
        responses={
            200: openapi.Response(
                description="Liste des citations récupérée avec succès",
                schema=inspira_serializers.CitationListSerializer
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Récupère la liste des citations.
        """
        return super().get(request, *args, **kwargs)

class CitationDetailView(generics.RetrieveAPIView):
    """
    Vue pour afficher les détails d'une citation.
    """
    queryset = inspira_models.Citation.objects.filter(active=True)
    serializer_class = inspira_serializers.CitationDetailSerializer
    lookup_field = "slug"
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Détails d'une citation",
        operation_description="Récupère les détails d'une citation par son identifiant unique (slug).",
        responses={
            200: openapi.Response(
                description="Détails de la citation récupérés avec succès",
                schema=inspira_serializers.CitationDetailSerializer
            ),
            404: openapi.Response(description="Citation non trouvée.")
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Récupère les détails de la citation.
        """
        return super().get(request, *args, **kwargs)

class ThoughtListView(generics.ListAPIView):
    """
    Vue pour lister toutes les pensées.
    """
    queryset = inspira_models.Thought.objects.filter(active=True)
    serializer_class = inspira_serializers.ThoughtListSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Liste des pensées",
        operation_description="Récupère toutes les pensées actives disponibles.",
        responses={
            200: openapi.Response(
                description="Liste des pensées récupérée avec succès",
                schema=inspira_serializers.ThoughtListSerializer
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Récupère la liste des pensées.
        """
        return super().get(request, *args, **kwargs)

class ThoughtDetailView(generics.RetrieveAPIView):
    """
    Vue pour afficher les détails d'une pensée.
    """
    queryset = inspira_models.Thought.objects.filter(active=True)
    serializer_class = inspira_serializers.ThoughtDetailSerializer
    lookup_field = "slug"
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Détails d'une pensée",
        operation_description="Récupère les détails d'une pensée par son identifiant unique (slug).",
        responses={
            200: openapi.Response(
                description="Détails de la pensée récupérés avec succès",
                schema=inspira_serializers.ThoughtDetailSerializer
            ),
            404: openapi.Response(description="Pensée non trouvée.")
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Récupère les détails de la pensée.
        """
        return super().get(request, *args, **kwargs)

class GenericLikeFavoriteView(APIView):
    """
    Vue générique pour gérer les likes et les favoris.
    """
    model = None  # Modèle à gérer (Citation, Thought, etc.)
    relation_model = None  # Modèle de relation (Like ou Favorite)
    relation_type = ""  # Type d'action : "like" ou "favorite"
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Ajouter ou supprimer un like ou favori",
        operation_description="Permet à l'utilisateur d'ajouter ou de supprimer un like ou favori sur un élément spécifique (Citation, Pensée, etc.).",
        responses={
            201: openapi.Response(description="Objet liké ou ajouté aux favoris avec succès."),
            400: openapi.Response(description="Vous avez déjà effectué cette action."),
            404: openapi.Response(description="Objet non trouvé."),
        }
    )

    def post(self, request, *args, **kwargs):
        # Récupération de l'objet cible (exemple : Citation ou Thought)
        obj_id = kwargs.get('object_id')
        obj = get_object_or_404(self.model, id=obj_id)

        # Vérification si la relation existe déjà
        content_type = ContentType.objects.get_for_model(obj)
        relation_exists = self.relation_model.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
        ).exists()

        if relation_exists:
            return Response(
                {"message": f"You have already {self.relation_type}d this item."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Création de la relation
        self.relation_model.objects.create(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
        )
        return Response(
            {"message": f"You have {self.relation_type}d this item."},
            status=status.HTTP_201_CREATED
        )

    @swagger_auto_schema(
        operation_summary="Supprimer un like ou favori",
        operation_description="Permet à l'utilisateur de supprimer un like ou favori d'un élément spécifique.",
        responses={
            200: openapi.Response(description="Objet retiré des likes ou favoris avec succès."),
            404: openapi.Response(description="Aucun like ou favori trouvé pour cet élément."),
        }
    )
    def delete(self, request, *args, **kwargs):
        # Récupération de l'objet cible (exemple : Citation ou Thought)
        obj_id = kwargs.get('id')
        obj = get_object_or_404(self.model, id=obj_id)

        # Suppression de la relation si elle existe
        content_type = ContentType.objects.get_for_model(obj)
        relation = self.relation_model.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=obj_id,
        ).first()

        if not relation:
            # Retourne un message d'erreur plus explicite
            return Response(
                {
                    "detail": f"No {self.relation_type} found for this item with ID {obj_id}. "
                              f"Make sure you have already {self.relation_type}d this item."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Suppression de la relation
        relation.delete()
        return Response(
            {"message": f"You have removed your {self.relation_type} for this item."},
            status=status.HTTP_200_OK
        )

class LikeCitationView(GenericLikeFavoriteView):
    model = inspira_models.Citation
    relation_model = inspira_models.Like
    relation_type = "like"
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Ajouter un like à une citation",
        operation_description="Permet d'ajouter un like à une citation spécifique.",
        responses={
            201: openapi.Response(description="Citation likée avec succès."),
            400: openapi.Response(description="Vous avez déjà liké cette citation."),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class FavoriteCitationView(GenericLikeFavoriteView):
    model = inspira_models.Citation
    relation_model = inspira_models.Favorite
    relation_type = "favorite"
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Ajouter une citation aux favoris",
        operation_description="Permet d'ajouter une citation aux favoris.",
        responses={
            201: openapi.Response(description="Citation ajoutée aux favoris avec succès."),
            400: openapi.Response(description="Vous avez déjà ajouté cette citation aux favoris."),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LikeThoughtView(GenericLikeFavoriteView):
    model = inspira_models.Thought
    relation_model = inspira_models.Like
    relation_type = "like"
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Ajouter un like à une pensée",
        operation_description="Permet d'ajouter un like à une pensée spécifique.",
        responses={
            201: openapi.Response(description="Pensée likée avec succès."),
            400: openapi.Response(description="Vous avez déjà liké cette pensée."),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class FavoriteThoughtView(GenericLikeFavoriteView):
    model = inspira_models.Thought
    relation_model = inspira_models.Favorite
    relation_type = "favorite"
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Ajouter une pensée aux favoris",
        operation_description="Permet d'ajouter une pensée aux favoris.",
        responses={
            201: openapi.Response(description="Pensée ajoutée aux favoris avec succès."),
            400: openapi.Response(description="Vous avez déjà ajouté cette pensée aux favoris."),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class FavoriteCitationListView(generics.ListAPIView):
    """
    Vue pour lister les citations favorites de l'utilisateur.
    """
    serializer_class = inspira_serializers.CitationListSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Liste des citations favorites",
        operation_description="Récupère toutes les citations favorites de l'utilisateur connecté.",
        responses={
            200: openapi.Response(
                description="Liste des citations favorites récupérée avec succès",
                schema=inspira_serializers.CitationListSerializer
            ),
            401: openapi.Response(description="Authentification requise.")
        }
    )

    def get_queryset(self):
        # Récupérer le type de contenu pour Citation
        citation_content_type = ContentType.objects.get_for_model(inspira_models.Citation)

        # Obtenir les IDs des favoris correspondant aux citations
        favorite_citation_ids = inspira_models.Favorite.objects.filter(
            user=self.request.user,
            content_type=citation_content_type
        ).values_list('object_id', flat=True)

        # Retourner les citations favorites
        return inspira_models.Citation.objects.filter(id__in=favorite_citation_ids)
    
    @swagger_auto_schema(
        operation_summary="Liste des citations favorites",
        operation_description="Récupère toutes les citations favorites de l'utilisateur connecté.",
        responses={
            200: openapi.Response(
                description="Liste des citations favorites récupérée avec succès",
                schema=inspira_serializers.CitationListSerializer
            ),
            401: openapi.Response(description="Authentification requise.")
        }
    )
    def list(self, request, *args, **kwargs):
        """
        Récupère et renvoie les citations favorites de l'utilisateur.
        """
        # Obtenir les citations favorites
        citations = self.get_queryset()

        # Sérialiser les données
        serializer = inspira_serializers.CitationListSerializer(citations, many=True)

        return Response(serializer.data)


class FavoriteThoughtListView(generics.ListAPIView):
    """
    Vue pour lister les pensées favorites de l'utilisateur.
    """
    serializer_class = inspira_serializers.ThoughtListSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Liste des pensées favorites",
        operation_description="Récupère toutes les pensées favorites de l'utilisateur connecté.",
        responses={
            200: openapi.Response(
                description="Liste des pensées favorites récupérée avec succès",
                schema=inspira_serializers.ThoughtListSerializer
            ),
            401: openapi.Response(description="Authentification requise.")
        }
    )

    def get_queryset(self):
        # Récupérer le type de contenu pour Thought
        thought_content_type = ContentType.objects.get_for_model(inspira_models.Thought)

        # Obtenir les IDs des favoris correspondant aux pensées
        favorite_thought_ids = inspira_models.Favorite.objects.filter(
            user=self.request.user,
            content_type=thought_content_type
        ).values_list('object_id', flat=True)

        # Retourner les pensées favorites
        return inspira_models.Thought.objects.filter(id__in=favorite_thought_ids)
    
    @swagger_auto_schema(
        operation_summary="Liste des pensées favorites",
        operation_description="Récupère toutes les pensées favorites de l'utilisateur connecté.",
        responses={
            200: openapi.Response(
                description="Liste des pensées favorites récupérée avec succès",
                schema=inspira_serializers.ThoughtListSerializer
            ),
            401: openapi.Response(description="Authentification requise.")
        }
    )
    def list(self, request, *args, **kwargs):
        """
        Récupère et renvoie les pensées favorites de l'utilisateur.
        """
        # Obtenir les pensées favorites
        thoughts = self.get_queryset()

        # Sérialiser les données
        serializer = inspira_serializers.ThoughtListSerializer(thoughts, many=True)

        return Response(serializer.data)
    

class FavoriteCitationsAndThoughtsByCategoryView(generics.ListAPIView):
    """
    Vue pour lister les citations et pensées favorites de l'utilisateur dans une catégorie donnée.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Liste des citations et pensées favorites par catégorie",
        operation_description="Récupère toutes les citations et pensées favorites de l'utilisateur connecté dans une catégorie donnée.",
        responses={
            200: openapi.Response(
                description="Liste des citations et pensées favorites récupérée avec succès",
                schema={
                    "citations": inspira_serializers.CitationListSerializer,
                    "thoughts": inspira_serializers.ThoughtListSerializer
                }
            ),
            401: openapi.Response(description="Authentification requise.")
        }
    )

    def get_queryset(self):
        # Récupérer la catégorie à partir du slug
        category_slug = self.kwargs.get('category_slug')
        category = inspira_models.Category.objects.filter(slug=category_slug).first()

        if not category:
            return []

        # Récupérer les types de contenu
        citation_content_type = ContentType.objects.get_for_model(inspira_models.Citation)
        thought_content_type = ContentType.objects.get_for_model(inspira_models.Thought)

        # Obtenir les IDs des favoris pour cette catégorie
        favorite_citation_ids = inspira_models.Favorite.objects.filter(
            user=self.request.user,
            content_type=citation_content_type
        ).values_list('object_id', flat=True)

        favorite_thought_ids = inspira_models.Favorite.objects.filter(
            user=self.request.user,
            content_type=thought_content_type
        ).values_list('object_id', flat=True)

        # Filtrer les citations et pensées dans la catégorie
        citations = inspira_models.Citation.objects.filter(id__in=favorite_citation_ids, category=category)
        thoughts = inspira_models.Thought.objects.filter(id__in=favorite_thought_ids, category=category)

        # Retourner les résultats sous forme de liste (pas un QuerySet combiné)
        return {
            'citations': citations,
            'thoughts': thoughts
        }
    
    @swagger_auto_schema(
        operation_summary="Liste des citations et pensées favorites par catégorie",
        operation_description="Récupère toutes les citations et pensées favorites de l'utilisateur connecté dans une catégorie donnée.",
        responses={
            200: openapi.Response(
                description="Liste des citations et pensées favorites récupérée avec succès",
                schema={
                    "citations": inspira_serializers.CitationListSerializer,
                    "thoughts": inspira_serializers.ThoughtListSerializer
                }
            ),
            401: openapi.Response(description="Authentification requise.")
        }
    )

    def list(self, request, *args, **kwargs):
        """
        Sérialiser et renvoyer les citations et pensées favorites dans la catégorie spécifiée.
        """
        # Obtenir les résultats des citations et pensées
        results = self.get_queryset()
        citations = results['citations']
        thoughts = results['thoughts']

        # Sérialiser les données
        citation_serializer = inspira_serializers.CitationListSerializer(citations, many=True)
        thought_serializer = inspira_serializers.ThoughtListSerializer(thoughts, many=True)

        # Fusionner les résultats dans un dictionnaire
        return Response({
            'citations': citation_serializer.data,
            'thoughts': thought_serializer.data
        })
    
class AboutView(APIView):
    """
    Vue pour afficher les informations sur l'application.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Informations sur l'application",
        operation_description="Récupère les informations sur l'application.",
        responses={
            200: openapi.Response(
                description="Informations sur l'application récupérées avec succès",
                schema=inspira_serializers.AboutSerializer
            ),
            404: openapi.Response(description="Informations introuvables.") 
        }   
    )

    def get(self, request, *args, **kwargs):
        about = inspira_models.About.objects.first()
        if not about:
            raise Http404("About information not found.")
        serializer = inspira_serializers.AboutSerializer(about)
        return Response(serializer.data)
