# -*- coding: utf-8 -*-
"""
donnees.py - Données et logique pure de NEXA KIDS AFRICA (sans interface).
Copié à l'identique de la version Tkinter (mon_application.py) : conjugaison,
badges, alphabet, quiz, animaux, contes, anglais, français, 54 pays, couleurs,
formes, calendrier, corps humain, catégories du menu, nombres en lettres.
Aucune dépendance à Tkinter ni à Kivy : ce module est testable seul.
"""
import random

PRONOMS = ["je", "tu", "il", "nous", "vous", "ils"]

TERMINAISONS_ER = {
    "présent": ["e", "es", "e", "ons", "ez", "ent"],
    "imparfait": ["ais", "ais", "ait", "ions", "iez", "aient"],
    "futur-simple": ["ai", "as", "a", "ons", "ez", "ont"],
    "passé-simple": ["ai", "as", "a", "âmes", "âtes", "èrent"],
}

VERBES_IRREGULIERS = {
    "être": {
        "présent": ["suis", "es", "est", "sommes", "êtes", "sont"],
        "imparfait": ["étais", "étais", "était", "étions", "étiez", "étaient"],
        "futur-simple": ["serai", "seras", "sera", "serons", "serez", "seront"],
        "passé-simple": ["fus", "fus", "fut", "fûmes", "fûtes", "furent"],
    },
    "avoir": {
        "présent": ["ai", "as", "a", "avons", "avez", "ont"],
        "imparfait": ["avais", "avais", "avait", "avions", "aviez", "avaient"],
        "futur-simple": ["aurai", "auras", "aura", "aurons", "aurez", "auront"],
        "passé-simple": ["eus", "eus", "eut", "eûmes", "eûtes", "eurent"],
    },
    "aller": {
        "présent": ["vais", "vas", "va", "allons", "allez", "vont"],
        "imparfait": ["allais", "allais", "allait", "allions", "alliez", "allaient"],
        "futur-simple": ["irai", "iras", "ira", "irons", "irez", "iront"],
        "passé-simple": ["allai", "allas", "alla", "allâmes", "allâtes", "allèrent"],
    },
    "faire": {
        "présent": ["fais", "fais", "fait", "faisons", "faites", "font"],
        "imparfait": ["faisais", "faisais", "faisait", "faisions", "faisiez", "faisaient"],
        "futur-simple": ["ferai", "feras", "fera", "ferons", "ferez", "feront"],
        "passé-simple": ["fis", "fis", "fit", "fîmes", "fîtes", "firent"],
    },
    "dire": {
        "présent": ["dis", "dis", "dit", "disons", "dites", "disent"],
        "imparfait": ["disais", "disais", "disait", "disions", "disiez", "disaient"],
        "futur-simple": ["dirai", "diras", "dira", "dirons", "direz", "diront"],
        "passé-simple": ["dis", "dis", "dit", "dîmes", "dîtes", "dirent"],
    },
    "prendre": {
        "présent": ["prends", "prends", "prend", "prenons", "prenez", "prennent"],
        "imparfait": ["prenais", "prenais", "prenait", "prenions", "preniez", "prenaient"],
        "futur-simple": ["prendrai", "prendras", "prendra", "prendrons", "prendrez", "prendront"],
        "passé-simple": ["pris", "pris", "prit", "prîmes", "prîtes", "prirent"],
    },
    "venir": {
        "présent": ["viens", "viens", "vient", "venons", "venez", "viennent"],
        "imparfait": ["venais", "venais", "venait", "venions", "veniez", "venaient"],
        "futur-simple": ["viendrai", "viendras", "viendra", "viendrons", "viendrez", "viendront"],
        "passé-simple": ["vins", "vins", "vint", "vînmes", "vîntes", "vinrent"],
    },
    "voir": {
        "présent": ["vois", "vois", "voit", "voyons", "voyez", "voient"],
        "imparfait": ["voyais", "voyais", "voyait", "voyions", "voyiez", "voyaient"],
        "futur-simple": ["verrai", "verras", "verra", "verrons", "verrez", "verront"],
        "passé-simple": ["vis", "vis", "vit", "vîmes", "vîtes", "virent"],
    },
    "pouvoir": {
        "présent": ["peux", "peux", "peut", "pouvons", "pouvez", "peuvent"],
        "imparfait": ["pouvais", "pouvais", "pouvait", "pouvions", "pouviez", "pouvaient"],
        "futur-simple": ["pourrai", "pourras", "pourra", "pourrons", "pourrez", "pourront"],
        "passé-simple": ["pus", "pus", "put", "pûmes", "pûtes", "purent"],
    },
    "vouloir": {
        "présent": ["veux", "veux", "veut", "voulons", "voulez", "veulent"],
        "imparfait": ["voulais", "voulais", "voulait", "voulions", "vouliez", "voulaient"],
        "futur-simple": ["voudrai", "voudras", "voudra", "voudrons", "voudrez", "voudront"],
        "passé-simple": ["voulus", "voulus", "voulut", "voulûmes", "voulûtes", "voulurent"],
    },
    "finir": {
        "présent": ["finis", "finis", "finit", "finissons", "finissez", "finissent"],
        "imparfait": ["finissais", "finissais", "finissait", "finissions", "finissiez", "finissaient"],
        "futur-simple": ["finirai", "finiras", "finira", "finirons", "finirez", "finiront"],
        "passé-simple": ["finis", "finis", "finit", "finîmes", "finîtes", "finirent"],
    },
}


