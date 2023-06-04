from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', views.register, name="register"),
    # path('img/<int:pk>/', views.ProductViews.as_view()),
    # path('img/', views.ProductViews.as_view()),
    path('product/<int:pk>/', views.ProductViews.as_view()),
    path('product/', views.ProductViews.as_view()),
    path('profile/<int:pk>/', views.ProfileViews.as_view()),
    path('profile/', views.ProfileViews.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('user-id/', views.get_user_id),
    path('cart/', views.get_user_cart),
    path('cart/history/', views.get_user_cart_history),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
