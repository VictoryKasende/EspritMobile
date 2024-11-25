from InspiraApp.models import Category, Citation, Thought, Paragraph, User
from django.utils.text import slugify

# Création des catégories
def create_categories():
    categories = [
        {"name": "Inspiration", "description": "Catégorie pour des idées inspirantes."},
        {"name": "Motivation", "description": "Catégorie pour booster votre motivation."},
        {"name": "Sagesse", "description": "Catégorie pour des pensées sages."},
        {"name": "Philosophie", "description": "Catégorie sur la philosophie et la réflexion."},
        {"name": "Humour", "description": "Catégorie pour des citations humoristiques."},
        {"name": "Amour", "description": "Catégorie pour des pensées d'amour."},
        {"name": "Leadership", "description": "Catégorie sur le leadership et le succès."},
        {"name": "Développement personnel", "description": "Catégorie pour la croissance personnelle."},
        {"name": "Spiritualité", "description": "Catégorie sur la spiritualité et la foi."},
        {"name": "Résilience", "description": "Catégorie pour surmonter les obstacles."},
    ]

    for category_data in categories:
        category, created = Category.objects.get_or_create(
            name=category_data["name"],
            defaults={
                "slug": slugify(category_data["name"]),
                "description": category_data["description"],
            },
        )
        if created:
            print(f"Catégorie créée : {category.name}")
        else:
            print(f"Catégorie existante : {category.name}")

# Création des citations
def create_citations():
    user = User.objects.first()  # Remplacez par un utilisateur spécifique si nécessaire
    if not user:
        print("Aucun utilisateur trouvé.")
        return

    citations = [
        {"title": "La vie est belle", "author": "Auteur inconnu", "category": "Inspiration", "description": "Une citation inspirante."},
        {"title": "Le succès vient avec l'effort", "author": "Auteur célèbre", "category": "Motivation", "description": "Une citation pour motiver."},
    ]

    for citation_data in citations:
        category = Category.objects.filter(name=citation_data["category"]).first()
        if category:
            citation, created = Citation.objects.get_or_create(
                title=citation_data["title"],
                defaults={
                    "slug": slugify(citation_data["title"]),
                    "author": citation_data["author"],
                    "description": citation_data["description"],
                    "user": user,
                    "category": category,
                },
            )
            if created:
                print(f"Citation créée : {citation.title}")
            else:
                print(f"Citation existante : {citation.title}")

# Création des pensées
def create_thoughts():
    user = User.objects.first()  # Remplacez par un utilisateur spécifique si nécessaire
    if not user:
        print("Aucun utilisateur trouvé.")
        return

    thoughts = [
        {"title": "Réflexion sur la vie", "author": "Auteur inconnu", "category": "Philosophie", "description": "Une pensée profonde."},
        {"title": "L'humour est une clé", "author": "Auteur humoriste", "category": "Humour", "description": "Une pensée humoristique."},
    ]

    for thought_data in thoughts:
        category = Category.objects.filter(name=thought_data["category"]).first()
        if category:
            thought, created = Thought.objects.get_or_create(
                title=thought_data["title"],
                defaults={
                    "slug": slugify(thought_data["title"]),
                    "author": thought_data["author"],
                    "description": thought_data["description"],
                    "user": user,
                    "category": category,
                },
            )
            if created:
                print(f"Pensée créée : {thought.title}")
            else:
                print(f"Pensée existante : {thought.title}")

# Création des paragraphes
def create_paragraphs():
    thought = Thought.objects.first()  # Remplacez par une pensée spécifique si nécessaire
    if not thought:
        print("Aucune pensée trouvée.")
        return

    paragraphs = [
        {"content": "Première réflexion intéressante.", "active": True},
        {"content": "Deuxième réflexion pour approfondir.", "active": True},
    ]

    for paragraph_data in paragraphs:
        paragraph, created = Paragraph.objects.get_or_create(
            thought=thought,
            defaults={
                "content": paragraph_data["content"],
                "active": paragraph_data["active"],
            },
        )
        if created:
            print(f"Paragraphe créé pour {thought.title}")
        else:
            print(f"Paragraphe existant pour {thought.title}")

if __name__ == "__main__":
    print("Création des données...")
    #create_categories()
    create_citations()
    create_thoughts()
    create_paragraphs()
    print("Données créées avec succès.")
