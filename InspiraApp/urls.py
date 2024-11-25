from django.urls import path
import InspiraApp.views as inspira_views

urlpatterns = [
    path('categories/', inspira_views.CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', inspira_views.CategoryDetailView.as_view(), name='category-detail'),
    path('citations/', inspira_views.CitationListView.as_view(), name='citation-list'),
    path('citations/<slug:slug>/', inspira_views.CitationDetailView.as_view(), name='citation-detail'),
    path('thoughts/', inspira_views.ThoughtListView.as_view(), name='thought-list'),
    path('thoughts/<slug:slug>/', inspira_views.ThoughtDetailView.as_view(), name='thought-detail'),
]