from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

def register(request):
    """
    Vue pour l'inscription des utilisateurs
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Compte créé pour {username}! Vous pouvez maintenant vous connecter.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})