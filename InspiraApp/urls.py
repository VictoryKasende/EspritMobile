from django.urls import path
import InspiraApp.views as inspira_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication
    path('auth/token/', inspira_views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', inspira_views.RegisterView.as_view(), name='register'),
    path('auth/profile/', inspira_views.ProfileView.as_view(), name='profile'),
    path('auth/password-reset/', inspira_views.PasswordEmailVerify.as_view(), name='password-reset'),
    path('auth/password-change/', inspira_views.PasswordChangeView.as_view(), name='password-reset-confirm'),
    
    # Inspirations
    path('inspiration/categories/', inspira_views.CategoryListView.as_view(), name='category-list'),
    path('inspiration/categories/<slug:slug>/', inspira_views.CategoryDetailView.as_view(), name='category-detail'),
    path('inspiration/citations/', inspira_views.CitationListView.as_view(), name='citation-list'),
    path('inspiration/citations/<slug:slug>/', inspira_views.CitationDetailView.as_view(), name='citation-detail'),
    path('inspiration/thoughts/', inspira_views.ThoughtListView.as_view(), name='thought-list'),
    path('inspiration/thoughts/<slug:slug>/', inspira_views.ThoughtDetailView.as_view(), name='thought-detail'),

    path('inspiration/citation/<int:object_id>/likes/', inspira_views.LikeCitationView.as_view(), name='like-citation'),
    path('inspiration/citation/<int:object_id>/favorites/', inspira_views.FavoriteCitationView.as_view(), name='favorite-citation'),
    path('inspiration/thoughts/<int:object_id>/likes/', inspira_views.LikeThoughtView.as_view(), name='like-thought'),
    path('inspiration/thoughts/<int:object_id>/favorites/', inspira_views.FavoriteThoughtView.as_view(), name='favorite-thought'),
    path('inspiration/favorites/thoughts/', inspira_views.FavoriteThoughtListView.as_view(), name='favorite-thoughts-list'),
    path('inspiration/favorites/citations/', inspira_views.FavoriteCitationListView.as_view(), name='favorite-citations-list'),
    path('inspiration/favorites/category/<slug:category_slug>/', inspira_views.FavoriteCitationsAndThoughtsByCategoryView.as_view(), name='favorites-category'),
    path('inspiration/about/', inspira_views.AboutView.as_view(), name='about'),
]