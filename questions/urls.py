
from django.urls import path, include # Importe 'include' ici aussi
from . import views # Importe le module views de notre application

app_name = 'questions' # Définit un espace de nom pour nos URLs

urlpatterns = [
    path('', views.liste_questions, name='liste_questions'), # URL pour la page d'accueil
    path('compte/inscription/', views.inscription, name='inscription'), # Notre vue d'inscription
    path('question/poser/', views.poser_question, name='poser_question'),
    path('question/<int:question_id>/', views.detail_question, name='detail_question'),
    path('question/<int:question_id>/repondre/', views.repondre_question, name='repondre_question'),
    path('reponse/<int:reponse_id>/vote/', views.voter_reponse, name='voter_reponse'),
    path('reponse/<int:reponse_id>/meilleure/', views.marquer_meilleure_reponse, name='marquer_meilleure_reponse'),
    path('tag/<int:tag_id>/', views.filtrer_par_tag, name='filtrer_par_tag'),
    path('tags/', views.liste_tags, name='liste_tags'),
    path('tags/populaires/', views.tags_populaires, name='tags_populaires'),
    path('tag/ajouter/', views.ajouter_tag, name='ajouter_tag'),
    path('question/modifier/<int:id>/', views.modifier_question, name='modifier_question'),
    path('question/supprimer/<int:id>/', views.supprimer_question, name='supprimer_question'),
    path('reponse/modifier/<int:reponse_id>/', views.modifier_reponse, name='modifier_reponse'),
    path('reponse/supprimer/<int:reponse_id>/', views.supprimer_reponse, name='supprimer_reponse'),
    path('reponse/valider/<int:reponse_id>/', views.valider_reponse, name='valider_reponse'),

]

