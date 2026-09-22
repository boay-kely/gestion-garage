import io
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Count, Q
from django.core.paginator import Paginator
from xhtml2pdf import pisa

from .models import Reparation, Client, Vehicule, Facture
from .forms import ClientForm, VehiculeForm, ReparationForm


# --- TABLEAU DE BORD ---
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

    total_clients = Client.objects.count()
    total_vehicules = Vehicule.objects.count()
    total_reparations = Reparation.objects.count()

    clients_recents = Client.objects.order_by('-id')[:3]
    vehicules_recents = Vehicule.objects.order_by('-id')[:3]
    reparations_recentes = Reparation.objects.select_related('vehicule').order_by('-id')[:3]

    stats_statut = Reparation.objects.values('statut').annotate(total=Count('id'))
    statut_counts = {'EN_ATTENTE': 0, 'EN_COURS': 0, 'TERMINE': 0}
    for item in stats_statut:
        statut_counts[item['statut']] = item['total']

    context = {
        'total_clients': total_clients,
        'total_vehicules': total_vehicules,
        'total_reparations': total_reparations,
        'clients_recents': clients_recents,
        'vehicules_recents': vehicules_recents,
        'reparations_recentes': reparations_recentes,
        'statut_counts': statut_counts,
        'client_form': ClientForm(),
        'vehicule_form': VehiculeForm(),
        'reparation_form': ReparationForm(),
    }
    return render(request, 'garage/index.html', context)


# --- MODULE CLIENTS (CRUD, RECHERCHE, PAGINATION) ---
def client_list(request):
    query = request.GET.get('q', '')
    if query:
        clients_all = Client.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) | 
            Q(telephone__icontains=query) | 
            Q(email__icontains=query)
        ).order_by('-id')
    else:
        clients_all = Client.objects.all().order_by('-id')

    # Pagination : 5 clients par page
    paginator = Paginator(clients_all, 5)
    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)

    form = ClientForm()
    context = {
        'clients': clients,
        'query': query,
        'form': form,
    }
    return render(request, 'garage/client_list.html', context)


def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    return redirect('client_list')


def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    vehicules = client.vehicules.all()
    context = {
        'client': client,
        'vehicules': vehicules,
    }
    return render(request, 'garage/client_detail.html', context)


def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'garage/client_form.html', {'form': form, 'client': client})


def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        return redirect('client_list')
    return render(request, 'garage/client_confirm_delete.html', {'client': client})


# --- VUE FACTURE PDF ---
def generer_facture_pdf(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    template = get_template('garage/facture_pdf.html')
    
    context = {
        'facture': facture,
        'lignes': facture.lignes.all(),
    }
    
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    
    filename = f"{facture.get_type_document_display()}_{facture.numero}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=response)
    
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)
    
    return response