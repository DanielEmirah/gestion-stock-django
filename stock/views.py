from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from .models import Produit, MouvementStock, Fournisseur, Categorie

@login_required
def dashboard(request):
    """
    Vue pour le tableau de bord principal avec les statistiques
    """
    # Statistiques principales
    total_produits = Produit.objects.count()
    total_fournisseurs = Fournisseur.objects.count()
    
    # Calcul de la valeur totale du stock
    produits = Produit.objects.all()
    valeur_totale_stock = sum(prod.valeur_stock for prod in produits)
    
    # Mouvements récents (7 derniers jours)
    date_limite = timezone.now() - timedelta(days=7)
    mouvements_recents = MouvementStock.objects.filter(
        date_mouvement__gte=date_limite
    ).select_related('produit').order_by('-date_mouvement')[:10]
    
    # Produits avec stock faible
    produits_stock_faible = [
        prod for prod in Produit.objects.all() 
        if prod.statut_stock in ['faible', 'rupture']
    ]
    
    # Statistiques des mouvements
    mouvements_entree = MouvementStock.objects.filter(
        type_mouvement='entree',
        date_mouvement__gte=date_limite
    ).count()
    
    mouvements_sortie = MouvementStock.objects.filter(
        type_mouvement='sortie',
        date_mouvement__gte=date_limite
    ).count()
    
    context = {
        'total_produits': total_produits,
        'total_fournisseurs': total_fournisseurs,
        'valeur_totale_stock': valeur_totale_stock,
        'mouvements_recents': mouvements_recents,
        'produits_stock_faible': produits_stock_faible,
        'mouvements_entree': mouvements_entree,
        'mouvements_sortie': mouvements_sortie,
    }
    
    return render(request, 'stock/dashboard.html', context)

@login_required
def liste_produits(request):
    """
    Vue pour lister tous les produits avec leur statut de stock
    """
    produits = Produit.objects.all().select_related('categorie', 'fournisseur')
    
    # Filtrage par statut de stock
    statut_filter = request.GET.get('statut')
    if statut_filter:
        # Filtrage en mémoire car c'est une propriété Python
        produits = [p for p in produits if p.statut_stock == statut_filter]
    
    # Compter les alertes
    produits_stock_faible_count = len([p for p in produits if p.statut_stock in ['faible', 'rupture']])
    
    context = {
        'produits': produits,
        'statut_filter': statut_filter,
        'produits_stock_faible_count': produits_stock_faible_count,
    }
    return render(request, 'stock/liste_produits.html', context)

@login_required
def mouvement_stock(request, produit_id=None):
    """
    Vue pour gérer les mouvements de stock (entrées/sorties)
    """
    produit = None
    if produit_id:
        produit = get_object_or_404(Produit, id=produit_id)
    
    if request.method == 'POST':
        produit_id = request.POST.get('produit')
        type_mouvement = request.POST.get('type_mouvement')
        quantite = request.POST.get('quantite')
        notes = request.POST.get('notes', '')
        
        try:
            produit = Produit.objects.get(id=produit_id)
            quantite = int(quantite)
            
            if quantite <= 0:
                messages.error(request, "La quantité doit être positive.")
            elif type_mouvement == 'sortie':
                # Vérifier le stock AVANT de créer le mouvement
                stock_actuel = produit.quantite_stock
                if quantite > stock_actuel:
                    messages.error(
                        request, 
                        f"Stock insuffisant. Stock actuel: {stock_actuel}, "
                        f"quantité demandée: {quantite}"
                    )
                else:
                    # Créer le mouvement de sortie
                    MouvementStock.objects.create(
                        produit=produit,
                        type_mouvement=type_mouvement,
                        quantite=quantite,
                        utilisateur=request.user,
                        notes=notes
                    )
                    
                    nouveau_stock = produit.quantite_stock
                    messages.success(
                        request, 
                        f"{quantite} unité(s) retirée(s) de {produit.nom}. "
                        f"Nouveau stock: {nouveau_stock}"
                    )
                    return redirect('stock:liste_produits')
            else:
                # Mouvement d'entrée
                MouvementStock.objects.create(
                    produit=produit,
                    type_mouvement=type_mouvement,
                    quantite=quantite,
                    utilisateur=request.user,
                    notes=notes
                )
                
                nouveau_stock = produit.quantite_stock
                messages.success(
                    request, 
                    f"{quantite} unité(s) ajoutée(s) à {produit.nom}. "
                    f"Nouveau stock: {nouveau_stock}"
                )
                return redirect('stock:liste_produits')
                
        except (Produit.DoesNotExist, ValueError):
            messages.error(request, "Erreur dans les données soumises.")
    
    produits = Produit.objects.all()
    context = {
        'produits': produits,
        'produit_selectionne': produit,
    }
    return render(request, 'stock/mouvement_stock.html', context)

@login_required
def historique_mouvements(request):
    """
    Vue pour afficher l'historique complet des mouvements
    """
    mouvements = MouvementStock.objects.all().select_related(
        'produit', 'utilisateur'
    ).order_by('-date_mouvement')
    
    # Filtrage
    type_filter = request.GET.get('type')
    if type_filter:
        mouvements = mouvements.filter(type_mouvement=type_filter)
    
    produit_filter = request.GET.get('produit')
    if produit_filter:
        mouvements = mouvements.filter(produit_id=produit_filter)
    
    # Pagination
    paginator = Paginator(mouvements, 25)  # 25 mouvements par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    mouvements_entrees = mouvements.filter(type_mouvement='entree').count()
    mouvements_sorties = mouvements.filter(type_mouvement='sortie').count()
    
    context = {
        'mouvements': page_obj,
        'produits': Produit.objects.all(),
        'mouvements_entrees': mouvements_entrees,
        'mouvements_sorties': mouvements_sorties,
    }
    return render(request, 'stock/historique_mouvements.html', context)