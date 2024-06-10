from django.urls import path,include

from . import views
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register(r'groups', views.GroupViewSet, basename='user_groups')
router.register(r'', views.UserViewSet)


app_name = "users"
urlpatterns = [
    # path('register/', views.RegisterApi.as_view()),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('set-account/', views.SetAccountView.as_view(), name='account_signup'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('reset-password/request/', views.PasswordResetRequestView.as_view(), name="password_reset_request"),
    path('reset-password/confirm/', views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('', include(router.urls)),
]
