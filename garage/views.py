from django.shortcuts import render, redirect
from .models import Reparation, Client, Vehicule
from .forms import ClientForm, VehiculeForm, ReparationForm

def index(request):
    if request.method == 'POST':
        if 'add_client' in request.POST:
            form = ClientForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('index')
        elif 'add_vehicule' in request.POST:
            form = VehiculeForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('index')
        elif 'add_reparation' in request.POST:
            form = ReparationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('index')

    reparations = Reparation.objects.all().select_related('vehicule')
    clients = Client.objects.all()
    vehicules = Vehicule.objects.all()

    context = {
        'reparations': reparations,
        'total_clients': clients.count(),
        'total_vehicules': vehicules.count(),
        'client_form': ClientForm(),
        'vehicule_form': VehiculeForm(),
        'reparation_form': ReparationForm(),
    }
    return render(request, 'garage/index.html', context)