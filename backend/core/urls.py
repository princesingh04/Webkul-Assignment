from django.urls import path
from .views import SignupView, LoginView, ProfileView, PostListCreateView, PostDeleteView,  PostReactView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # posts
    path('posts/', PostListCreateView.as_view(), name='posts'),
    path('posts/<int:pk>/', PostDeleteView.as_view(), name='delete-post'),
    path('posts/<int:pk>/react/', PostReactView.as_view(), name='react-post'),
]
