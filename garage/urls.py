from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # Client URLs
    path('clients/', views.client_list, name='client_list'),
    path('clients/creer/', views.client_create, name='client_create'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/<int:pk>/modifier/', views.client_update, name='client_update'),
    path('clients/<int:pk>/supprimer/', views.client_delete, name='client_delete'),

    # Vehicule URLs
    path('vehicules/', views.vehicule_list, name='vehicule_list'),
    path('vehicules/creer/', views.vehicule_create, name='vehicule_create'),
    path('vehicules/<int:pk>/', views.vehicule_detail, name='vehicule_detail'),
    path('vehicules/<int:pk>/modifier/', views.vehicule_update, name='vehicule_update'),
    path('vehicules/<int:pk>/supprimer/', views.vehicule_delete, name='vehicule_delete'),

    # Reparation URLs
    path('reparations/', views.reparation_list, name='reparation_list'),
    path('reparations/creer/', views.reparation_create, name='reparation_create'),
    path('reparations/<int:pk>/', views.reparation_detail, name='reparation_detail'),
    path('reparations/<int:pk>/modifier/', views.reparation_update, name='reparation_update'),
    path('reparations/<int:pk>/supprimer/', views.reparation_delete, name='reparation_delete'),

    # Facture PDF URL
    path('facture/<int:facture_id>/pdf/', views.generer_facture_pdf, name='facture_pdf'),
]