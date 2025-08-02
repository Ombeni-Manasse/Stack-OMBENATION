from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Sum, Count
import json

from .models import Question, Reponse, VoteReponse, Tag
from .forms import CustomUserCreationForm, QuestionForm, ReponseForm, TagForm

def liste_questions(request):
    question_list = Question.objects.annotate(
        score=Sum('reponses__votes_recu__valeur')
    ).order_by('-date_publication')

    paginator = Paginator(question_list, 5)
    page_number = request.GET.get('page')
    questions = paginator.get_page(page_number)

    tags = Tag.objects.all()

    questions_resolues = {
        q.id: q.reponses.filter(est_meilleure_reponse=True).exists()
        for q in questions
    }

    return render(request, 'questions/liste_questions.html', {
        'questions': questions,
        'tags': tags,
        'titre_page': "Questions récentes",
        'questions_resolues': questions_resolues,
        'tag_actif': None,  # ← important pour gérer le style même sans filtre
    })


def filtrer_par_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)

    question_list = tag.questions_associees.annotate(
        score=Sum('reponses__votes_recu__valeur')
    ).order_by('-date_publication')

    paginator = Paginator(question_list, 5)
    page_number = request.GET.get('page')
    questions = paginator.get_page(page_number)

    questions_resolues = {
        q.id: q.reponses.filter(est_meilleure_reponse=True).exists()
        for q in questions
    }

    tags = Tag.objects.all()

    return render(request, 'questions/liste_questions.html', {
        'questions': questions,
        'tags': tags,
        'tag_actif': tag,  # ← ajout essentiel pour activer le style sticky
        'titre_page': f"Questions sur « {tag.nom} »",
        'questions_resolues': questions_resolues,
    })


def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('questions:liste_questions')
    else:
        form = CustomUserCreationForm()

    return render(request, 'questions/inscription.html', {
        'form': form,
        'titre_page': "S'inscrire",
    })


@login_required
def poser_question(request):
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.auteur = request.user
            question.save()
            form.save_m2m()
            return redirect('questions:liste_questions')
    else:
        form = QuestionForm()
    return render(request, 'questions/poser_question.html', {
        'form': form,
        'titre_page': "Poser une question",
    })


@login_required
def detail_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    reponse_form = ReponseForm()

    # Pagination manuelle des réponses
    all_reponses = question.reponses.order_by('-date_publication')
    paginator = Paginator(all_reponses, 3)  # ← 3 réponses visibles par page
    page_number = request.GET.get('page')
    reponses = paginator.get_page(page_number)

    return render(request, 'questions/detail_question.html', {
        'question': question,
        'reponse_form': reponse_form,
        'reponses': reponses,
        'has_more': reponses.has_next(),
        'titre_page': "Détail de la question",
    })




@login_required
def repondre_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        form = ReponseForm(request.POST)
        if form.is_valid():
            reponse = form.save(commit=False)
            reponse.auteur = request.user
            reponse.question = question
            reponse.save()
            return redirect('questions:detail_question', question_id=question.id)
    else:
        form = ReponseForm()

    return render(request, 'questions/repondre_question.html', {
        'form': form,
        'question': question,
        'titre_page': "Répondre à la question"
    })


@require_POST
@login_required
def voter_reponse(request, reponse_id):
    reponse = get_object_or_404(Reponse, id=reponse_id)
    data = json.loads(request.body)
    valeur_vote = int(data.get("valeur", 0))

    if valeur_vote not in [1, -1]:
        return JsonResponse({'success': False, 'error': 'Vote non valide'}, status=400)

    try:
        vote, created = VoteReponse.objects.get_or_create(
            reponse=reponse,
            utilisateur=request.user,
            defaults={'valeur': valeur_vote}
        )

        if not created:
            return JsonResponse({'success': False, 'error': "Vous avez déjà voté cette réponse"}, status=403)

        return JsonResponse({'success': True, 'score': reponse.score})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@login_required
def marquer_meilleure_reponse(request, reponse_id):
    reponse = get_object_or_404(Reponse, id=reponse_id)
    question = reponse.question

    if request.user != question.auteur:
        return JsonResponse({'success': False, 'error': "Action non autorisée"}, status=403)

    question.reponses.update(est_meilleure_reponse=False)
    reponse.est_meilleure_reponse = True
    reponse.save()

    return JsonResponse({'success': True})


