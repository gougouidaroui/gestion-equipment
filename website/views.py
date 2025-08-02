from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import EquipmentForm, MaterialTypeForm, MaterialRequestForm, SignUpForm, LoginForm
from .models import Equipment, MaterialRequest, AssignmentHistory, MaterialType
from django.contrib.auth.models import User
from django.utils import timezone

def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def home(request):
    if request.user.is_staff:
        equipements = Equipment.objects.all()
        demandes = MaterialRequest.objects.filter(history=False)
    else:
        equipements = Equipment.objects.filter(etat='Disponible')
        demandes = MaterialRequest.objects.filter(demandeur=request.user, history=False)
    return render(request, 'home.html', {'equipements': equipements, 'demandes': demandes})

@login_required
@user_passes_test(lambda u: u.is_staff)
def equipment_create(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EquipmentForm()
    return render(request, 'equipment_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def equipment_update(request, pk):
    equipment = Equipment.objects.get(pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EquipmentForm(instance=equipment)
    return render(request, 'equipment_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def equipment_delete(request, pk):
    equipment = Equipment.objects.get(pk=pk)
    if request.method == 'POST':
        equipment.delete()
        return redirect('home')
    return render(request, 'equipment_form.html', {'form': None, 'equipment': equipment})

@login_required
@user_passes_test(lambda u: u.is_staff)
def material_type_create(request):
    if request.method == 'POST':
        form = MaterialTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = MaterialTypeForm()
    return render(request, 'material_type_form.html', {'form': form})

@login_required
def request_create(request):
    if request.method == 'POST':
        form = MaterialRequestForm(request.POST, user=request.user)
        if form.is_valid():
            material_request = form.save(commit=False)
            material_request.demandeur = request.user
            material_request.etat = 'En attente'
            material_request.save()
            form.save_m2m()
            equipements = form.cleaned_data['equipements']
            types = set(equipement.type_materiel for equipement in equipements)
            material_request.types_materiel.set(types)
            return redirect('home')
    else:
        form = MaterialRequestForm(user=request.user)
    material_types = MaterialType.objects.all()
    return render(request, 'request_form.html', {'form': form, 'material_types': material_types})

@login_required
@user_passes_test(lambda u: u.is_staff)
def request_update(request, pk):
    material_request = MaterialRequest.objects.get(pk=pk)
    if request.method == 'POST':
        form = MaterialRequestForm(request.POST, instance=material_request, user=request.user)
        if form.is_valid():
            material_request.etat = form.cleaned_data['etat']
            if material_request.etat == 'Validée':
                for equipment in material_request.equipements.all():
                    equipment.etat = 'Affecté'
                    equipment.save()
                    AssignmentHistory.objects.create(
                        equipement=equipment,
                        utilisateur=material_request.demandeur,
                        demande=material_request
                    )
            elif material_request.etat == 'Refusée':
                for equipment in material_request.equipements.all():
                    equipment.etat = 'Disponible'
                    equipment.save()
                    AssignmentHistory.objects.filter(demande=material_request, retourne_le__isnull=True).update(retourne_le=timezone.now())
                material_request.equipements.clear()
            material_request.save()
            return redirect('home')
    else:
        form = MaterialRequestForm(instance=material_request, user=request.user)
    material_types = MaterialType.objects.all()
    return render(request, 'request_form.html', {'form': form, 'material_types': material_types})

@login_required
@user_passes_test(lambda u: u.is_staff)
def request_delete(request, pk):
    material_request = MaterialRequest.objects.get(pk=pk)
    if request.method == 'POST':
        for equipment in material_request.equipements.all():
            equipment.etat = 'Disponible'
            equipment.save()
            AssignmentHistory.objects.filter(demande=material_request, retourne_le__isnull=True).update(retourne_le=timezone.now())
        material_request.delete()
        return redirect('home')
    return render(request, 'request_delete.html', {'demande': material_request})

@login_required
def return_equipment(request, assignment_id):
    assignment = AssignmentHistory.objects.get(pk=assignment_id)
    if request.user == assignment.utilisateur and not assignment.retourne_le:
        if request.method == 'POST':
            assignment.retourne_le = timezone.now()
            assignment.equipement.etat = 'Disponible'
            assignment.demande.history = True
            assignment.demande.save()
            assignment.equipement.save()
            assignment.save()
            return redirect('home')
        return render(request, 'return_confirm.html', {'assignment': assignment})
    return redirect('home')

@login_required
def history_view(request):
    if request.user.is_staff:
        history = AssignmentHistory.objects.all()
    else:
        history = AssignmentHistory.objects.filter(utilisateur=request.user)
    return render(request, 'history.html', {'history': history})