class ConjugueurLocal:
    def conjugate(self, verbe):
        verbe = verbe.strip().lower()
        if verbe in VERBES_IRREGULIERS:
            return {"moods": {"indicatif": dict(VERBES_IRREGULIERS[verbe])}}
        if verbe.endswith("er") and len(verbe) > 2:
            radical = verbe[:-2]
            modes = {}
            for temps, terminaisons in TERMINAISONS_ER.items():
                modes[temps] = [
                    f"{PRONOMS[i]} {radical}{term}"
                    for i, term in enumerate(terminaisons)
                ]
            return {"moods": {"indicatif": modes}}
        raise ValueError(f"Verbe '{verbe}' non reconnu")


conjugateur = ConjugueurLocal()


BADGES = {
    "alphabet":  {"nom": "🔤 Maître de l'Alphabet",  "desc": "Voir les 26 lettres"},
    "quiz10":    {"nom": "🎮 Quiz Master",            "desc": "10 bonnes réponses quiz"},
    "animaux10": {"nom": "🦁 Ami des Animaux",        "desc": "10 bonnes réponses animaux"},
    "memory10":  {"nom": "🧠 Mémoire d'Éléphant",     "desc": "Terminer le jeu"},
    "conteur":   {"nom": "📖 Conteur",                "desc": "Lire tous les contes"},
    "explo":     {"nom": "🌍 Explorateur",            "desc": "Visiter les 54 pays"},
    "geo20":     {"nom": "🗺️ Géographe",             "desc": "20 bonnes réponses géo"},
    "tables50":  {"nom": "✖️ Roi des Tables",         "desc": "50 bonnes réponses"},
    "horloge":   {"nom": "⏰ Maître du Temps",        "desc": "20 bonnes heures"},
    "dictee10":  {"nom": "📝 Orthographe Parfaite",   "desc": "10 bonnes dictées"},
}


alphabet_data = {
    "A": "Ananas", "B": "Banane", "C": "Chat", "D": "Dromadaire", "E": "Éléphant",
    "F": "Fourmi", "G": "Girafe", "H": "Hippopotame", "I": "Iguane", "J": "Jus",
    "K": "Kiwi", "L": "Lion", "M": "Mangue", "N": "Nuage", "O": "Oiseau",
    "P": "Papaye", "Q": "Quatre", "R": "Rhinocéros", "S": "Singe", "T": "Tortue",
    "U": "Uniforme", "V": "Vache", "W": "Wagon", "X": "Xylophone", "Y": "Yack",
    "Z": "Zèbre",
}

questions_data = [
    ("Combien font 2 + 2 ?", "4"), ("Combien font 3 + 1 ?", "4"),
    ("Combien font 5 - 2 ?", "3"), ("Combien font 6 - 1 ?", "5"),
    ("Combien font 3 + 3 ?", "6"), ("Combien font 7 - 3 ?", "4"),
    ("Combien font 5 + 5 ?", "10"), ("Combien font 8 - 4 ?", "4"),
    ("Combien font 6 + 2 ?", "8"), ("Combien font 9 - 5 ?", "4"),
]

animaux_jeu = {
    "Lion": "🦁", "Éléphant": "🐘", "Girafe": "🦒", "Singe": "🐒",
    "Zèbre": "🦓", "Crocodile": "🐊", "Hippopotame": "🦛", "Léopard": "🐆",
}

