from django.urls import include, path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('connexion/', views.login_view, name='login'),
    path('inscription/', views.register_view, name='register'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('equipement/nouveau/', views.equipment_create, name='equipment_create'),
    path('equipement/<int:pk>/modifier/', views.equipment_update, name='equipment_update'),
    path('equipement/<int:pk>/supprimer/', views.equipment_delete, name='equipment_delete'),
    path('type_materiel/nouveau/', views.material_type_create, name='material_type_create'),
    path('demande/nouveau/', views.request_create, name='request_create'),
    path('demande/<int:pk>/modifier/', views.request_update, name='request_update'),
    path('demande/<int:pk>/supprimer/', views.request_delete, name='request_delete'),
    path('historique/', views.history_view, name='history'),
    path('retour/<int:assignment_id>/', views.return_equipment, name='return_equipment'),
    path("__reload__/", include("django_browser_reload.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
