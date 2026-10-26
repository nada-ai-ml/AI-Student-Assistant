import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from google import genai

# -------------------- CONFIGURATION --------------------
st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="🎓",
    layout="wide",
)

DB_PATH = "student_assistant.db"
GEMINI_MODEL = "gemini-3.5-flash-lite"


# -------------------- DESIGN --------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #f5f8ff;
        color: #172554;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #123b78, #0b2550);
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 20px;
        background: linear-gradient(120deg, #123b78, #2563eb);
        color: #ffffff;
        margin-bottom: 1rem;
    }

    .hero h1,
    .hero p {
        color: #ffffff !important;
    }

    .card {
        background: #ffffff;
        padding: 1rem 1.2rem;
        border: 1px solid #e2eaf8;
        border-radius: 15px;
        margin-bottom: .8rem;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2eaf8;
        border-radius: 14px;
        padding: 12px;
    }

    /* CORRECTION : affichage des choix du quiz */
    div[data-testid="stRadio"] {
        background: #ffffff;
        border: 1px solid #dbeafe;
        border-radius: 12px;
        padding: 12px 16px;
    }

    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] [role="radiogroup"] {
        color: #172554 !important;
    }

    div[data-testid="stRadio"] [role="radiogroup"] {
        gap: 10px;
    }

    div[data-testid="stRadio"] [role="radiogroup"] label {
        background: #ffffff !important;
        border: 1px solid #dbeafe;
        border-radius: 10px;
        padding: 8px 12px;
    }

    div[data-testid="stRadio"] [role="radiogroup"] label:hover {
        background: #eff6ff !important;
        border-color: #93c5fd;
    }

    /* Texte de la page principale */
    .stMarkdown,
    .stText,
    p,
    label {
        color: #172554;
    }

    /* Texte de la barre latérale */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- BASE DE DONNÉES --------------------
def creer_base_de_donnees():
    """Créer la table des résultats si elle n'existe pas."""
    with sqlite3.connect(DB_PATH) as connexion:
        connexion.execute(
            """
            CREATE TABLE IF NOT EXISTS resultats_quiz (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matiere TEXT NOT NULL,
                score INTEGER NOT NULL,
                date_resultat TEXT NOT NULL
            )
            """
        )


def lire_resultats():
    """Lire les résultats des quiz."""
    with sqlite3.connect(DB_PATH) as connexion:
        return pd.read_sql_query(
            """
            SELECT matiere, score, date_resultat
            FROM resultats_quiz
            ORDER BY id DESC
            """,
            connexion,
        )


def enregistrer_resultat(matiere, score):
    """Enregistrer le résultat d'un quiz."""
    with sqlite3.connect(DB_PATH) as connexion:
        connexion.execute(
            """
            INSERT INTO resultats_quiz
            (matiere, score, date_resultat)
            VALUES (?, ?, ?)
            """,
            (
                matiere,
                score,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )


# -------------------- GEMINI --------------------
def obtenir_client_gemini():
    """Créer le client Gemini avec la clé API."""
    cle_api = st.secrets.get("GEMINI_API_KEY", "")

    if not cle_api:
        raise ValueError(
            "La clé GEMINI_API_KEY est absente. "
            "Vérifie le fichier .streamlit/secrets.toml."
        )

    return genai.Client(api_key=cle_api)


def generer_contenu(prompt):
    """Envoyer une demande à Gemini."""
    client = obtenir_client_gemini()

    resultat = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    texte = getattr(resultat, "text", None)

    if not texte:
        raise ValueError(
            "Gemini n'a pas retourné de texte. Réessaie."
        )

    return texte


creer_base_de_donnees()


# -------------------- NAVIGATION --------------------
with st.sidebar:
    st.markdown("# 🎓 Student AI")
    st.caption("Ton espace d'apprentissage")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Accueil",
            "📊 Habitudes d'étude",
            "📚 Planning de révision",
            "🧠 Quiz",
            "📈 Progression",
            "🤖 Assistant IA",
            "📝 Résumé de cours",
        ],
        label_visibility="collapsed",
        key="navigation_page",
    )

    st.divider()
    st.caption("AI Student Assistant • Version 2.1")


