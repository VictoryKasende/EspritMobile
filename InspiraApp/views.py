from django.shortcuts import render
from rest_framework.generics import RetrieveAPIView, ListAPIView
import InspiraApp.models as inspira_models
import InspiraApp.serializers as inspira_serializers

class CategoryListView(ListAPIView):
    """
    Vue pour lister toutes les catégories.
    """
    queryset = inspira_models.Category.objects.all()
    serializer_class = inspira_serializers.CategoryListSerializer


class CategoryDetailView(RetrieveAPIView):
    """
    Vue pour afficher les détails d'une catégorie.
    """
    queryset = inspira_models.Category.objects.all()
    serializer_class = inspira_serializers.CategoryDetailSerializer
    lookup_field = "slug"

class CitationListView(ListAPIView):
    """
    Vue pour lister toutes les citations.
    """
    queryset = inspira_models.Citation.objects.filter(active=True)
    serializer_class = inspira_serializers.CitationListSerializer

class CitationDetailView(RetrieveAPIView):
    """
    Vue pour afficher les détails d'une citation.
    """
    queryset = inspira_models.Citation.objects.filter(active=True)
    serializer_class = inspira_serializers.CitationDetailSerializer
    lookup_field = "slug"

class ThoughtListView(ListAPIView):
    """
    Vue pour lister toutes les pensées.
    """
    queryset = inspira_models.Thought.objects.filter(active=True)
    serializer_class = inspira_serializers.ThoughtListSerializer

class ThoughtDetailView(RetrieveAPIView):
    """
    Vue pour afficher les détails d'une pensée.
    """
    queryset = inspira_models.Thought.objects.filter(active=True)
    serializer_class = inspira_serializers.ThoughtDetailSerializer
    lookup_field = "slug"