contes_data = [
    {"titre": "Anansi l'Araignée Maligne",
     "histoire": "Anansi est une araignée très intelligente d'Afrique de l'Ouest. Un jour, elle voulut rassembler toute la sagesse du monde dans une calebasse. Mais en grimpant sur un arbre, la calebasse tomba et se brisa, partageant ainsi la sagesse entre tous les êtres humains.",
     "video_link": "https://www.youtube.com/watch?v=SPhvOor9oE0"},
    {"titre": "Le Lièvre Leuk et l'Éléphant",
     "histoire": "Le lièvre Leuk est petit mais très rusé. Face à l'éléphant qui se croyait le plus fort, Leuk lui proposa un défi d'endurance. Par sa ruse, Leuk prouva que l'intelligence est souvent plus forte que la force brute !",
     "video_link": "https://www.youtube.com/watch?v=68mYj_w0P1s"},
    {"titre": "La Hyène et le Lièvre",
     "histoire": "La hyène voulait toujours voler la nourriture du lièvre. Un jour, le lièvre lui proposa de cultiver ensemble un champ. Grâce à sa ruse, le lièvre récolta le meilleur et la hyène comprit que patience et honnêteté paient toujours.",
     "video_link": "https://www.youtube.com/watch?v=SPhvOor9oE0"},
    {"titre": "Le Baobab Magique",
     "histoire": "Dans un village, un vieux baobab exauçait les vœux des enfants sages. Un petit garçon nommé Kofi alla lui demander la sagesse. Le baobab lui répondit : « La sagesse vient de l'écoute, du respect et du partage. »",
     "video_link": "https://www.youtube.com/watch?v=68mYj_w0P1s"},
]

english_curriculum = {
    "1ère - 2ème Année (CP/CE1)": {
        "mots": [
            {"en": "Hello", "fr": "Bonjour", "emoji": "👋"},
            {"en": "Goodbye", "fr": "Au revoir", "emoji": "🏃‍♂️"},
            {"en": "Red, Blue, Green", "fr": "Rouge, Bleu, Vert", "emoji": "🎨"},
            {"en": "One, Two, Three", "fr": "Un, Deux, Trois", "emoji": "🔢"},
            {"en": "Thank you", "fr": "Merci", "emoji": "🙏"},
            {"en": "Please", "fr": "S'il te plaît", "emoji": "🙂"},
        ],
        "video_link": "https://www.youtube.com/watch?v=dUXk8Nc5qGo",
    },
    "3ème - 4ème Année (CE2/CM1)": {
        "mots": [
            {"en": "What is your name?", "fr": "Comment tu t'appelles ?", "emoji": "🗣️"},
            {"en": "Father and Mother", "fr": "Père et Mère", "emoji": "👨‍👩‍👧‍👦"},
            {"en": "I like fruits", "fr": "J'aime les fruits", "emoji": "🍎"},
            {"en": "How old are you?", "fr": "Quel âge as-tu ?", "emoji": "🎂"},
        ],
        "video_link": "https://www.youtube.com/watch?v=QA48wTGbU7A",
    },
}

