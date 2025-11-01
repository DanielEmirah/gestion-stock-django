from django.contrib import admin
from django.utils.html import format_html
from .models import Produit, Fournisseur, Categorie, MouvementStock

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle Categorie
    """
    list_display = ['nom', 'description']
    search_fields = ['nom']
    list_per_page = 20

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle Fournisseur
    """
    list_display = ['nom', 'telephone', 'email', 'date_creation']
    search_fields = ['nom', 'email']
    list_filter = ['date_creation']
    list_per_page = 20

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 
        'categorie', 
        'fournisseur', 
        'prix_achat', 
        'prix_vente', 
        'quantite_stock',
        'statut_stock_coloré',
        'valeur_stock'
    ]
    
    list_filter = ['categorie', 'fournisseur', 'date_creation']
    search_fields = ['nom', 'description']
    readonly_fields = ['date_creation']
    list_per_page = 25
    
    def statut_stock_coloré(self, obj):
        """
        Affiche le statut du stock avec une couleur
        """
        statut = obj.statut_stock
        if statut == "normal":
            return format_html('<span style="color: green;">● Normal</span>')
        elif statut == "faible":
            return format_html('<span style="color: orange;">● Faible</span>')
        else:
            return format_html('<span style="color: red;">● Rupture</span>')
    
    statut_stock_coloré.short_description = "Statut Stock"
    
    def valeur_stock(self, obj):
        """
        Affiche la valeur du stock formatée
        """
        return f"{obj.valeur_stock:.2f} €"
    
    valeur_stock.short_description = "Valeur Stock"

@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    """
    Administration personnalisée pour le modèle MouvementStock
    """
    list_display = [
        'produit', 
        'type_mouvement_coloré', 
        'quantite', 
        'date_mouvement', 
        'utilisateur'
    ]
    
    list_filter = ['type_mouvement', 'date_mouvement', 'utilisateur']
    search_fields = ['produit__nom', 'notes']
    readonly_fields = ['date_mouvement']
    list_per_page = 30
    
    def type_mouvement_coloré(self, obj):
        """
        Affiche le type de mouvement avec une couleur
        """
        if obj.type_mouvement == 'entree':
            return format_html('<span style="color: green;">↑ Entrée</span>')
        else:
            return format_html('<span style="color: red;">↓ Sortie</span>')
    
    type_mouvement_coloré.short_description = "Type Mouvement"
    
    def save_model(self, request, obj, form, change):
        """
        S'assure que l'utilisateur est enregistré comme créateur du mouvement
        """
        if not obj.pk:
            obj.utilisateur = request.user
        super().save_model(request, obj, form, change)