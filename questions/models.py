from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom

class Question(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions_posees')
    date_publication = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='questions_associees', blank=True)

    @property
    def total_votes(self):
        return sum(reponse.score for reponse in self.reponses.all())

    def __str__(self):
        return self.titre

class Reponse(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='reponses')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reponses_donnees')
    contenu = models.TextField()
    date_publication = models.DateTimeField(auto_now_add=True)
    est_meilleure_reponse = models.BooleanField(default=False)

    @property
    def score(self):
        return sum(v.valeur for v in self.votes_recu.all())

    def __str__(self):
        return f"Réponse de {self.auteur.username} à '{self.question.titre}'"

class VoteReponse(models.Model):
    reponse = models.ForeignKey(Reponse, on_delete=models.CASCADE, related_name='votes_recu')
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    valeur = models.SmallIntegerField(choices=[(1, '👍'), (-1, '👎')], default=1)

    class Meta:
        unique_together = ('reponse', 'utilisateur')

    def __str__(self):
        return f"{self.utilisateur.username} a voté {self.valeur} sur réponse {self.reponse.id}"