francais_curriculum = {
    "1ère et 2ème Année Primaire": {"leçons": [
        {"titre": "Leçon 1 : L'Alphabet et les Sons",
         "regle": "L'alphabet français comporte 26 lettres. 6 voyelles (A, E, I, O, U, Y) et 20 consonnes.",
         "exemple": "Voyelles : ami, école, orange. Consonnes : ballon, chat, porte.", "emoji": "🔤"},
        {"titre": "Leçon 2 : Les Syllabes",
         "regle": "Une syllabe est une partie d'un mot prononcée en une seule fois.",
         "exemple": "maman (ma-man), papa (pa-pa), table (ta-ble), école (é-co-le).", "emoji": "🗣️"},
        {"titre": "Leçon 3 : Le Mot",
         "regle": "Un mot est un ensemble de lettres qui a un sens.",
         "exemple": "Personne (maman), Animal (mouton), Chose (table), Lieu (école).", "emoji": "📖"},
        {"titre": "Leçon 4 : La Phrase",
         "regle": "Une phrase commence par une majuscule et finit par un point.",
         "exemple": "Le garçon joue. / La fille lit un livre.", "emoji": "✍️"},
        {"titre": "Leçon 5 : Le Nom",
         "regle": "Commun / Propre (majuscule).",
         "exemple": "Commun : garçon, livre. Propre : Guinée, Conakry.", "emoji": "🏷️"},
    ]},
    "3ème et 4ème Année Primaire": {"leçons": [
        {"titre": "Leçon 1 : Le Nom",
         "regle": "Commun = général. Propre = particulier avec majuscule.",
         "exemple": "Communs : élève, village. Propres : Mamadou, Guinée.", "emoji": "🇬🇳"},
        {"titre": "Leçon 2 : Les Articles",
         "regle": "Définis (le, la, les, l') / Indéfinis (un, une, des).",
         "exemple": "le livre, une fille, des mangues.", "emoji": "📌"},
        {"titre": "Leçon 3 : Genre et Nombre",
         "regle": "Masculin/Féminin, Singulier/Pluriel.",
         "exemple": "un garçon / une fille. le livre / les livres.", "emoji": "👫"},
        {"titre": "Leçon 4 : L'Adjectif",
         "regle": "Donne une qualité, s'accorde en genre et nombre.",
         "exemple": "un grand arbre, une belle maison.", "emoji": "🎨"},
        {"titre": "Leçon 5 : Le Verbe et le Sujet",
         "regle": "Verbe = action. Sujet fait l'action.",
         "exemple": "Moussa mange. → Sujet : Moussa", "emoji": "🏃‍♂️"},
        {"titre": "Leçon 6 : Présent 1er groupe",
         "regle": "Terminaisons : -e, -es, -e, -ons, -ez, -ent.",
         "exemple": "chanter : je chante, tu chantes…", "emoji": "🗣️"},
        {"titre": "Leçon 7 : Phrases & Vocabulaire",
         "regle": "Déclarative, interrogative, exclamative. Synonymes, contraires.",
         "exemple": "heureux = content. grand / petit.", "emoji": "🔄"},
    ]},
    "5ème et 6ème Année Primaire": {"leçons": [
        {"titre": "Leçon 1 : Les Classes de Mots",
         "regle": "nom, déterminant, adjectif, pronom, verbe, adverbe…",
         "exemple": "'Le petit garçon joue dans la cour.'", "emoji": "🗂️"},
        {"titre": "Leçon 2 : Déterminants et Pronoms",
         "regle": "Déterminants accompagnent le nom. Pronom le remplace.",
         "exemple": "Mon cahier. Mamadou lit → Il lit.", "emoji": "👤"},
        {"titre": "Leçon 3 : Groupes et Temps",
         "regle": "1er (-er), 2e (-ir), 3e (autres).",
         "exemple": "parler, finir, prendre.", "emoji": "⚙️"},
        {"titre": "Leçon 4 : COD / COI",
         "regle": "COD : qui/quoi. COI : à qui/à quoi.",
         "exemple": "Aïssatou mange une mangue. (COD)", "emoji": "🎯"},
        {"titre": "Leçon 5 : Accords et Ponctuation",
         "regle": "Verbe-sujet, adjectif-nom. Signes : . , ; : ? ! « »",
         "exemple": "ver, verre, vert (homonymes).", "emoji": "📚"},
    ]},
}