def liste_tags(request):
    tags = Tag.objects.all()
    return render(request, 'questions/liste_tags.html', {
        'tags': tags,
        'titre_page': "Liste des tags",
    })


def tags_populaires(request):
    tags = Tag.objects.annotate(nb_questions=Count('questions_associees')).order_by('-nb_questions')
    return render(request, 'questions/tags_populaires.html', {
        'tags': tags,
        'titre_page': "Tags les plus populaires",
    })


@login_required
def ajouter_tag(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('questions:poser_question')
    else:
        form = TagForm()
    return render(request, 'questions/ajouter_tag.html', {
        'form': form,
        'titre_page': "Ajouter un tag",
    })


@login_required
def modifier_question(request, id):
    question = get_object_or_404(Question, id=id)

    if request.user != question.auteur:
        return redirect('questions:detail_question', id=question.id)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('questions:detail_question', id=question.id)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'questions/modifier_question.html', {
        'form': form,
        'question': question
    })


@login_required
def supprimer_question(request, id):
    question = get_object_or_404(Question, id=id)

    if request.user == question.auteur:
        question.delete()

    return redirect('questions:liste_questions')


@login_required
def modifier_reponse(request, reponse_id):
    reponse = get_object_or_404(Reponse, id=reponse_id)

    if request.user != reponse.auteur:
        return redirect('questions:detail_question', question_id=reponse.question.id)

    if request.method == 'POST':
        form = ReponseForm(request.POST, instance=reponse)
        if form.is_valid():
            form.save()
            return redirect('questions:detail_question', question_id=reponse.question.id)
    else:
        form = ReponseForm(instance=reponse)

    return render(request, 'questions/modifier_reponse.html', {
        'form': form,
        'reponse': reponse
    })


@login_required
def supprimer_reponse(request, reponse_id):
    reponse = get_object_or_404(Reponse, id=reponse_id)

    if request.user == reponse.auteur:
        reponse.delete()

    return redirect('questions:detail_question', question_id=reponse.question.id)


@login_required
def valider_reponse(request, reponse_id):
    reponse = get_object_or_404(Reponse, id=reponse_id)

    if request.user == reponse.question.auteur:
        reponse.est_meilleure_reponse = True
        reponse.save()

    return redirect('questions:detail_question', question_id=reponse.question.id)


def questions_par_tag(request, tag_id=None):
    tags = Tag.objects.all()
    tag_actif = None
    questions = []
    titre_page = "Questions par tag"

    if tag_id:
        tag = get_object_or_404(Tag, id=tag_id)

        # Si le tag est déjà actif (via paramètre GET), on le désactive
        if request.GET.get('actif') == 'false':
            tag_actif = None
        else:
            tag_actif = tag
            questions = tag.questions_associees.annotate(
                score=Sum('reponses__votes_recu__valeur')
            ).order_by('-date_publication')

    paginator = Paginator(questions, 5)
    page_number = request.GET.get('page')
    questions_paginees = paginator.get_page(page_number)

    questions_resolues = {
        q.id: q.reponses.filter(est_meilleure_reponse=True).exists()
        for q in questions_paginees
    }

    return render(request, 'questions/questions_par_tag.html', {
        'questions': questions_paginees,
        'tags': tags,
        'tag_actif': tag_actif,
        'titre_page': titre_page,
        'questions_resolues': questions_resolues,
    })

def fragment_questions_par_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    questions = tag.questions_associees.annotate(
        score=Sum('reponses__votes_recu__valeur')
    ).order_by('-date_publication')

    return render(request, 'questions/fragment_questions_par_tag.html', {
        'questions': questions,
        'tag': tag,
    })


def voir_plus_reponses(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    reponses_list = Reponse.objects.filter(question=question).order_by('-date_creation')

    paginator = Paginator(reponses_list, 5)  # 5 réponses par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'question': question,
        'page_obj': page_obj,
        'has_more': page_obj.has_next(),
    }
    return render(request, 'questions/voir_plus_reponses.html', context)

