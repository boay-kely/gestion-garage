import io
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Count, Q
from django.core.paginator import Paginator
from xhtml2pdf import pisa

from .models import Reparation, Client, Vehicule, Facture, LigneFacture
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
                reparation = form.save()
                # Création automatique d'une facture liée
                facture = Facture.objects.create(
                    reparation=reparation,
                    numero=f"FAC-{reparation.id:04d}",
                    type_document='FACTURE'
                )
                LigneFacture.objects.create(
                    facture=facture,
                    description=reparation.description,
                    quantite=1,
                    prix_unitaire=reparation.cout
                )
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


# --- MODULE CLIENTS ---
def client_list(request):
    query = request.GET.get('q', '')
    if query:
        clients_all = Client.objects.filter(
            Q(nom__icontains=query) | Q(prenom__icontains=query) |
            Q(telephone__icontains=query) | Q(email__icontains=query)
        ).order_by('-id')
    else:
        clients_all = Client.objects.all().order_by('-id')

    paginator = Paginator(clients_all, 5)
    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)

    return render(request, 'garage/client_list.html', {'clients': clients, 'query': query, 'form': ClientForm()})


def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('client_list')


def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'garage/client_detail.html', {'client': client, 'vehicules': client.vehicules.all()})


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


# --- MODULE VÉHICULES ---
def vehicule_list(request):
    query = request.GET.get('q', '')
    if query:
        vehicules_all = Vehicule.objects.select_related('client').filter(
            Q(immatriculation__icontains=query) | Q(marque__icontains=query) |
            Q(modele__icontains=query) | Q(client__nom__icontains=query)
        ).order_by('-id')
    else:
        vehicules_all = Vehicule.objects.select_related('client').all().order_by('-id')

    paginator = Paginator(vehicules_all, 5)
    vehicules = paginator.get_page(request.GET.get('page'))

    return render(request, 'garage/vehicule_list.html', {'vehicules': vehicules, 'query': query, 'form': VehiculeForm()})


def vehicule_create(request):
    if request.method == 'POST':
        form = VehiculeForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('vehicule_list')


def vehicule_detail(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    reparations = Reparation.objects.filter(vehicule=vehicule).order_by('-id')
    return render(request, 'garage/vehicule_detail.html', {'vehicule': vehicule, 'reparations': reparations})


def vehicule_update(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        form = VehiculeForm(request.POST, instance=vehicule)
        if form.is_valid():
            form.save()
            return redirect('vehicule_list')
    else:
        form = VehiculeForm(instance=vehicule)
    return render(request, 'garage/vehicule_form.html', {'form': form, 'vehicule': vehicule})


def vehicule_delete(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        vehicule.delete()
        return redirect('vehicule_list')
    return render(request, 'garage/vehicule_confirm_delete.html', {'vehicule': vehicule})


# --- MODULE RÉPARATIONS (CRUD, RECHERCHE, PAGINATION & FACTURE) ---
def reparation_list(request):
    query = request.GET.get('q', '')
    statut = request.GET.get('statut', '')

    reparations_all = Reparation.objects.select_related('vehicule', 'vehicule__client').all().order_by('-id')

    if query:
        reparations_all = reparations_all.filter(
            Q(description__icontains=query) |
            Q(vehicule__immatriculation__icontains=query) |
            Q(vehicule__marque__icontains=query) |
            Q(vehicule__client__nom__icontains=query)
        )

    if statut:
        reparations_all = reparations_all.filter(statut=statut)

    paginator = Paginator(reparations_all, 5)
    reparations = paginator.get_page(request.GET.get('page'))

    return render(request, 'garage/reparation_list.html', {
        'reparations': reparations,
        'query': query,
        'statut': statut,
        'form': ReparationForm()
    })


def reparation_create(request):
    if request.method == 'POST':
        form = ReparationForm(request.POST)
        if form.is_valid():
            reparation = form.save()
            # Création automatique de la facture
            facture = Facture.objects.create(
                reparation=reparation,
                numero=f"FAC-{reparation.id:04d}",
                type_document='FACTURE'
            )
            LigneFacture.objects.create(
                facture=facture,
                description=reparation.description,
                quantite=1,
                prix_unitaire=reparation.cout
            )
            return redirect('reparation_list')
    return redirect('reparation_list')


def reparation_detail(request, pk):
    reparation = get_object_or_404(Reparation, pk=pk)
    facture = Facture.objects.filter(reparation=reparation).first()
    return render(request, 'garage/reparation_detail.html', {'reparation': reparation, 'facture': facture})


def reparation_update(request, pk):
    reparation = get_object_or_404(Reparation, pk=pk)
    if request.method == 'POST':
        form = ReparationForm(request.POST, instance=reparation)
        if form.is_valid():
            rep = form.save()
            # Mise à jour du prix sur la ligne de facture associée
            facture = Facture.objects.filter(reparation=rep).first()
            if facture:
                ligne = facture.lignes.first()
                if ligne:
                    ligne.description = rep.description
                    ligne.prix_unitaire = rep.cout
                    ligne.save()
            return redirect('reparation_list')
    else:
        form = ReparationForm(instance=reparation)
    return render(request, 'garage/reparation_form.html', {'form': form, 'reparation': reparation})


def reparation_delete(request, pk):
    reparation = get_object_or_404(Reparation, pk=pk)
    if request.method == 'POST':
        reparation.delete()
        return redirect('reparation_list')
    return render(request, 'garage/reparation_confirm_delete.html', {'reparation': reparation})


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