# ---- 54 PAYS D'AFRIQUE ----
afrique_geographie = {
    "Algérie": {"capitale": "Alger", "regions": "58 wilayas", "superficie": "2 381 741 km²",
                "situation": "Afrique du Nord", "population": "44 M", "langues": "Arabe, Français", "emoji": "🇩🇿"},
    "Égypte": {"capitale": "Le Caire", "regions": "27 gouv.", "superficie": "1 001 450 km²",
               "situation": "Afrique du Nord", "population": "104 M", "langues": "Arabe", "emoji": "🇪🇬"},
    "Libye": {"capitale": "Tripoli", "regions": "22 districts", "superficie": "1 759 540 km²",
              "situation": "Afrique du Nord", "population": "7 M", "langues": "Arabe", "emoji": "🇱🇾"},
    "Maroc": {"capitale": "Rabat", "regions": "12 régions", "superficie": "446 550 km²",
              "situation": "Afrique du Nord", "population": "37 M", "langues": "Arabe, Français", "emoji": "🇲🇦"},
    "Soudan": {"capitale": "Khartoum", "regions": "18 États", "superficie": "1 861 484 km²",
               "situation": "Afrique du Nord", "population": "45 M", "langues": "Arabe, Anglais", "emoji": "🇸🇩"},
    "Tunisie": {"capitale": "Tunis", "regions": "24 gouv.", "superficie": "163 610 km²",
                "situation": "Afrique du Nord", "population": "12 M", "langues": "Arabe, Français", "emoji": "🇹🇳"},
    "Bénin": {"capitale": "Porto-Novo", "regions": "12 dép.", "superficie": "112 622 km²",
              "situation": "Afrique de l'Ouest", "population": "12 M", "langues": "Français", "emoji": "🇧🇯"},
    "Burkina Faso": {"capitale": "Ouagadougou", "regions": "45 provinces", "superficie": "274 200 km²",
                     "situation": "Afrique de l'Ouest", "population": "21 M", "langues": "Français", "emoji": "🇧🇫"},
    "Cap-Vert": {"capitale": "Praia", "regions": "22 munic.", "superficie": "4 033 km²",
                 "situation": "Afrique de l'Ouest", "population": "550k", "langues": "Portugais", "emoji": "🇨🇻"},
    "Côte d'Ivoire": {"capitale": "Yamoussoukro", "regions": "31 régions", "superficie": "322 463 km²",
                      "situation": "Afrique de l'Ouest", "population": "28 M", "langues": "Français", "emoji": "🇨🇮"},
    "Gambie": {"capitale": "Banjul", "regions": "5 régions", "superficie": "11 295 km²",
               "situation": "Afrique de l'Ouest", "population": "2,4 M", "langues": "Anglais", "emoji": "🇬🇲"},
    "Ghana": {"capitale": "Accra", "regions": "16 régions", "superficie": "238 533 km²",
              "situation": "Afrique de l'Ouest", "population": "31 M", "langues": "Anglais", "emoji": "🇬🇭"},
    "Guinée": {"capitale": "Conakry", "regions": "8 régions", "superficie": "245 857 km²",
               "situation": "Afrique de l'Ouest", "population": "13,8 M", "langues": "Français", "emoji": "🇬🇳"},
    "Guinée-Bissau": {"capitale": "Bissau", "regions": "9 régions", "superficie": "36 125 km²",
                      "situation": "Afrique de l'Ouest", "population": "2 M", "langues": "Portugais", "emoji": "🇬🇼"},
    "Liberia": {"capitale": "Monrovia", "regions": "15 comtés", "superficie": "111 369 km²",
                "situation": "Afrique de l'Ouest", "population": "5 M", "langues": "Anglais", "emoji": "🇱🇷"},
    "Mali": {"capitale": "Bamako", "regions": "19 régions", "superficie": "1 241 238 km²",
             "situation": "Afrique de l'Ouest", "population": "22,5 M", "langues": "Français", "emoji": "🇲🇱"},
    "Mauritanie": {"capitale": "Nouakchott", "regions": "15 wilayas", "superficie": "1 030 700 km²",
                   "situation": "Afrique de l'Ouest", "population": "4,6 M", "langues": "Arabe", "emoji": "🇲🇷"},
    "Niger": {"capitale": "Niamey", "regions": "7 régions", "superficie": "1 267 000 km²",
              "situation": "Afrique de l'Ouest", "population": "24 M", "langues": "Français", "emoji": "🇳🇪"},
    "Nigeria": {"capitale": "Abuja", "regions": "36 États", "superficie": "923 768 km²",
                "situation": "Afrique de l'Ouest", "population": "206 M", "langues": "Anglais", "emoji": "🇳🇬"},
    "Sénégal": {"capitale": "Dakar", "regions": "14 régions", "superficie": "196 722 km²",
                "situation": "Afrique de l'Ouest", "population": "17,3 M", "langues": "Français", "emoji": "🇸🇳"},
    "Sierra Leone": {"capitale": "Freetown", "regions": "5 prov.", "superficie": "71 740 km²",
                     "situation": "Afrique de l'Ouest", "population": "8 M", "langues": "Anglais", "emoji": "🇸🇱"},
    "Togo": {"capitale": "Lomé", "regions": "5 régions", "superficie": "56 785 km²",
             "situation": "Afrique de l'Ouest", "population": "8 M", "langues": "Français", "emoji": "🇹🇬"},
    "Angola": {"capitale": "Luanda", "regions": "18 prov.", "superficie": "1 246 700 km²",
               "situation": "Afrique Centrale", "population": "33 M", "langues": "Portugais", "emoji": "🇦🇴"},
    "Cameroun": {"capitale": "Yaoundé", "regions": "10 régions", "superficie": "475 442 km²",
                 "situation": "Afrique Centrale", "population": "27,9 M", "langues": "Français, Anglais", "emoji": "🇨🇲"},
    "RCA": {"capitale": "Bangui", "regions": "20 préf.", "superficie": "622 984 km²",
            "situation": "Afrique Centrale", "population": "5 M", "langues": "Français", "emoji": "🇨🇫"},
    "Tchad": {"capitale": "N'Djamena", "regions": "23 régions", "superficie": "1 284 000 km²",
              "situation": "Afrique Centrale", "population": "16 M", "langues": "Français, Arabe", "emoji": "🇹🇩"},
    "Congo": {"capitale": "Brazzaville", "regions": "12 dép.", "superficie": "342 000 km²",
              "situation": "Afrique Centrale", "population": "5,5 M", "langues": "Français", "emoji": "🇨🇬"},
    "RD Congo": {"capitale": "Kinshasa", "regions": "26 prov.", "superficie": "2 344 858 km²",
                 "situation": "Afrique Centrale", "population": "90 M", "langues": "Français", "emoji": "🇨🇩"},
    "Guinée Équatoriale": {"capitale": "Malabo", "regions": "8 prov.", "superficie": "28 051 km²",
                            "situation": "Afrique Centrale", "population": "1,4 M", "langues": "Espagnol", "emoji": "🇬🇶"},
    "Gabon": {"capitale": "Libreville", "regions": "9 prov.", "superficie": "267 668 km²",
              "situation": "Afrique Centrale", "population": "2,3 M", "langues": "Français", "emoji": "🇬🇦"},
    "São Tomé": {"capitale": "São Tomé", "regions": "7 districts", "superficie": "1 001 km²",
                 "situation": "Afrique Centrale", "population": "220k", "langues": "Portugais", "emoji": "🇸🇹"},
    "Burundi": {"capitale": "Gitega", "regions": "18 prov.", "superficie": "27 834 km²",
                "situation": "Afrique de l'Est", "population": "12 M", "langues": "Kirundi", "emoji": "🇧🇮"},
    "Comores": {"capitale": "Moroni", "regions": "3 îles", "superficie": "2 235 km²",
                "situation": "Afrique de l'Est", "population": "850k", "langues": "Comorien", "emoji": "🇰🇲"},
    "Djibouti": {"capitale": "Djibouti", "regions": "6 régions", "superficie": "23 200 km²",
                 "situation": "Afrique de l'Est", "population": "1 M", "langues": "Français", "emoji": "🇩🇯"},
    "Érythrée": {"capitale": "Asmara", "regions": "6 régions", "superficie": "117 600 km²",
                 "situation": "Afrique de l'Est", "population": "3,6 M", "langues": "Tigrinya", "emoji": "🇪🇷"},
    "Éthiopie": {"capitale": "Addis-Abeba", "regions": "11 États", "superficie": "1 104 300 km²",
                 "situation": "Afrique de l'Est", "population": "117 M", "langues": "Amharique", "emoji": "🇪🇹"},
    "Kenya": {"capitale": "Nairobi", "regions": "47 comtés", "superficie": "580 367 km²",
              "situation": "Afrique de l'Est", "population": "54 M", "langues": "Swahili", "emoji": "🇰🇪"},
    "Madagascar": {"capitale": "Antananarivo", "regions": "22 régions", "superficie": "587 041 km²",
                   "situation": "Afrique de l'Est", "population": "28 M", "langues": "Malgache", "emoji": "🇲🇬"},
    "Malawi": {"capitale": "Lilongwe", "regions": "28 districts", "superficie": "118 484 km²",
               "situation": "Afrique de l'Est", "population": "19 M", "langues": "Anglais", "emoji": "🇲🇼"},
    "Maurice": {"capitale": "Port-Louis", "regions": "9 districts", "superficie": "2 040 km²",
                "situation": "Afrique de l'Est", "population": "1,3 M", "langues": "Anglais", "emoji": "🇲🇺"},
    "Mozambique": {"capitale": "Maputo", "regions": "11 prov.", "superficie": "801 590 km²",
                   "situation": "Afrique de l'Est", "population": "31 M", "langues": "Portugais", "emoji": "🇲🇿"},
    "Rwanda": {"capitale": "Kigali", "regions": "5 prov.", "superficie": "26 338 km²",
               "situation": "Afrique de l'Est", "population": "13 M", "langues": "Kinyarwanda", "emoji": "🇷🇼"},
    "Seychelles": {"capitale": "Victoria", "regions": "26 districts", "superficie": "455 km²",
                   "situation": "Afrique de l'Est", "population": "100k", "langues": "Créole", "emoji": "🇸🇨"},
    "Somalie": {"capitale": "Mogadiscio", "regions": "18 régions", "superficie": "637 657 km²",
                "situation": "Afrique de l'Est", "population": "16 M", "langues": "Somali", "emoji": "🇸🇴"},
    "Soudan du Sud": {"capitale": "Djouba", "regions": "10 États", "superficie": "619 745 km²",
                      "situation": "Afrique de l'Est", "population": "11 M", "langues": "Anglais", "emoji": "🇸🇸"},
    "Tanzanie": {"capitale": "Dodoma", "regions": "31 régions", "superficie": "945 087 km²",
                 "situation": "Afrique de l'Est", "population": "60 M", "langues": "Swahili", "emoji": "🇹🇿"},
    "Ouganda": {"capitale": "Kampala", "regions": "135 districts", "superficie": "241 550 km²",
                "situation": "Afrique de l'Est", "population": "45 M", "langues": "Anglais", "emoji": "🇺🇬"},
    "Zambie": {"capitale": "Lusaka", "regions": "10 prov.", "superficie": "752 614 km²",
               "situation": "Afrique de l'Est", "population": "18 M", "langues": "Anglais", "emoji": "🇿🇲"},
    "Zimbabwe": {"capitale": "Harare", "regions": "8 prov.", "superficie": "390 757 km²",
                 "situation": "Afrique de l'Est", "population": "15 M", "langues": "Anglais", "emoji": "🇿🇼"},
    "Afrique du Sud": {"capitale": "Pretoria", "regions": "9 prov.", "superficie": "1 219 090 km²",
                       "situation": "Afrique Australe", "population": "60 M", "langues": "11 langues", "emoji": "🇿🇦"},
    "Botswana": {"capitale": "Gaborone", "regions": "16 districts", "superficie": "581 730 km²",
                 "situation": "Afrique Australe", "population": "2,4 M", "langues": "Anglais", "emoji": "🇧🇼"},
    "Eswatini": {"capitale": "Mbabane", "regions": "4 régions", "superficie": "17 363 km²",
                 "situation": "Afrique Australe", "population": "1,2 M", "langues": "Anglais", "emoji": "🇸🇿"},
    "Lesotho": {"capitale": "Maseru", "regions": "10 districts", "superficie": "30 355 km²",
                "situation": "Afrique Australe", "population": "2,1 M", "langues": "Anglais", "emoji": "🇱🇸"},
    "Namibie": {"capitale": "Windhoek", "regions": "14 régions", "superficie": "825 615 km²",
                "situation": "Afrique Australe", "population": "2,5 M", "langues": "Anglais", "emoji": "🇳🇦"},
}

