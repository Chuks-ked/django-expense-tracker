from . import views
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('validate-username/',csrf_exempt(views.UsernameValidation.as_view()), name='validate-username'),

    path('validate-email/', csrf_exempt(views.EmailValidation.as_view()), name='validate_email'),

    path('acitvate/<uidb64>/<token>/', views.VerificationView.as_view(), name='activate'),

    path('reset/<uidb64>/<token>/', views.CompletePasswordReset.as_view(), name='reset-user-password'),

    path('reset-link/', views.RequestPasswordResetEmail.as_view(), name='reset-link')
    
]
