from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, EquipmentForm, AffectationForm, DemandeEquipementForm, DemandeInterventionForm, LoginForm, UserUpdateForm
from .models import Equipment, Affectation, DemandeEquipement, DemandeIntervention, Notification
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q

def is_admin(user):
    return user.is_superuser

def is_gestionnaire(user):
    return user.is_staff and not user.is_superuser

def is_fonctionnaire(user):
    return not user.is_staff and not user.is_superuser

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    form.add_error(None, "Mot de passe incorrect.")
            except User.DoesNotExist:
                form.add_error('email', "Aucun utilisateur trouvé avec cet email.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    return render(request, 'home.html')

@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data['role']
            user.email = form.cleaned_data['email']
            if role == 'admin':
                user.is_superuser = True
                user.is_staff = True
            elif role == 'gestionnaire':
                user.is_staff = True
            user.save()
            return redirect('user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'user_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def modify_user(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data['role']
            user.is_superuser = role == 'admin'
            user.is_staff = role in ['admin', 'gestionnaire']
            user.email = form.cleaned_data['email']
            user.save()
            return redirect('user_list')
    else:
        form = UserUpdateForm(instance=user, initial={'role': 'admin' if user.is_superuser else 'gestionnaire' if user.is_staff else 'fonctionnaire'})
    return render(request, 'modify_user.html', {'form': form, 'user': user})

@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    return render(request, 'user_delete.html', {'user': user})


@login_required
@user_passes_test(lambda u: is_admin(u) or is_gestionnaire(u))
def gestion_equipement(request):
    equipements = Equipment.objects.all()
    return render(request, 'gestion_equipement.html', {'equipements': equipements})

@login_required
@user_passes_test(lambda u: is_admin(u) or is_gestionnaire(u))
def gestion_affectation(request):
    affectations = Affectation.objects.all().order_by('-date_affectation')
    return render(request, 'gestion_affectation.html', {'affectations': affectations})

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})

@login_required
def dashboard(request):
    if is_admin(request.user) or is_gestionnaire(request.user):
        return redirect('stock')
    return redirect('mes_equipements')

@login_required
@user_passes_test(lambda u: is_admin(u) or is_gestionnaire(u))
def stock(request):
    type_filter = request.GET.get('type', '')
    sous_type_filter = request.GET.get('sous_type', '')
    emplacement_filter = request.GET.get('emplacement', '')
    affecte_filter = request.GET.get('affecte', '')

    equipements = Equipment.objects.all()
    if type_filter:
        equipements = equipements.filter(type__icontains=type_filter)
    if sous_type_filter:
        equipements = equipements.filter(sous_type__icontains=sous_type_filter)
    if emplacement_filter:
        equipements = equipements.filter(emplacement__icontains=emplacement_filter)
    if affecte_filter:
        equipements = equipements.filter(affecte=affecte_filter == 'True')

    return render(request, 'stock.html', {
        'equipements': equipements,
        'type_filter': type_filter,
        'sous_type_filter': sous_type_filter,
        'emplacement_filter': emplacement_filter,
        'affecte_filter': affecte_filter,
    })

@login_required
@user_passes_test(lambda u: is_admin(u) or is_gestionnaire(u))
def equipment_create(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stock')
    else:
        form = EquipmentForm()
    return render(request, 'equipment_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: is_admin(u) or is_gestionnaire(u))
def equipment_update(request, pk):
    equipment = Equipment.objects.get(pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            return redirect('stock')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'equipment_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: is_admin(u) or is_gestionnaire(u))
def equipment_delete(request, pk):
    equipment = Equipment.objects.get(pk=pk)
    if request.method == 'POST':
        equipment.delete()
        return redirect('stock')
    return render(request, 'equipment_delete.html', {'equipment': equipment})

@login_required
@user_passes_test(lambda u: is_admin(u) or is_gestionnaire(u))
def affectation_create(request):
    if request.method == 'POST':
        form = AffectationForm(request.POST)
        if form.is_valid():
            affectation = form.save(commit=False)
            affectation.equipement.affecte = True
            affectation.equipement.save()
            affectation.save()
            Notification.objects.create(
                message=f"Nouvelle affectation: {affectation.equipement} à {affectation.fonctionnaire}",
                personne=User.objects.filter(is_staff=True).first()
            )
            return redirect('notifications')
    else:
        form = AffectationForm()
    return render(request, 'affectation_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: is_admin(u) or is_gestionnaire(u))
def affectation_update(request, pk):
    affectation = Affectation.objects.get(pk=pk)
    if request.method == 'POST':
        form = AffectationForm(request.POST, instance=affectation)
        if form.is_valid():
            old_equipment = affectation.equipement
            affectation = form.save(commit=False)
            if old_equipment != affectation.equipement:
                old_equipment.affecte = False
                old_equipment.save()
                affectation.equipement.affecte = True
                affectation.equipement.save()
            affectation.save()
            Notification.objects.create(
                message=f"Affectation modifiée: {affectation.equipement} à {affectation.fonctionnaire}",
                personne=User.objects.filter(is_staff=True).first()
            )
            return redirect('notifications')
    else:
        form = AffectationForm(instance=affectation)
    return render(request, 'affectation_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: is_admin(u) or is_gestionnaire(u))
def affectation_return(request, pk):
    affectation = Affectation.objects.get(pk=pk)
    if request.method == 'POST':
        affectation.date_retour = timezone.now()
        affectation.equipement.affecte = False
        # Find the related DemandeEquipement to get the quantity
        try:
            demande = DemandeEquipement.objects.get(
                equipements=affectation.equipement,
                demandeur=affectation.fonctionnaire,
                service=affectation.service,
                etat='Validée'
            )
            affectation.equipement.quantity += demande.quantity
        except DemandeEquipement.DoesNotExist:
            affectation.equipement.quantity += 1  # Fallback: assume 1 if no demande found
        affectation.equipement.save()
        affectation.save()
        Notification.objects.create(
            message=f"Retour d'affectation: {affectation.equipement} par {affectation.fonctionnaire}",
            personne=User.objects.filter(is_staff=True).first()
        )
        return redirect('gestion_affectation')
    return render(request, 'affectation_return.html', {'affectation': affectation})

@login_required
@user_passes_test(lambda u: is_admin(u) or is_gestionnaire(u))
def notifications(request):
    equipement_demandes = DemandeEquipement.objects.all().order_by('-date_creation')
    intervention_demandes = DemandeIntervention.objects.all().order_by('-date')
    notifications = Notification.objects.filter(personne=request.user).order_by('-date')

    # Filters for DemandeEquipement
    etat_equipement = request.GET.get('etat_equipement', '')
    demandeur_equipement = request.GET.get('demandeur_equipement', '')
    date_equipement = request.GET.get('date_equipement', '')

    if etat_equipement:
        equipement_demandes = equipement_demandes.filter(etat=etat_equipement)
    if demandeur_equipement:
        equipement_demandes = equipement_demandes.filter(demandeur__email__icontains=demandeur_equipement)
    if date_equipement:
        equipement_demandes = equipement_demandes.filter(date_creation__date=date_equipement)

    # Filters for DemandeIntervention
    demandeur_intervention = request.GET.get('demandeur_intervention', '')
    date_intervention = request.GET.get('date_intervention', '')

    if demandeur_intervention:
        intervention_demandes = intervention_demandes.filter(demandeur__email__icontains=demandeur_intervention)
    if date_intervention:
        intervention_demandes = intervention_demandes.filter(date__date=date_intervention)

    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            Notification.objects.filter(pk=notification_id, personne=request.user).update(read=True)
        return redirect('notifications')

    return render(request, 'notifications.html', {
        'equipement_demandes': equipement_demandes,
        'intervention_demandes': intervention_demandes,
        'notifications': notifications,
        'etat_equipement': etat_equipement,
        'demandeur_equipement': demandeur_equipement,
        'date_equipement': date_equipement,
        'demandeur_intervention': demandeur_intervention,
        'date_intervention': date_intervention,
    })

@login_required
@user_passes_test(is_fonctionnaire)
def mes_equipements(request):
    affectations = Affectation.objects.filter(fonctionnaire=request.user, date_retour__isnull=True)
    return render(request, 'mes_equipements.html', {'affectations': affectations})

@login_required
@user_passes_test(is_fonctionnaire)
def demande_equipement_create(request):
    if request.method == 'POST':
        form = DemandeEquipementForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.demandeur = request.user
            demande.save()
            form.save_m2m()
            Notification.objects.create(
                message=f"Nouvelle demande d'équipement: {demande.objet} par {demande.demandeur}",
                personne=User.objects.filter(is_staff=True).first()
            )
            return redirect('mes_equipements')
    else:
        form = DemandeEquipementForm()
    return render(request, 'demande_equipement_form.html', {'form': form})

@login_required
@user_passes_test(is_fonctionnaire)
def demande_intervention_create(request):
    if request.method == 'POST':
        form = DemandeInterventionForm(request.POST)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.demandeur = request.user
            demande.save()
            Notification.objects.create(
                message=f"Nouvelle demande d'intervention: {demande.description[:50]} par {demande.demandeur}",
                personne=User.objects.filter(is_staff=True).first()
            )
            return redirect('mes_equipements')
    else:
        form = DemandeInterventionForm()
    return render(request, 'demande_intervention_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: is_admin(u) or is_gestionnaire(u))
def demande_equipement_approve(request, pk):
    demande = DemandeEquipement.objects.get(pk=pk)
    if request.method == 'POST':
        etat = request.POST.get('etat')
        demande.etat = etat
        if etat == 'Validée':
            for equipement in demande.equipements.all():
                if equipement.quantity >= demande.quantity:
                    equipement.affecte = True
                    equipement.quantity -= demande.quantity
                    equipement.save()
                    Affectation.objects.create(
                        equipement=equipement,
                        fonctionnaire=demande.demandeur,
                        service=demande.service
                    )
        elif etat == 'Refusée':
            demande.equipements.clear()
        demande.save()
        Notification.objects.create(
            message=f"Demande d'équipement {demande.id} {etat} pour {demande.demandeur}",
            personne=demande.demandeur
        )
        return redirect('notifications')
    return render(request, 'demande_equipement_approve.html', {'demande': demande})
