# 🧠 Stack-OMBENATION

🎓 **Projet académique** réalisé avec Django — une plateforme de type Q&R inspirée de StackOverflow, adaptée aux besoins pédagogiques et communautaires.
## 🧩 Fonctionnalités principales

- 💬 **Poser des questions** avec titre, description et tags
- 🗳️ **Voter** pour les réponses les plus pertinentes
- 🏅 **Marquer une réponse comme “meilleure”**
- 🏷️ **Filtrer les questions par tags**
- 🔍 **Recherche dynamique** des questions
- 📄 **Pagination AJAX** pour une navigation fluide
- 👤 **Gestion des rôles utilisateurs** (utilisateur simple, gestionnaire, admin)

## ⚙️ Technologies utilisées

| Outil | Version | Rôle |
|------|---------|------|
| Python | 3.13 | Langage principal |
| Django | 5.2 | Framework web |
| HTML/CSS | — | Structure et style |
| FontAwesome | — | Icônes |
| Git & GitHub | — | Versioning et publication |

## 🧪 Instructions pour tester en local

```bash
git clone https://github.com/Ombeni-Manasse/Stack-OMBENATION.git
cd Stack-OMBENATION
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