couleurs_data = {
    "Rouge": "#E74C3C", "Bleu": "#3498DB", "Vert": "#2ECC71",
    "Jaune": "#F1C40F", "Orange": "#E67E22", "Violet": "#9B59B6",
    "Rose": "#FF69B4", "Noir": "#000000", "Blanc": "#FFFFFF", "Marron": "#8B4513",
}
formes_data = {
    "Cercle": "⭕", "Carré": "⬛", "Triangle": "🔺", "Rectangle": "▬",
    "Étoile": "⭐", "Cœur": "❤️", "Losange": "🔷", "Hexagone": "⬡",
}
jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
mois_annee = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
              "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
corps_humain = {
    "Tête": "👤", "Yeux": "👁️", "Nez": "👃", "Bouche": "👄",
    "Oreilles": "👂", "Main": "✋", "Pied": "🦶", "Bras": "💪",
    "Jambe": "🦵", "Cœur": "❤️", "Cerveau": "🧠", "Dent": "🦷",
}
dict_temps = {
    "Présent": ("indicatif", "présent"),
    "Imparfait": ("indicatif", "imparfait"),
    "Futur simple": ("indicatif", "futur-simple"),
    "Passé simple": ("indicatif", "passé-simple"),
}


dictee_mots = ["chat", "chien", "maison", "école", "livre", "table", "fleur",
               "jardin", "soleil", "lune", "étoile", "nuage", "oiseau", "poisson",
               "mangue", "banane", "orange", "voiture", "vélo", "ballon"]



