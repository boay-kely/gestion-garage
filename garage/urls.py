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
    
    # Facture PDF URL
    path('facture/<int:facture_id>/pdf/', views.generer_facture_pdf, name='facture_pdf'),
]