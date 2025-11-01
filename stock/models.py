from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from django.core.exceptions import ValidationError

class Fournisseur(models.Model):
    """
    Modèle représentant un fournisseur de produits
    """
    nom = models.CharField(max_length=100, verbose_name="Nom du fournisseur")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email", blank=True)
    adresse = models.TextField(verbose_name="Adresse", blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom

class Categorie(models.Model):
    """
    Modèle pour catégoriser les produits
    """
    nom = models.CharField(max_length=50, verbose_name="Nom de la catégorie")
    description = models.TextField(verbose_name="Description", blank=True)
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
    
    def __str__(self):
        return self.nom

class Produit(models.Model):
    """
    Modèle représentant un produit dans le stock
    """
    nom = models.CharField(max_length=100, verbose_name="Nom du produit")
    description = models.TextField(verbose_name="Description", blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, verbose_name="Catégorie")
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, verbose_name="Fournisseur")
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix d'achat")
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de vente")
    stock_minimum = models.IntegerField(default=0, verbose_name="Stock minimum d'alerte")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} (Ref: {self.id})"
    
    @property
    def quantite_stock(self):
        """
        Calcule la quantité actuelle en stock - VERSION SIMPLIFIÉE
        """
        # Calculer la somme des entrées
        entrees = MouvementStock.objects.filter(
            produit=self, 
            type_mouvement='entree'
        ).aggregate(total=Sum('quantite'))['total'] or 0
        
        # Calculer la somme des sorties
        sorties = MouvementStock.objects.filter(
            produit=self, 
            type_mouvement='sortie'
        ).aggregate(total=Sum('quantite'))['total'] or 0
        
        # Stock = entrées - sorties
        return entrees - sorties
    
    @property
    def valeur_stock(self):
        """
        Calcule la valeur totale du stock pour ce produit
        """
        return self.quantite_stock * self.prix_achat
    
    @property
    def statut_stock(self):
        """
        Retourne le statut du stock (Normal, Faible, Rupture)
        """
        quantite = self.quantite_stock
        if quantite == 0:
            return "rupture"
        elif quantite <= self.stock_minimum:
            return "faible"
        else:
            return "normal"

class MouvementStock(models.Model):
    """
    Modèle représentant un mouvement de stock (entrée/sortie)
    """
    TYPE_MOUVEMENT_CHOICES = [
        ('entree', 'Entrée en stock'),
        ('sortie', 'Sortie de stock'),
    ]
    
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, verbose_name="Produit")
    type_mouvement = models.CharField(max_length=10, choices=TYPE_MOUVEMENT_CHOICES, verbose_name="Type de mouvement")
    quantite = models.IntegerField(verbose_name="Quantité")
    date_mouvement = models.DateTimeField(auto_now_add=True, verbose_name="Date du mouvement")
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    notes = models.TextField(verbose_name="Notes", blank=True)
    
    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-date_mouvement']
    
    def __str__(self):
        type_str = "Entrée" if self.type_mouvement == 'entree' else "Sortie"
        return f"{type_str} - {self.produit.nom} - {self.quantite}"
    
    def clean(self):
        """
        Validation pour empêcher les sorties avec stock insuffisant
        """
        if self.type_mouvement == 'sortie' and self.produit:
            stock_actuel = self.produit.quantite_stock
            if self.quantite > stock_actuel:
                raise ValidationError(
                    f"Stock insuffisant. Stock actuel: {stock_actuel}, "
                    f"quantité demandée: {self.quantite}"
                )
    
    def save(self, *args, **kwargs):
        """
        Surcharge de save pour appeler la validation
        """
        self.clean()
        super().save(*args, **kwargs)

# Signals pour mettre à jour les statistiques ou effectuer des validations
@receiver(post_save, sender=MouvementStock)
def verifier_stock_apres_mouvement(sender, instance, **kwargs):
    """
    Signal pour vérifier le niveau de stock après chaque mouvement
    et logger si nécessaire
    """
    produit = instance.produit
    quantite_actuelle = produit.quantite_stock
    
    # Ici on pourrait ajouter une notification si le stock est faible
    if quantite_actuelle <= produit.stock_minimum:
        print(f"ALERTE: Stock faible pour {produit.nom} - Quantité: {quantite_actuelle}")