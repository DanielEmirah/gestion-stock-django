from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from utilisateur import views as user_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # URLs d'authentification
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        redirect_authenticated_user=True
    ), name='login'),  # Nom simple 'login'
    
    path('logout/', auth_views.LogoutView.as_view(
        template_name='users/logout.html',
        next_page='login'
    ), name='logout'),
    
    path('register/', user_views.register, name='register'),
    
    # URLs de l'application stock
    path('', include(('stock.urls', 'stock'), namespace='stock')),
]

# Servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)