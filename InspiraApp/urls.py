from django.urls import path
import InspiraApp.views as inspira_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Authentication
    path('user/token/', inspira_views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', inspira_views.RegisterView.as_view(), name='register'),
    path('user/profile/<user_id>/', inspira_views.ProfileView.as_view(), name='profile'),
    path('user/password-reset/<email>', inspira_views.PasswordEmailVerify.as_view(), name='password-reset'),
    path('user/password-change/', inspira_views.PasswordChangeView.as_view(), name='password-reset-confirm'),
    
    # Inspirations
    path('inspiration/categories/', inspira_views.CategoryListView.as_view(), name='category-list'),
    path('inspiration/categories/<slug:slug>/', inspira_views.CategoryDetailView.as_view(), name='category-detail'),
    path('inspiration/citations/', inspira_views.CitationListView.as_view(), name='citation-list'),
    path('inspiration/citations/<slug:slug>/', inspira_views.CitationDetailView.as_view(), name='citation-detail'),
    path('inspiration/thoughts/', inspira_views.ThoughtListView.as_view(), name='thought-list'),
    path('inspiration/thoughts/<slug:slug>/', inspira_views.ThoughtDetailView.as_view(), name='thought-detail'),
    path('inspiration/likes/<user_id>/<citation_id>/', inspira_views.LikeCitationView.as_view(), name='like-list'),
    path('inspiration/favorite/<user_id>/<citation_id>', inspira_views.FavoriteCitationView.as_view(), name='like-list'),
    path('inspiration/likes/<user_id>/<thought_id>/', inspira_views.LikeThoughtView.as_view(), name='like-list'),
    path('inspiration/favorite/<user_id>/<thought_id>', inspira_views.FavoriteThoughtView.as_view(), name='like-list'),

]