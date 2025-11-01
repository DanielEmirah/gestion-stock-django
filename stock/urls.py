from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('produits/', views.liste_produits, name='liste_produits'),
    path('mouvement/', views.mouvement_stock, name='mouvement_stock'),
    path('mouvement/<int:produit_id>/', views.mouvement_stock, name='mouvement_stock_produit'),
    path('historique/', views.historique_mouvements, name='historique_mouvements'),
]