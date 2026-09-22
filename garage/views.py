import io
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from .models import Reparation, Client, Vehicule, Facture
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


# -------------------------------------------------------------------
# NOUVELLE VUE : GÉNÉRATION DU PDF DE FACTURE / DEVIS
# -------------------------------------------------------------------

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