# Couleurs des boutons de catégories (mêmes valeurs que la version PC)
MENU_BLUE = "#1565C0"
CAT_BG = "#FFFFFF"
CAT_FG = "#1565C0"
CAT_ACTIVE_BG = "#E3F2FD"

CATEGORIES = {
    "Apprendre": {
        "emoji": "📚", "color": CAT_BG,
        "items": [
            ("📚 Apprendre l'Alphabet", "alphabet"),
            ("🔢 Compter les Chiffres", "chiffres"),
            ("🎨 Couleurs & Formes", "couleurs"),
            ("📅 Jours & Mois", "calendrier"),
            ("🧪 Sciences (Corps Humain)", "sciences"),
            ("✖️ Tables de Multiplication", "tables"),
            ("⏰ Lire l'Heure", "heure"),
        ],
    },
    "Jouer": {
        "emoji": "🎮", "color": CAT_BG,
        "items": [
            ("🦁 Identifier les Animaux", "animaux"),
            ("🧠 Jeu de Mémoire", "memory"),
            ("🎮 Quiz Mathématiques", "quiz"),
            ("🗺️ Quiz Géographie", "geo_quiz"),
            ("📝 Mini-dictée", "dictee"),
        ],
    },
    "Langues": {
        "emoji": "🌐", "color": CAT_BG,
        "items": [
            ("🇫🇷 Français (Grammaire)", "francais"),
            ("🇬🇧 Anglais (Cours)", "anglais"),
        ],
    },
    "Découvrir": {
        "emoji": "🌍", "color": CAT_BG,
        "items": [
            ("🌍 Contes Africains", "contes"),
            ("🌍 Géographie (54 pays)", "geographie"),
        ],
    },
    "Mon Espace": {
        "emoji": "🏆", "color": CAT_BG,
        "items": [
            ("🏆 Mon Progrès", "progres"),
            ("⚙️ Paramètres", "parametres"),
        ],
    },
}



