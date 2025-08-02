from django.urls import include, path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('connexion/', views.login_view, name='login'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/nouveau/', views.user_create, name='user_create'),
    path('users/<int:pk>/modifier/', views.modify_user, name='modify_user'),
    path('users/<int:pk>/supprimer/', views.user_delete, name='user_delete'),
    path('stock/', views.stock, name='stock'),
    path('equipement/nouveau/', views.equipment_create, name='equipment_create'),
    path('equipement/<int:pk>/modifier/', views.equipment_update, name='equipment_update'),
    path('equipement/<int:pk>/supprimer/', views.equipment_delete, name='equipment_delete'),
    path('affectation/', views.gestion_affectation, name='gestion_affectation'),
    path('affectation/nouveau/', views.affectation_create, name='affectation_create'),
    path('affectation/<int:pk>/modifier/', views.affectation_update, name='affectation_update'),
    path('affectation/<int:pk>/retour/', views.affectation_return, name='affectation_return'),
    path('notifications/', views.notifications, name='notifications'),
    path('mes_equipements/', views.mes_equipements, name='mes_equipements'),
    path('demande_equipement/nouveau/', views.demande_equipement_create, name='demande_equipement_create'),
    path('demande_intervention/nouveau/', views.demande_intervention_create, name='demande_intervention_create'),
    path('equipement/', views.gestion_equipement, name='gestion_equipement'),
    path('demande_equipement/<int:pk>/approuver/', views.demande_equipement_approve, name='demande_equipement_approve'),
    path("__reload__/", include("django_browser_reload.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