# -------------------- ACCUEIL --------------------
if page == "🏠 Accueil":

    st.markdown(
        """
        <div class="hero">
            <h1>🎓 AI Student Assistant</h1>
            <p>
                Ton espace intelligent pour apprendre,
                planifier et progresser.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    historique = lire_resultats()

    total = len(historique)

    moyenne = (
        historique["score"].mean() * 100
        if total
        else 0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Outils d'apprentissage", "6")
    col2.metric("Quiz réalisés", total)
    col3.metric("Score moyen", f"{moyenne:.0f}%")

    st.subheader("Bienvenue !")

    st.write(
        "Utilise le menu à gauche pour choisir un outil "
        "et travailler dans une section à la fois."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="card">
                <h3>📅 Organise tes révisions</h3>
                <p>
                    Crée un planning selon tes matières
                    et ton temps disponible.
                </p>
            </div>

            <div class="card">
                <h3>🤖 Pose tes questions</h3>
                <p>
                    Demande à Gemini de t'expliquer
                    des notions de cours.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="card">
                <h3>🧠 Entraîne-toi</h3>
                <p>
                    Teste tes connaissances avec
                    des quiz rapides.
                </p>
            </div>

            <div class="card">
                <h3>📈 Suis tes progrès</h3>
                <p>
                    Consulte tes résultats enregistrés.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# -------------------- HABITUDES D'ÉTUDE --------------------
elif page == "📊 Habitudes d'étude":

    st.title("📊 Analyse de tes habitudes d'étude")

    st.write(
        "Renseigne tes habitudes pour obtenir "
        "des conseils pratiques."
    )

    col1, col2 = st.columns(2)

    study_hours = col1.number_input(
        "Heures d'étude par jour",
        min_value=0.0,
        max_value=24.0,
        value=2.0,
        step=0.5,
        key="study_hours",
    )

    sleep_hours = col2.number_input(
        "Heures de sommeil par nuit",
        min_value=0.0,
        max_value=24.0,
        value=8.0,
        step=0.5,
        key="sleep_hours",
    )

    if st.button("Analyser mes habitudes", type="primary"):

        donnees = pd.DataFrame(
            {
                "Activité": ["Étude", "Sommeil"],
                "Heures": [study_hours, sleep_hours],
            }
        )

        st.bar_chart(
            donnees,
            x="Activité",
            y="Heures",
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Temps d'étude",
            f"{study_hours:g} h/jour",
        )

        col2.metric(
            "Sommeil",
            f"{sleep_hours:g} h/nuit",
        )

        if sleep_hours < 7:
            st.warning(
                "Essaie de préserver suffisamment "
                "de temps pour dormir."
            )
        else:
            st.success(
                "Tu déclares dormir au moins 7 heures. "
                "Continue à préserver ton sommeil."
            )

        if study_hours < 2:
            st.info(
                "Essaie de planifier de petites "
                "sessions régulières."
            )
        else:
            st.info(
                "Répartis tes sessions d'étude "
                "et prévois des pauses."
            )


# -------------------- PLANNING DE RÉVISION --------------------
elif page == "📚 Planning de révision":

    st.title("📚 Générateur de planning de révision")

    st.write(
        "Organise tes révisions selon tes matières "
        "et ton temps disponible."
    )

    matieres = st.text_area(
        "Entre tes matières (une matière par ligne)",
        "Python\nDeep Learning\nBig Data Analytics",
        height=130,
    )

    heures = st.number_input(
        "Combien d'heures peux-tu étudier par jour ?",
        min_value=1,
        max_value=12,
        value=2,
        step=1,
    )

    if st.button("Générer mon planning", type="primary"):

        liste = [
            matiere.strip()
            for matiere in matieres.splitlines()
            if matiere.strip()
        ]

        if not liste:
            st.warning("Entre au moins une matière.")

        else:
            duree = heures / len(liste)

            planning = pd.DataFrame(
                {
                    "Séance": [
                        f"Séance {i}"
                        for i in range(1, len(liste) + 1)
                    ],
                    "Matière": liste,
                    "Durée (heures)": [
                        round(duree, 2)
                    ] * len(liste),
                }
            )

            st.dataframe(
                planning,
                use_container_width=True,
                hide_index=True,
            )

            st.success("Ton planning est prêt !")


# -------------------- QUIZ --------------------
elif page == "🧠 Quiz":

    st.title("🧠 Quiz de connaissances")
    st.write("Teste tes connaissances et améliore ton score !")

    questions = {
        "Python": [
            {
                "question": "Quel mot-clé permet de définir une fonction en Python ?",
                "options": ["function", "def", "define", "func"],
                "reponse": "def",
            },
            {
                "question": "Quel type de données représente le nombre 10 ?",
                "options": ["str", "float", "int", "bool"],
                "reponse": "int",
            },
            {
                "question": "Quelle fonction affiche un message à l'écran ?",
                "options": ["input()", "print()", "show()", "display_text()"],
                "reponse": "print()",
            },
            {
                "question": "Quel symbole permet de faire une comparaison d'égalité ?",
                "options": ["=", "==", "!=", "=>"],
                "reponse": "==",
            },
            {
                "question": "Quelle structure permet de répéter des instructions ?",
                "options": ["if", "def", "for", "return"],
                "reponse": "for",
            },
            {
                "question": "Comment créer une liste en Python ?",
                "options": ["(1, 2, 3)", "{1, 2, 3}", "[1, 2, 3]", "<1, 2, 3>"],
                "reponse": "[1, 2, 3]",
            },
            {
                "question": "Quel mot-clé permet de tester une condition ?",
                "options": ["if", "loop", "check", "test"],
                "reponse": "if",
            },
            {
                "question": "Quel est le résultat de 3 + 2 * 2 ?",
                "options": ["10", "7", "12", "8"],
                "reponse": "7",
            },
            {
                "question": "Quelle fonction demande une saisie à l'utilisateur ?",
                "options": ["print()", "input()", "read()", "scan()"],
                "reponse": "input()",
            },
            {
                "question": "Quelle valeur représente un booléen vrai en Python ?",
                "options": ["true", "TRUE", "True", "1True"],
                "reponse": "True",
            },
        ],

        "Deep Learning": [
            {
                "question": "Quel élément est à la base d'un réseau de neurones artificiels ?",
                "options": ["Une base de données", "Un neurone artificiel", "Un fichier Excel", "Un navigateur"],
                "reponse": "Un neurone artificiel",
            },
            {
                "question": "Qu'est-ce que le Deep Learning ?",
                "options": [
                    "Une branche du Machine Learning utilisant des réseaux de neurones profonds",
                    "Un langage de programmation",
                    "Un système de stockage",
                    "Un type de clavier",
                ],
                "reponse": "Une branche du Machine Learning utilisant des réseaux de neurones profonds",
            },
            {
                "question": "À quoi sert une fonction d'activation ?",
                "options": [
                    "À supprimer les données",
                    "À introduire une non-linéarité dans le réseau",
                    "À éteindre le réseau",
                    "À créer un fichier",
                ],
                "reponse": "À introduire une non-linéarité dans le réseau",
            },
            {
                "question": "Quel est le rôle d'une fonction de perte ?",
                "options": [
                    "Mesurer l'erreur du modèle",
                    "Augmenter la taille du fichier",
                    "Afficher une image",
                    "Supprimer les neurones",
                ],
                "reponse": "Mesurer l'erreur du modèle",
            },
            {
                "question": "À quoi sert l'entraînement d'un réseau de neurones ?",
                "options": [
                    "À apprendre des paramètres à partir des données",
                    "À modifier le clavier",
                    "À installer Internet",
                    "À créer uniquement des graphiques",
                ],
                "reponse": "À apprendre des paramètres à partir des données",
            },
            {
                "question": "Quel algorithme est souvent utilisé pour optimiser les réseaux de neurones ?",
                "options": ["Dijkstra", "Gradient Descent", "K-means uniquement", "Tri à bulles"],
                "reponse": "Gradient Descent",
            },
            {
                "question": "Que signifie une époque (epoch) pendant l'entraînement ?",
                "options": [
                    "Un passage complet sur les données d'entraînement",
                    "Une seule variable",
                    "Une couche du réseau",
                    "Une erreur de programmation",
                ],
                "reponse": "Un passage complet sur les données d'entraînement",
            },
            {
                "question": "Qu'est-ce que le surapprentissage (overfitting) ?",
                "options": [
                    "Le modèle mémorise trop les données d'entraînement et généralise mal",
                    "Le modèle n'utilise aucune donnée",
                    "Le modèle est toujours parfait",
                    "Le modèle fonctionne sans entraînement",
                ],
                "reponse": "Le modèle mémorise trop les données d'entraînement et généralise mal",
            },
            {
                "question": "Quel type de réseau est souvent utilisé pour les images ?",
                "options": ["CNN", "FTP", "SQL", "HTML"],
                "reponse": "CNN",
            },
            {
                "question": "Pourquoi sépare-t-on les données en entraînement et test ?",
                "options": [
                    "Pour évaluer les performances sur des données non utilisées pour l'entraînement",
                    "Pour supprimer les données",
                    "Pour doubler la taille du réseau",
                    "Pour éviter toute programmation",
                ],
                "reponse": "Pour évaluer les performances sur des données non utilisées pour l'entraînement",
            },
        ],

        "Big Data Analytics": [
            {
                "question": "Quel est l'objectif principal du Big Data Analytics ?",
                "options": [
                    "Analyser de grandes quantités de données",
                    "Créer uniquement des sites web",
                    "Remplacer les ordinateurs",
                    "Écrire du HTML uniquement",
                ],
                "reponse": "Analyser de grandes quantités de données",
            },
            {
                "question": "Que désigne généralement le Big Data ?",
                "options": [
                    "De très grands volumes de données complexes",
                    "Un petit fichier texte",
                    "Un langage de programmation",
                    "Un ordinateur portable",
                ],
                "reponse": "De très grands volumes de données complexes",
            },
            {
                "question": "Que représente le volume dans les 3V du Big Data ?",
                "options": [
                    "La quantité de données",
                    "La vitesse du processeur",
                    "La couleur des données",
                    "Le nombre de programmes",
                ],
                "reponse": "La quantité de données",
            },
            {
                "question": "Que représente la vélocité dans le Big Data ?",
                "options": [
                    "La vitesse de génération et de traitement des données",
                    "La taille de l'écran",
                    "Le coût du clavier",
                    "Le nombre de langages",
                ],
                "reponse": "La vitesse de génération et de traitement des données",
            },
            {
                "question": "À quoi sert la visualisation des données ?",
                "options": [
                    "À rendre les informations plus faciles à comprendre",
                    "À supprimer toutes les données",
                    "À remplacer l'analyse",
                    "À ralentir les calculs",
                ],
                "reponse": "À rendre les informations plus faciles à comprendre",
            },
            {
                "question": "Quel outil est couramment utilisé pour analyser des données avec Python ?",
                "options": ["Pandas", "PowerPoint uniquement", "Paint", "Notepad uniquement"],
                "reponse": "Pandas",
            },
            {
                "question": "Qu'est-ce qu'une donnée structurée ?",
                "options": [
                    "Une donnée organisée selon un format défini, comme une table",
                    "Une image sans description",
                    "Un son uniquement",
                    "Une donnée toujours incorrecte",
                ],
                "reponse": "Une donnée organisée selon un format défini, comme une table",
            },
            {
                "question": "Quel est le rôle du Data Mining ?",
                "options": [
                    "Découvrir des tendances et des relations dans les données",
                    "Réparer un écran",
                    "Créer un système d'exploitation",
                    "Écrire uniquement des documents",
                ],
                "reponse": "Découvrir des tendances et des relations dans les données",
            },
            {
                "question": "Pourquoi nettoyer les données avant une analyse ?",
                "options": [
                    "Pour corriger les erreurs et traiter les valeurs manquantes",
                    "Pour rendre les données plus grandes",
                    "Pour supprimer les résultats utiles",
                    "Pour éviter toute analyse",
                ],
                "reponse": "Pour corriger les erreurs et traiter les valeurs manquantes",
            },
            {
                "question": "Quelle est une application du Big Data Analytics ?",
                "options": [
                    "Prévoir les tendances de vente",
                    "Changer la couleur du clavier",
                    "Augmenter la luminosité de l'écran",
                    "Remplacer le système électrique",
                ],
                "reponse": "Prévoir les tendances de vente",
            },
        ],
    }

    matiere = st.selectbox(
        "Choisis un module :",
        list(questions.keys()),
    )

    liste_questions = questions[matiere]

    # Réinitialiser le quiz quand le module change
    cle_module = f"quiz_index_{matiere}"
    cle_scores = f"quiz_scores_{matiere}"

    if cle_module not in st.session_state:
        st.session_state[cle_module] = 0

    if cle_scores not in st.session_state:
        st.session_state[cle_scores] = []

    index = st.session_state[cle_module]

    if index < len(liste_questions):

        q = liste_questions[index]

        st.progress(index / len(liste_questions))
        st.write(f"Question **{index + 1} sur {len(liste_questions)}**")

        st.subheader(q["question"])

        reponse = st.radio(
            "Choisis ta réponse :",
            options=q["options"],
            index=None,
            key=f"choix_{matiere}_{index}",
        )

        if st.button("Valider ma réponse", type="primary"):

            if reponse is None:
                st.warning("Choisis une réponse avant de continuer.")

            else:
                correcte = reponse == q["reponse"]

                if correcte:
                    st.success("Bonne réponse ! 🎉")
                else:
                    st.error("Incorrect.")
                    st.info(f"Bonne réponse : {q['reponse']}")

                st.session_state[cle_scores].append(
                    1 if correcte else 0
                )

                st.session_state[cle_module] += 1

                st.rerun()

    else:

        scores = st.session_state[cle_scores]
        total = len(scores)
        bonnes_reponses = sum(scores)
        pourcentage = bonnes_reponses / total * 100 if total else 0

        st.success("Quiz terminé ! 🎉")

        st.metric(
            "Ton score final",
            f"{bonnes_reponses}/{total}",
        )

        st.progress(int(pourcentage) / 100)

        st.write(f"Résultat : {pourcentage:.0f}%")

        if pourcentage >= 80:
            st.balloons()
            st.success("Excellent travail !")
        elif pourcentage >= 50:
            st.info("Bon travail ! Continue à t'entraîner.")
        else:
            st.warning("Révise ce module et réessaie.")

        if st.button("Recommencer le quiz", type="primary"):
            st.session_state[cle_module] = 0
            st.session_state[cle_scores] = []
            st.rerun()
    st.title("🧠 Quiz de connaissances")

    st.write(
        "Teste tes connaissances dans tes matières."
    )

    questions = {
        "Python": {
            "question": (
                "Quel mot-clé permet de définir "
                "une fonction en Python ?"
            ),
            "options": [
                "function",
                "def",
                "define",
                "func",
            ],
            "reponse": "def",
        },

        "Deep Learning": {
            "question": (
                "Quel élément est à la base "
                "d'un réseau de neurones artificiels ?"
            ),
            "options": [
                "Une cellule biologique uniquement",
                "Un neurone artificiel",
                "Une base de données",
                "Un fichier Excel",
            ],
            "reponse": "Un neurone artificiel",
        },

        "Big Data Analytics": {
            "question": (
                "Quel est l'objectif principal "
                "du Big Data Analytics ?"
            ),
            "options": [
                "Créer uniquement des sites web",
                "Analyser de grandes quantités de données",
                "Remplacer tous les ordinateurs",
                "Écrire uniquement du code HTML",
            ],
            "reponse": (
                "Analyser de grandes quantités de données"
            ),
        },
    }

    matiere = st.selectbox(
        "Choisis une matière :",
        list(questions.keys()),
    )

    question = questions[matiere]

    st.subheader(f"Question — {matiere}")

    st.info(question["question"])

    # Les réponses sont affichées dans un widget radio.
    reponse = st.radio(
        "Choisis ta réponse :",
        options=question["options"],
        index=None,
        key=f"reponse_quiz_{matiere}",
    )

    if st.button(
        "Vérifier ma réponse",
        type="primary",
        key="verifier_quiz",
    ):

        if reponse is None:
            st.warning(
                "Choisis une réponse avant de vérifier."
            )

        else:
            score = int(
                reponse == question["reponse"]
            )

            if score:
                st.success("Bonne réponse ! 🎉")
            else:
                st.error(
                    "Ce n'est pas la bonne réponse."
                )

                st.info(
                    f"La bonne réponse est : "
                    f"{question['reponse']}"
                )

            enregistrer_resultat(
                matiere,
                score,
            )

            st.write(f"Ton score : {score}/1")

            st.success(
                "Ton résultat a été enregistré."
            )


# -------------------- PROGRESSION --------------------
elif page == "📈 Progression":

    st.title("📈 Ta progression")

    historique = lire_resultats()

    if historique.empty:

        st.info(
            "Tu n'as pas encore de résultats. "
            "Fais un quiz pour commencer !"
        )

    else:

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Quiz réalisés",
            len(historique),
        )

        col2.metric(
            "Score moyen",
            f"{historique['score'].mean() * 100:.0f}%",
        )

        col3.metric(
            "Bonnes réponses",
            int(historique["score"].sum()),
        )

        st.subheader("Historique des quiz")

        affichage = historique.rename(
            columns={
                "matiere": "Matière",
                "score": "Score (sur 1)",
                "date_resultat": "Date",
            }
        )

        st.dataframe(
            affichage,
            use_container_width=True,
            hide_index=True,
        )

        par_matiere = historique.groupby(
            "matiere",
            as_index=False,
        )["score"].mean()

        par_matiere["score"] = (
            par_matiere["score"] * 100
        ).round(0)

        par_matiere = par_matiere.rename(
            columns={
                "matiere": "Matière",
                "score": "Score moyen (%)",
            }
        )

        st.subheader("Scores par matière")

        st.bar_chart(
            par_matiere,
            x="Matière",
            y="Score moyen (%)",
        )


# -------------------- ASSISTANT IA --------------------
elif page == "🤖 Assistant IA":

    st.title("🤖 Ton assistant IA")

    st.write(
        "Pose tes questions sur tes cours et obtiens "
        "de l'aide pour tes révisions."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question_utilisateur = st.chat_input(
        "Pose ta question ici..."
    )

    if question_utilisateur:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question_utilisateur,
            }
        )

        with st.chat_message("user"):
            st.markdown(question_utilisateur)

        try:
            prompt = (
                "Tu es AI Student Assistant, "
                "un assistant pédagogique. "
                "Réponds clairement et simplement en français "
                "par défaut, sauf si l'étudiant demande "
                "une autre langue.\n\n"
                f"Question de l'étudiant : "
                f"{question_utilisateur}"
            )

            with st.spinner("L'assistant réfléchit..."):
                reponse = generer_contenu(prompt)

        except Exception as erreur:

            reponse = (
                "Je n'ai pas pu obtenir de réponse pour "
                "le moment. Vérifie ta clé API Gemini, "
                "ta connexion Internet et le nom du modèle."
            )

            st.error(
                f"Détail de l'erreur : {erreur}"
            )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": reponse,
            }
        )

        with st.chat_message("assistant"):
            st.markdown(reponse)


# -------------------- RÉSUMÉ DE COURS --------------------
elif page == "📝 Résumé de cours":

    st.title("📝 Résumé de cours avec l'IA")

    st.write(
        "Colle ton cours ci-dessous et Gemini préparera "
        "un résumé pour réviser."
    )

    cours = st.text_area(
        "Colle ton cours ici",
        height=250,
        placeholder="Colle le texte de ton cours ici...",
    )

    longueur = st.selectbox(
        "Choisis la longueur du résumé",
        [
            "Court",
            "Moyen",
            "Détaillé",
        ],
    )

    if st.button(
        "✨ Résumer mon cours",
        type="primary",
    ):

        if not cours.strip():

            st.warning(
                "Veuillez d'abord coller votre cours."
            )

        else:

            prompt = f"""
Tu es un assistant pédagogique.
Résume le cours suivant en français.

Longueur demandée : {longueur}

Consignes :
- Présente les idées essentielles.
- Utilise des titres et des listes.
- Explique les termes difficiles simplement.
- N'invente pas d'informations absentes du cours.

Cours :
{cours}
"""

            try:
                with st.spinner(
                    "Gemini prépare ton résumé..."
                ):
                    resume = generer_contenu(prompt)

                st.subheader("📖 Voici ton résumé")

                st.markdown(resume)

            except Exception as erreur:

                st.error(
                    "Impossible de générer le résumé "
                    "pour le moment."
                )

                st.caption(
                    f"Détail technique : {erreur}"
                )


# -------------------- PIED DE PAGE --------------------
st.markdown(
    """
    <p style="
        text-align:center;
        color:#64748b;
        margin-top:2rem;
    ">
        AI Student Assistant • Conçu pour accompagner tes études
    </p>
    """,
    unsafe_allow_html=True,
)