def nombre_en_lettres(n):
    if n == 0:
        return "zéro"
    if n == 1000:
        return "mille"
    unites = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"]
    particuliers = ["dix", "onze", "douze", "treize", "quatorze", "quinze",
                    "seize", "dix-sept", "dix-huit", "dix-neuf"]
    dizaines = ["", "dix", "vingt", "trente", "quarante", "cinquante",
                "soixante", "soixante-dix", "quatre-vingt", "quatre-vingt-dix"]
    res = []
    c, r = n // 100, n % 100
    if c > 0:
        res.append((unites[c] + "-cent") if c > 1 else "cent")
    if r > 0:
        d, u = r // 10, r % 10
        if d == 0:
            res.append(unites[u])
        elif d == 1:
            res.append(particuliers[u])
        elif d == 7:
            res.append("soixante-et-onze" if u == 1 else "soixante-" + particuliers[u])
        elif d == 8:
            res.append("quatre-vingts" if u == 0 else "quatre-vingt-" + unites[u])
        elif d == 9:
            res.append("quatre-vingt-" + particuliers[u])
        else:
            if u == 1:
                res.append(dizaines[d] + "-et-un")
            elif u > 1:
                res.append(dizaines[d] + "-" + unites[u])
            else:
                res.append(dizaines[d])
    return " ".join(res)




def generer_question_math():
    a, b = random.randint(1, 10), random.randint(1, 10)
    if random.random() < 0.5:
        return (f"Combien font {a} + {b} ?", str(a + b))
    a, b = max(a, b), min(a, b)
    return (f"Combien font {a} - {b} ?", str(a - b))



# ==========================================================================
# EMOJIS : sur Android, la police par défaut de Kivy ne sait pas afficher les
# emojis. Ils sont donc affichés comme IMAGES PNG (dossier assets/emoji/),
# générées par generer_emojis.py. Les fonctions ci-dessous font le lien.
# ==========================================================================
import re

_EMOJI_CHARS = ("\U0001F000-\U0001FAFF←-⇿⌀-⏿■-◿"
                "☀-➿⬀-⯿️‍⃣")
_RE_DEBUT = re.compile("^([" + _EMOJI_CHARS + "]+)\\s*(.*)$", re.S)
_RE_TOUS = re.compile("[" + _EMOJI_CHARS + "]+")


def separer_emoji(texte):
    """'🦁 Lion' -> ('🦁', 'Lion') ; 'Lion' -> ('', 'Lion')."""
    m = _RE_DEBUT.match(texte)
    return (m.group(1), m.group(2)) if m else ("", texte)


def sans_emoji(texte):
    """Retire tous les emojis (pour la voix et les titres de fenêtres)."""
    return re.sub(r"\s{2,}", " ", _RE_TOUS.sub("", texte)).strip()


def emoji_fichier(emoji):
    """Chemin relatif de l'image PNG d'un emoji (codes Unicode séparés par '-')."""
    return "assets/emoji/" + "-".join(f"{ord(c):x}" for c in emoji) + ".png"


# Emojis utilisés directement par l'interface (hors données ci-dessus)
EMOJIS_UI = ["❓", "🕐", "👋", "🏠", "🌍", "🎖️", "🎉", "✅", "❌", "🔊", "🎬",
             "👀", "✨", "🗑️", "🚪", "ℹ️", "⚙️", "🏆", "🎲", "🔄", "🏢", "🌍",
             "📐", "👥", "🗺️", "🗣️", "📋", "⬅️", "➡️", "🏅", "✖️", "⏰", "📝",
             "📖", "✨", "🌐", "🎨", "📅", "🧪", "🧠"]


def tous_les_emojis():
    """Ensemble de tous les emojis à fournir en images."""
    s = set(EMOJIS_UI)
    s.update(animaux_jeu.values())
    s.update(formes_data.values())
    s.update(corps_humain.values())
    for niv in english_curriculum.values():
        s.update(m["emoji"] for m in niv["mots"])
    for niv in francais_curriculum.values():
        s.update(l["emoji"] for l in niv["leçons"])
    s.update(p["emoji"] for p in afrique_geographie.values())
    for b in BADGES.values():
        s.add(separer_emoji(b["nom"])[0])
    for c in CATEGORIES.values():
        s.add(c["emoji"])
        for texte, _ in c["items"]:
            s.add(separer_emoji(texte)[0])
    s.discard("")
    return sorted(s)
