"""Generate an offline French study guide for the TaskFlow technical assessment."""

from pathlib import Path
import textwrap


OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "Guide_comprehension_TaskFlow_FR.pdf"

SECTIONS = [
    (
        "Guide de compréhension - TaskFlow",
        [
            "Objectif : comprendre l'application de bout en bout et pouvoir défendre ses choix techniques pendant un entretien.",
            "TaskFlow est une application web de gestion de projets et de tâches. Elle possède une interface React, une API FastAPI et une base de données MySQL.",
            "Conseil : ne mémorise pas ce document mot à mot. Ouvre les fichiers indiqués, exécute les commandes, puis explique-les avec tes propres mots.",
        ],
    ),
    (
        "1. Vue d'ensemble de l'architecture",
        [
            "Navigateur -> frontend React -> Nginx -> API FastAPI -> SQLAlchemy -> MySQL.",
            "Le frontend affiche les pages et recueille les actions de l'utilisateur. Le backend décide si une action est autorisée, valide les données et les enregistre. MySQL conserve les données même après le redémarrage des conteneurs.",
            "Dans Docker Compose, les services sont frontend, backend et db. Le frontend est accessible sur http://localhost:8080, Swagger sur http://localhost:8001/docs et le contrôle de santé sur http://localhost:8001/health.",
            "Le réseau interne isole MySQL : son port n'est pas publié vers le poste hôte. Les autres conteneurs le joignent avec le nom db.",
        ],
    ),
    (
        "2. Exemple complet : créer une tâche",
        [
            "1. L'utilisateur se connecte puis sélectionne un projet dans Dashboard.jsx.",
            "2. React utilise api() dans frontend/src/api.js pour envoyer une requête POST JSON à /api/v1/projects/{id}/tasks.",
            "3. Le jeton JWT est ajouté dans l'en-tête Authorization: Bearer <token>.",
            "4. FastAPI dirige la requête vers backend/app/api/routes/tasks.py.",
            "5. deps.py vérifie le JWT, identifie l'utilisateur courant et ouvre une session de base de données.",
            "6. Le backend vérifie que le projet appartient bien à cet utilisateur. Sinon il répond 404.",
            "7. Pydantic valide les champs : titre, statut, priorité et date éventuelle.",
            "8. SQLAlchemy écrit la tâche dans MySQL, puis FastAPI répond 201 Created avec du JSON.",
            "9. React recharge les données et affiche la nouvelle tâche.",
        ],
    ),
    (
        "3. Backend FastAPI : organisation",
        [
            "backend/app/main.py crée l'application FastAPI, configure CORS, les gestionnaires d'erreurs, /health et les routeurs.",
            "backend/app/api/routes/auth.py contient l'inscription et la connexion. projects.py gère les projets. tasks.py gère les tâches, les filtres, la recherche et les statistiques.",
            "backend/app/api/deps.py contient les dépendances réutilisables : session de base de données et utilisateur courant. C'est important car cela évite de recopier le contrôle de sécurité dans chaque route.",
            "backend/app/models contient les modèles SQLAlchemy. User possède plusieurs Project ; Project possède plusieurs Task.",
            "backend/app/schemas contient les modèles Pydantic utilisés pour valider les entrées et définir les réponses JSON. Un schéma API n'est pas obligatoirement identique à une table de base de données.",
            "backend/app/core/config.py lit les variables d'environnement. backend/app/core/security.py gère le hash des mots de passe et les JWT.",
            "backend/alembic contient les migrations. Au démarrage, alembic upgrade head applique le schéma de base de données attendu.",
        ],
    ),
    (
        "4. Authentification et autorisation",
        [
            "Authentification : vérifier qui est l'utilisateur. Lors de la connexion, le mot de passe fourni est comparé à son hash BCrypt stocké. Si la vérification réussit, l'API produit un JWT signé.",
            "Autorisation : vérifier ce que cet utilisateur peut faire. Avant de lire, modifier ou supprimer un projet ou une tâche, le backend filtre avec l'identifiant du propriétaire du projet.",
            "Phrase d'entretien : l'authentification prouve l'identité ; l'autorisation vérifie les droits sur une ressource.",
            "Pourquoi répondre 404 pour une ressource d'un autre utilisateur ? Cela évite aussi de confirmer qu'une ressource appartenant à quelqu'un d'autre existe.",
        ],
    ),
    (
        "5. Frontend React et Vite",
        [
            "React construit l'interface avec des composants. App.jsx définit les routes Login, Register et Dashboard. ProtectedRoute redirige vers /login si aucun jeton n'est présent.",
            "auth.jsx stocke l'état de connexion et le jeton. api.js centralise fetch : URL API, en-têtes JSON, jeton Bearer et gestion uniforme des erreurs.",
            "Dashboard.jsx contient les états React pour les projets, les tâches, les formulaires, les filtres, le chargement et les erreurs. components.jsx regroupe les composants visuels réutilisables.",
            "Vite n'est pas React. Vite est l'outil qui lance rapidement le serveur de développement et produit les fichiers statiques optimisés pour la production.",
        ],
    ),
    (
        "6. Défendre le choix FastAPI",
        [
            "Réponse courte : j'ai choisi FastAPI pour construire une API REST moderne, lisible et rapidement testable. Il s'intègre à Pydantic pour la validation, à SQLAlchemy pour MySQL, et génère automatiquement OpenAPI et Swagger.",
            "Avantages concrets dans ce projet : validation typée, dépendances pour l'authentification et la base de données, réponses HTTP claires, documentation interactive à /docs, tests simples avec pytest.",
            "Limite honnête : sur un système beaucoup plus grand, j'ajouterais par exemple la limitation de débit, du cache, une observabilité plus complète, des tâches asynchrones et une séparation plus poussée des domaines métier.",
        ],
    ),
    (
        "7. Défendre le choix React + Vite",
        [
            "Réponse courte : TaskFlow est une interface interactive avec formulaires, filtres, statut de connexion, chargement et données qui évoluent sans recharger toute la page. React est adapté à cette gestion d'état par composants.",
            "Vite réduit la configuration et fournit un démarrage rapide en développement ainsi qu'un build statique optimisé. En production, Nginx sert ce build, ce qui est léger et fiable.",
            "Limite honnête : React introduit davantage de logique côté client qu'une page HTML rendue côté serveur. Ici ce compromis est justifié par l'expérience de tableau de bord dynamique.",
        ],
    ),
    (
        "8. Docker, CI/CD et qualité",
        [
            "docker-compose.yml orchestre les trois services. Les health checks permettent à Docker de savoir si MySQL, le backend et le frontend sont prêts. Le volume mysql_data garde les données entre les redémarrages.",
            "Le backend utilise un Dockerfile Python et lance les migrations avant Uvicorn. Le frontend utilise un build Node puis Nginx pour servir les fichiers produits.",
            "Les tests backend couvrent les unités, l'API, l'authentification, l'autorisation et les entrées invalides. Le frontend possède au moins un test de connexion. Le smoke test vérifie le parcours local après Docker.",
            "GitHub Actions répète lint, tests et build sur les pull requests. L'objectif est d'empêcher la publication d'une version si les vérifications échouent.",
        ],
    ),
    (
        "9. Questions fréquentes pour la soutenance",
        [
            "Pourquoi un ORM ? SQLAlchemy rend les modèles lisibles et produit des requêtes paramétrées, ce qui aide à prévenir l'injection SQL.",
            "Pourquoi Alembic ? Les migrations versionnent le schéma. Un autre environnement peut recréer la même base sans créer des tables manuellement.",
            "Pourquoi MySQL n'est pas exposé ? La base est privée dans le réseau Docker interne ; cela réduit la surface d'attaque.",
            "Que contient le JWT ? Une identité signée et une expiration. Le frontend le transmet ; le backend le valide avant une route protégée.",
            "Comment revenir en arrière après une mauvaise livraison ? Revenir à une image versionnée connue ou à un tag Git, puis redéployer l'image correspondante. Le plan détaillé est dans CLOUD_DEPLOYMENT.md.",
        ],
    ),
    (
        "10. Plan personnel de révision",
        [
            "1. Ouvre main.py, deps.py, security.py, projects.py et tasks.py. Explique leur rôle sans regarder ce guide.",
            "2. Crée deux comptes. Avec Swagger, vérifie qu'un compte ne peut pas accéder aux projets de l'autre.",
            "3. Lance docker compose up -d --build, puis explique chaque service et chaque health check.",
            "4. Lance pytest, ruff, npm run lint, npm run test et npm run build. Lis au moins un test backend et Login.test.jsx.",
            "5. Prépare une démonstration de 5 à 10 minutes : inscription, projet, tâche, filtre, Swagger, persistance MySQL, tests, Docker, GitHub Actions et plan de déploiement.",
            "6. Sois transparent sur l'aide IA : explique ce que tu as vérifié, adapté et compris. Ne prétends jamais connaître un détail que tu ne peux pas expliquer.",
        ],
    ),
]


def pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def make_pages() -> list[list[tuple[str, int, bool]]]:
    pages: list[list[tuple[str, int, bool]]] = []
    current: list[tuple[str, int, bool]] = []
    height = 0
    for title, paragraphs in SECTIONS:
        block: list[tuple[str, int, bool]] = [(title, 16, True)]
        for paragraph in paragraphs:
            for line in textwrap.wrap(paragraph, width=92, break_long_words=False):
                block.append((line, 10, False))
            block.append(("", 6, False))
        block_height = sum(size + 5 for _, size, _ in block) + 12
        if current and height + block_height > 690:
            pages.append(current)
            current, height = [], 0
        current.extend(block)
        height += block_height
    if current:
        pages.append(current)
    return pages


def build_pdf(pages: list[list[tuple[str, int, bool]]]) -> bytes:
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    page_ids = [5 + index * 2 for index in range(len(pages))]
    kids = " ".join(f"{identifier} 0 R" for identifier in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode())
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    for number, lines in enumerate(pages, start=1):
        content = [
            "BT",
            "/F1 9 Tf",
            f"1 0 0 1 50 815 Tm (TaskFlow - Guide de comprehension - page {number}) Tj",
        ]
        y = 770
        for line, size, bold in lines:
            y -= size + 5
            if not line:
                continue
            font = "F2" if bold else "F1"
            encoded = pdf_escape(line).encode("cp1252", "replace").decode("cp1252")
            content.extend([f"/{font} {size} Tf", f"1 0 0 1 50 {y} Tm ({encoded}) Tj"])
        stream = "\n".join(content + ["ET"]).encode("cp1252", "replace")
        page_id = page_ids[number - 1]
        content_id = page_id + 1
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {content_id} 0 R >>".encode()
        )
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream")
    result = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, item in enumerate(objects, start=1):
        offsets.append(len(result))
        result.extend(f"{index} 0 obj\n".encode())
        result.extend(item)
        result.extend(b"\nendobj\n")
    xref = len(result)
    result.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode())
    result.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    )
    return bytes(result)


if __name__ == "__main__":
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_bytes(build_pdf(make_pages()))
    print(OUTPUT)
