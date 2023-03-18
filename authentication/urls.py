from . import views
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register/', views.RegistrationView.as_view(), name='register'),

    path('validate-username/',csrf_exempt(views.UsernameValidation.as_view()), name='validate-username')
    
]
