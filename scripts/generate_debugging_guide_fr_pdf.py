"""Generate a French debugging and architecture study guide for TaskFlow."""

from pathlib import Path
import textwrap

from generate_guide_fr_pdf import build_pdf


OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "Guide_debogage_architecture_TaskFlow_FR.pdf"

SECTIONS = [
    (
        "Guide junior : déboguer et modifier TaskFlow",
        [
            "But : savoir où regarder quand une fonctionnalité échoue, comprendre le trajet complet d'une requête et réaliser une petite modification sans casser le projet.",
            "Règle principale : ne modifie pas plusieurs choses au hasard. Reproduis le problème, lis le message exact, formule une hypothèse, change la plus petite chose possible, teste, puis commit une modification cohérente.",
        ],
    ),
    (
        "1. La carte mentale du projet",
        [
            "Navigateur -> React/Vite -> Nginx -> FastAPI -> SQLAlchemy -> MySQL.",
            "React affiche les pages et envoie des requêtes HTTP. Nginx sert les fichiers React compilés et transmet les appels /api/v1. FastAPI applique les règles métier, la sécurité et la validation. SQLAlchemy traduit les objets Python en requêtes paramétrées. MySQL conserve les utilisateurs, projets et tâches.",
            "Dans Docker Compose, frontend, backend et db sont trois conteneurs. Si l'interface est visible mais les données ne chargent pas, il faut suivre cette chaîne dans l'ordre : navigateur, frontend, proxy Nginx, backend, base de données.",
        ],
    ),
    (
        "2. Méthode de débogage en six étapes",
        [
            "1. Reproduire : note les actions exactes, l'URL, le compte utilisé et le résultat attendu.",
            "2. Observer : ouvre les outils développeur du navigateur (Network et Console), les logs Docker et les messages d'erreur FastAPI.",
            "3. Isoler la couche : interface, requête réseau, API, authentification, validation, migration ou base de données.",
            "4. Vérifier l'entrée et la sortie : statut HTTP, corps JSON, en-têtes Authorization/CORS, données envoyées au backend.",
            "5. Corriger le plus petit élément responsable, puis exécuter le test ciblé avant toute suite complète.",
            "6. Empêcher la régression : ajoute ou adapte un test, documente le comportement et fais un commit clair.",
        ],
    ),
    (
        "3. Comprendre une requête backend",
        [
            "Exemple : POST /api/v1/projects/3/tasks. La requête arrive dans main.py, puis FastAPI choisit la route dans api/routes/tasks.py.",
            "Avant la route, deps.py fournit une session SQLAlchemy et get_current_user. Cette fonction lit le Bearer token, valide le JWT, récupère l'utilisateur, sinon renvoie 401.",
            "La route récupère le projet avec get_owned_project. Le filtre owner_id garantit que le projet appartient à l'utilisateur connecté. Une autre personne reçoit 404.",
            "TaskCreate dans schemas/task.py valide les données. Le modèle Task dans models/task.py décrit la table. La route ajoute l'objet, commit, refresh, puis renvoie TaskResponse en JSON.",
            "Pour une erreur backend, commence par le statut HTTP : 401 signifie token invalide ou absent; 404 peut signifier ressource absente ou non autorisée; 422 signifie données invalides; 500 signifie exception serveur à lire dans les logs.",
        ],
    ),
    (
        "4. Fichiers backend : où modifier quoi ?",
        [
            "Nouvelle route API : backend/app/api/routes/*.py, puis inclure le routeur dans main.py si c'est un nouveau module.",
            "Nouvelle validation ou champ de requête/réponse : backend/app/schemas/*.py. Les schémas Pydantic protègent l'API des entrées inattendues.",
            "Nouvelle colonne/table : backend/app/models/*.py, puis créer une migration Alembic dans backend/alembic/versions. Ne modifie pas seulement le modèle : sans migration MySQL ne connaît pas la colonne.",
            "Règle métier réutilisable, par exemple calcul de statistiques : backend/app/services/*.py.",
            "Configuration : backend/app/core/config.py et .env.example. Ne mets jamais un secret dans le code ou dans Git.",
            "Authentification : backend/app/core/security.py crée les tokens et hash les mots de passe; backend/app/api/deps.py vérifie le token et fournit l'utilisateur courant.",
        ],
    ),
    (
        "5. Exemple de modification backend : ajouter un champ à Task",
        [
            "Supposons que l'on demande un champ estimate_hours. Avant de coder, décider : type numérique ? obligatoire ? valeur minimale ? peut-il être null ?",
            "1. Ajouter la colonne dans models/task.py, par exemple un nombre décimal ou entier nullable selon la règle.",
            "2. Générer puis relire une migration Alembic. Elle doit ajouter la colonne sans supprimer les données existantes.",
            "3. Ajouter le champ à TaskCreate, TaskUpdate et TaskResponse dans schemas/task.py. Utiliser une contrainte comme ge=0 pour refuser une estimation négative.",
            "4. Les routes de création/mise à jour utilisent model_dump : vérifier que le nouveau champ est bien accepté et renvoyé.",
            "5. Ajouter des tests : création valide, valeur négative retourne 422, mise à jour, et contrôle qu'un autre utilisateur reste bloqué.",
            "6. Appliquer la migration, lancer les tests et vérifier le champ via Swagger avant de modifier React.",
        ],
    ),
    (
        "6. Comprendre le frontend",
        [
            "frontend/src/main.jsx démarre React. App.jsx définit les routes login, register et dashboard. ProtectedRoute protège le tableau de bord quand il n'y a pas de token.",
            "auth.jsx contient le contexte d'authentification : jeton, connexion et déconnexion. api.js est le point unique pour fetch : URL API, JSON, Bearer token et ApiError.",
            "pages/Login.jsx et Register.jsx envoient les formulaires. pages/Dashboard.jsx gère projets, tâches, filtres, formulaires, chargement et erreurs. components.jsx contient les éléments réutilisables.",
            "Le frontend ne doit pas décider seul si une action est autorisée. Il peut cacher un bouton pour une bonne expérience utilisateur, mais seul le backend applique réellement l'autorisation.",
        ],
    ),
    (
        "7. Exemple de modification frontend : afficher estimate_hours",
        [
            "Après la modification backend, ajoute estimate_hours dans emptyTask de Dashboard.jsx.",
            "Ajoute un input number au formulaire. Convertis proprement la valeur : un champ vide doit souvent devenir null, pas 0 par accident.",
            "Quand saveTask construit body, ajoute estimate_hours. Affiche ensuite la valeur dans la carte de tâche seulement si elle existe.",
            "Teste trois cas dans le navigateur : création avec valeur, création sans valeur, modification. Vérifie dans l'onglet Network que le JSON contient la valeur attendue.",
            "Si l'interface montre undefined, compare le nom du champ envoyé par React avec TaskResponse dans Swagger. Les noms doivent correspondre exactement.",
        ],
    ),
    (
        "8. Déboguer React et les appels API",
        [
            "Erreur dans le navigateur : ouvrir F12, Console. Une erreur JavaScript indique souvent une variable null, un import faux ou une réponse inattendue.",
            "Données non chargées : dans Network, sélectionner la requête. Vérifier URL, méthode, code HTTP, requête JSON et réponse JSON.",
            "401 : supprimer le token local, se reconnecter et vérifier que api.js ajoute Authorization: Bearer <token>.",
            "CORS : vérifier FRONTEND_ORIGIN dans .env, recréer le backend, et vérifier l'origine exacte du navigateur. http://localhost:5173 et http://localhost:8080 sont différentes.",
            "422 : lire error.details dans la réponse; il indique le champ et la validation qui a échoué.",
            "Pour déboguer temporairement, console.log est acceptable localement, mais retirer les logs de données sensibles avant de commit.",
        ],
    ),
    (
        "9. Docker : symptômes fréquents",
        [
            "Voir l'état : docker compose ps. Lire les logs : docker compose logs --tail=100 backend, puis frontend ou db.",
            "Backend unhealthy : appeler http://localhost:8001/health. Lire les logs pour migration Alembic, base non disponible, variable d'environnement manquante ou erreur Python.",
            "Frontend ne démarre pas : docker compose logs frontend. Un upstream backend introuvable est souvent normal tant que le backend redémarre; corriger d'abord le backend.",
            "Script shell 'no such file or directory' alors que le fichier existe : penser aux fins de ligne Windows CRLF. Les scripts Linux doivent être LF; .gitattributes les impose.",
            "Build npm ci échoue : package.json et package-lock.json ne sont pas synchronisés. Regénérer le lockfile, le tester avec npm ci, puis commit les deux fichiers cohérents.",
            "Ne pas utiliser docker compose down -v sauf si tu acceptes de supprimer les données MySQL locales.",
        ],
    ),
    (
        "10. Base de données et migrations",
        [
            "MySQL contient les données persistantes dans le volume mysql_data. Redémarrer docker compose sans -v garde le volume.",
            "Alembic compare l'historique des migrations avec la table alembic_version. Au démarrage du backend, alembic upgrade head applique les migrations non exécutées.",
            "Après une modification de modèle, créer une migration, lire le fichier généré, appliquer la migration sur une base locale et tester. Une migration mauvaise peut casser une base de production, donc ne l'exécute jamais aveuglément.",
            "Pour inspecter une migration : docker compose exec backend alembic current. Pour voir une erreur SQL : docker compose logs backend et docker compose logs db.",
        ],
    ),
    (
        "11. Tests : choisir le bon test",
        [
            "Test unitaire : teste une petite fonction isolée, par exemple le calcul des statistiques ou le hash du mot de passe.",
            "Test API : utilise TestClient pour simuler un client HTTP, vérifier statuts, JSON, authentification, validation et isolement entre utilisateurs.",
            "Test frontend : vérifie une interaction utilisateur, par exemple connexion et affichage du dashboard, avec fetch simulé.",
            "Smoke test : appelle le système réellement démarré par Docker, donc Nginx, backend et MySQL ensemble.",
            "Quand tu corriges un bug, écris d'abord un test qui échoue à cause du bug si possible; applique le correctif; vérifie que le test passe.",
        ],
    ),
    (
        "12. Commandes à connaître",
        [
            "Stack : docker compose up -d --build ; docker compose ps ; docker compose logs -f backend ; docker compose down.",
            "Backend : backend\\.venv\\Scripts\\python.exe -m pytest backend\\tests -q ; backend\\.venv\\Scripts\\python.exe -m ruff check backend.",
            "Frontend, depuis frontend : npm ci ; npm run lint ; npm run test ; npm run build.",
            "Santé : Invoke-RestMethod http://localhost:8001/health ; Swagger : http://localhost:8001/docs ; application : http://localhost:8080.",
            "Git avant chaque changement : git status. Après les tests : git add <fichiers>, git commit -m 'type: message', git push origin <branche>.",
        ],
    ),
    (
        "13. Exercices avant l'entretien",
        [
            "Exercice 1 : ajoute une règle qui interdit un titre de tâche composé uniquement d'espaces. Trouve le schéma, ajoute un test 422, puis vérifie Swagger.",
            "Exercice 2 : ajoute un filtre par date d'échéance. Commence par la requête SQLAlchemy, puis paramètre FastAPI, test API, puis contrôle React.",
            "Exercice 3 : casse volontairement JWT_SECRET_KEY dans .env, observe le résultat, puis restaure-le. Explique pourquoi les anciens tokens deviennent invalides.",
            "Exercice 4 : crée deux utilisateurs, puis utilise Swagger avec le token du second pour demander un projet du premier. Explique le 404.",
            "Exercice 5 : explique sans écran la différence entre React, Vite, Nginx, FastAPI, SQLAlchemy, Alembic et MySQL.",
        ],
    ),
    (
        "14. Réponses courtes pour défendre le projet",
        [
            "Pourquoi FastAPI ? API REST lisible, validation Pydantic, injection de dépendances, Swagger automatique et bonne intégration SQLAlchemy/Alembic.",
            "Pourquoi React/Vite ? L'application est un tableau de bord interactif; React organise l'état et les composants, Vite fournit un développement rapide et un build statique simple.",
            "Comment éviter l'injection SQL ? SQLAlchemy produit des requêtes paramétrées; le code n'assemble pas les entrées utilisateur dans du SQL brut.",
            "Comment protéger les données ? JWT identifie l'utilisateur, puis les requêtes filtrent les projets/tâches par propriétaire. Authentification n'est pas autorisation.",
            "Comment livrer de façon fiable ? Docker Compose reproduit la stack; migrations versionnent le schéma; tests et scans CI bloquent une release défaillante; les tags permettent le rollback.",
        ],
    ),
]


def make_pages() -> list[list[tuple[str, int, bool]]]:
    pages: list[list[tuple[str, int, bool]]] = []
    current: list[tuple[str, int, bool]] = []
    used_height = 0

    def add(line: str, size: int, bold: bool, height: int) -> None:
        nonlocal current, used_height
        if current and used_height + height > 690:
            pages.append(current)
            current, used_height = [], 0
        current.append((line, size, bold))
        used_height += height

    for title, paragraphs in SECTIONS:
        if current and used_height > 630:
            pages.append(current)
            current, used_height = [], 0
        add(title, 16, True, 28)
        for paragraph in paragraphs:
            for line in textwrap.wrap(paragraph, width=92, break_long_words=False):
                add(line, 10, False, 15)
            add("", 6, False, 6)
        add("", 6, False, 8)
    if current:
        pages.append(current)
    return pages


if __name__ == "__main__":
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_bytes(build_pdf(make_pages()))
    print(OUTPUT)
