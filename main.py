# -*- coding: utf-8 -*-
# ==========================================================================
# NEXA KIDS AFRICA v3.0 - Édition Android / PC (Kivy)
# Traduction de la version Tkinter (mon_application.py) :
#   * mêmes modules, mêmes données (voir donnees.py), même progression/badges ;
#   * interface tactile (boutons larges, défilement, menu latéral) ;
#   * voix : synthèse vocale Android (plyer) ou pyttsx3 sur PC ;
#   * emojis affichés comme images (assets/emoji) car la police Kivy ne les
#     contient pas ;
#   * sauvegarde de la progression dans le dossier privé de l'application.
# Lancer sur PC :  python main.py
# ==========================================================================
import os
import json
import random
import threading
import webbrowser
from functools import partial
from types import SimpleNamespace

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex as hexc
from kivy.utils import platform

from donnees import (
    BADGES, CATEGORIES, CAT_ACTIVE_BG, CAT_BG, CAT_FG, MENU_BLUE,
    afrique_geographie, alphabet_data, animaux_jeu, conjugateur, contes_data,
    corps_humain, couleurs_data, dict_temps, dictee_mots, emoji_fichier,
    english_curriculum, formes_data, francais_curriculum, generer_question_math,
    jours_semaine, mois_annee, nombre_en_lettres, questions_data,
    sans_emoji, separer_emoji,
)

RACINE = os.path.dirname(os.path.abspath(__file__))
if platform in ("win", "linux", "macosx"):
    Window.size = (400, 720)          # taille « téléphone » pour tester sur PC
Window.softinput_mode = "below_target"  # le clavier ne cache pas le champ de saisie

# ==========================================================================
# PROGRESSION (même contenu que la version PC)
# ==========================================================================
DEFAULT_PROGRESSION = {
    "badges": [], "quiz_points": 0, "animaux_points": 0,
    "memory_best": 0, "sound_on": True, "lettres_vues": [],
    "pays_vus": [], "contes_lus": [], "lecons_vues": [],
    "tables_points": 0, "heures_points": 0, "geo_quiz_points": 0,
    "dictee_points": 0, "xp": 0, "niveau": 1,
}
progression = {}
CHEMIN_PROGRES = [os.path.join(os.path.expanduser("~"), ".nexa_kids_progress.json")]


def _defauts():
    return {k: (v.copy() if isinstance(v, list) else v) for k, v in DEFAULT_PROGRESSION.items()}


def charger_progression():
    progression.clear()
    try:
        with open(CHEMIN_PROGRES[0], "r", encoding="utf-8") as f:
            data = json.load(f)
        progression.update(data)
        for k, v in _defauts().items():
            progression.setdefault(k, v)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        progression.update(_defauts())


def sauvegarder_progression():
    try:
        with open(CHEMIN_PROGRES[0], "w", encoding="utf-8") as f:
            json.dump(progression, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Sauvegarde impossible : {e}")


# ==========================================================================
# VOIX
# ==========================================================================
class Voix:
    """Android : synthèse vocale du téléphone (plyer). PC : pyttsx3 (facultatif)."""

    def __init__(self):
        self.tts = None
        self.moteur = None
        self.verrou = threading.Lock()
        if platform == "android":
            try:
                from plyer import tts
                self.tts = tts
            except Exception as e:
                print(f"Audio indisponible : {e}")
        else:
            try:
                import pyttsx3
                self.moteur = pyttsx3.init()
                self.moteur.setProperty("rate", 135)
                for v in (self.moteur.getProperty("voices") or []):
                    blob = f"{getattr(v, 'languages', '')} {getattr(v, 'name', '')}".lower()
                    if "fr" in blob or "french" in blob or "français" in blob:
                        self.moteur.setProperty("voice", v.id)
                        break
            except Exception as e:
                print(f"Audio PC indisponible : {e}")
                self.moteur = None

    def dire(self, texte):
        if not progression.get("sound_on", True):
            print(f"[Muet] {texte}")
            return
        texte = sans_emoji(texte)
        if not texte:
            return
        if self.tts is not None:
            try:
                try:
                    self.tts.speak(message=texte, locale="fr_FR")
                except TypeError:          # ancienne version de plyer sans « locale »
                    self.tts.speak(texte)
            except Exception as e:
                print(f"Erreur audio : {e}")
        elif self.moteur is not None:
            threading.Thread(target=self._lire_pc, args=(texte,), daemon=True).start()
        else:
            print(f"[Texte] {texte}")

    def _lire_pc(self, texte):
        with self.verrou:
            try:
                self.moteur.say(texte)
                self.moteur.runAndWait()
            except Exception as e:
                print(f"Erreur audio : {e}")


voix = Voix()


def parler(texte, delai=0.0):
    """Lit un texte ; delai > 0 : après un court délai (comme app.after(100, …))."""
    if delai:
        Clock.schedule_once(lambda dt: voix.dire(texte), delai)
    else:
        voix.dire(texte)


# ==========================================================================
# OUTILS D'INTERFACE
# ==========================================================================
class Et(Label):
    """Étiquette qui retourne à la ligne et s'ajuste en hauteur."""

    def __init__(self, **kw):
        kw.setdefault("size_hint_y", None)
        kw.setdefault("halign", "center")
        kw.setdefault("valign", "middle")
        kw.setdefault("color", hexc("#222222"))
        kw.setdefault("font_size", sp(16))
        super().__init__(**kw)
        self.bind(width=self._largeur, texture_size=self._hauteur)
        self._largeur()

    def _largeur(self, *a):
        self.text_size = (self.width, None)

    def _hauteur(self, *a):
        self.height = self.texture_size[1] + dp(8)


def et(texte="", taille=16, couleur="#222222", gras=False, italique=False, align="center", **kw):
    return Et(text=texte, font_size=sp(taille), color=hexc(couleur), bold=gras,
              italic=italique, halign=align, **kw)


class Bouton(Button):
    """Bouton coloré, arrondi, avec effet d'appui ; bordure et barre facultatives."""

    def __init__(self, fond="#1565C0", couleur_texte="#FFFFFF", bordure=None, barre=None, **kw):
        kw.setdefault("size_hint_y", None)
        kw.setdefault("height", dp(54))
        kw.setdefault("font_size", sp(17))
        kw.setdefault("bold", True)
        kw["color"] = hexc(couleur_texte)
        super().__init__(background_normal="", background_down="",
                         background_color=(0, 0, 0, 0), **kw)
        self.fond = hexc(fond)
        with self.canvas.before:
            self._c = Color(*self.fond)
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            if bordure:
                Color(*hexc(bordure))
                self._l = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(12)),
                               width=dp(1.6))
            else:
                self._l = None
            if barre:
                Color(*hexc(barre))
                self._b = Rectangle(pos=self.pos, size=(dp(5), self.height))
            else:
                self._b = None
        self.bind(pos=self._maj, size=self._maj, state=self._etat)

    def _maj(self, *a):
        self._r.pos, self._r.size = self.pos, self.size
        if self._l is not None:
            self._l.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(12))
        if self._b is not None:
            self._b.pos, self._b.size = self.pos, (dp(5), self.height)

    def _etat(self, *a):
        r, g, b, _ = self.fond
        self._c.rgba = (r * .8, g * .8, b * .8, 1) if self.state == "down" else self.fond


class BoutonEmoji(Bouton):
    """Bouton avec une image d'emoji.
    mode='icone'  : emoji seul, centré (jeu des animaux, cartes mémoire) ;
    mode='gauche' : emoji à gauche, texte aligné à gauche (menus)."""

    def __init__(self, emoji="", mode="gauche", **kw):
        self.mode = mode
        super().__init__(**kw)
        self.img = Image(source=self._chemin(emoji), size_hint=(None, None))
        self.add_widget(self.img)
        self.bind(pos=self._place, size=self._place)
        if mode == "gauche":
            self.halign = "left"
            self.valign = "middle"
            self.bind(size=self._texte)
        self._place()

    @staticmethod
    def _chemin(emoji):
        return os.path.join(RACINE, emoji_fichier(emoji)) if emoji else ""

    def _texte(self, *a):
        self.text_size = (self.width, self.height)
        self.padding_x = self.height * 0.58 + dp(30)

    def _place(self, *a):
        if self.mode == "icone":
            s = min(self.height, self.width) * 0.66
            self.img.size = (s, s)
            self.img.center = self.center
        else:
            s = self.height * 0.58
            self.img.size = (s, s)
            self.img.x = self.x + dp(16)
            self.img.center_y = self.center_y

    def set_emoji(self, emoji):
        self.img.source = self._chemin(emoji)
        self.img.opacity = 1 if emoji else 0


def image_emoji(emoji, taille=48):
    """Emoji centré (image carrée) à insérer dans une colonne."""
    boite = AnchorLayout(size_hint_y=None, height=dp(taille + 8))
    img = Image(source=os.path.join(RACINE, emoji_fichier(emoji)) if emoji else "",
                size_hint=(None, None), size=(dp(taille), dp(taille)))
    boite.add_widget(img)
    boite.img = img
    return boite


def ligne_icone(emoji, texte, taille=15, couleur="#222222"):
    """Ligne : petite image d'emoji + texte aligné à gauche."""
    ligne = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(taille * 2.1),
                      spacing=dp(10))
    img = Image(source=os.path.join(RACINE, emoji_fichier(emoji)) if emoji else "",
                size_hint=(None, 1), width=dp(taille * 1.7))
    lab = Label(text=texte, font_size=sp(taille), color=hexc(couleur), halign="left",
                valign="middle")
    lab.bind(size=lambda w, v: setattr(w, "text_size", (w.width, w.height)))
    ligne.add_widget(img)
    ligne.add_widget(lab)
    ligne.lab = lab
    ligne.img = img
    return ligne


class Carte(BoxLayout):
    """Zone à fond coloré arrondi (remplace Frame/Label avec relief)."""

    def __init__(self, fond="#FFFFFF", bordure="#CCCCCC", **kw):
        kw.setdefault("orientation", "vertical")
        kw.setdefault("size_hint_y", None)
        kw.setdefault("padding", dp(12))
        kw.setdefault("spacing", dp(6))
        super().__init__(**kw)
        with self.canvas.before:
            Color(*hexc(fond))
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            Color(*hexc(bordure))
            self._l = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(10)), width=dp(1.2))
        self.bind(pos=self._maj, size=self._maj, minimum_height=self.setter("height"))

    def _maj(self, *a):
        self._r.pos, self._r.size = self.pos, self.size
        self._l.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(10))


class Pastille(Widget):
    """Carré de couleur (page Couleurs)."""

    def __init__(self, couleur="#E74C3C", **kw):
        kw.setdefault("size_hint_y", None)
        kw.setdefault("height", dp(110))
        super().__init__(**kw)
        with self.canvas:
            self._c = Color(*hexc(couleur))
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
            Color(0.3, 0.3, 0.3, 1)
            self._l = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(14)), width=dp(2))
        self.bind(pos=self._maj, size=self._maj)

    def _maj(self, *a):
        self._r.pos, self._r.size = self.pos, self.size
        self._l.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(14))

    def mettre(self, couleur):
        self._c.rgba = hexc(couleur)


class Hamburger(ButtonBehavior, Widget):
    """Icône ☰ dessinée (la police Kivy n'a pas ce caractère)."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._dessiner, size=self._dessiner)

    def _dessiner(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            l, h = self.width * 0.5, dp(3)
            for dy in (-dp(8), 0, dp(8)):
                Rectangle(pos=(self.center_x - l / 2, self.center_y + dy - h / 2), size=(l, h))


def champ(**kw):
    """Zone de saisie centrée d'une ligne (remplace Entry)."""
    kw.setdefault("font_size", sp(24))
    kw.setdefault("size_hint_y", None)
    kw.setdefault("height", dp(56))
    kw.setdefault("padding", [dp(10), dp(12)])
    return TextInput(multiline=False, halign="center", write_tab=False, **kw)


class Choix(Bouton):
    """Remplace ttk.Combobox : un bouton qui ouvre une liste défilante."""

    def __init__(self, valeurs, valeur, on_choix=None, **kw):
        super().__init__(fond="#FFFFFF", couleur_texte="#222222", bordure="#7F8C8D",
                         text=valeur, **kw)
        self.valeurs = list(valeurs)
        self.valeur = valeur
        self.on_choix = on_choix
        self.bind(on_release=self.ouvrir)

    def ouvrir(self, *a):
        contenu = BoxLayout(orientation="vertical", spacing=dp(6))
        sv = ScrollView(do_scroll_x=False)
        liste = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(5))
        liste.bind(minimum_height=liste.setter("height"))
        pop = Popup(title="Choisis", content=contenu, size_hint=(0.92, 0.88))
        for v in self.valeurs:
            b = Bouton(fond="#E3F2FD", couleur_texte="#0D47A1", text=v, height=dp(48))
            b.bind(on_release=partial(self._choisi, v, pop))
            liste.add_widget(b)
        sv.add_widget(liste)
        contenu.add_widget(sv)
        fermer = Bouton(fond="#7F8C8D", text="Fermer", height=dp(46))
        fermer.bind(on_release=pop.dismiss)
        contenu.add_widget(fermer)
        pop.open()

    def _choisi(self, valeur, pop, *a):
        self.valeur = valeur
        self.text = valeur
        pop.dismiss()
        if self.on_choix:
            self.on_choix(valeur)


# ----- Messages (remplacent tkinter.messagebox) ---------------------------------
_file_messages = []
_message_actif = [False]


def message(titre, texte, auto=None, grand=False):
    """Fenêtre d'information ; affichées l'une après l'autre.
    auto : fermeture automatique après n secondes (retours de jeu)."""
    _file_messages.append((sans_emoji(titre), sans_emoji(texte) if len(texte) < 60 else texte, auto, grand))
    if not _message_actif[0]:
        _message_suivant()


def _message_suivant(*a):
    if not _file_messages:
        _message_actif[0] = False
        return
    _message_actif[0] = True
    titre, texte, auto, grand = _file_messages.pop(0)
    contenu = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(8))
    sv = ScrollView(do_scroll_x=False)
    col = BoxLayout(orientation="vertical", size_hint_y=None)
    col.bind(minimum_height=col.setter("height"))
    col.add_widget(et(texte, 17))
    sv.add_widget(col)
    contenu.add_widget(sv)
    pop = Popup(title=titre, content=contenu, size_hint=(0.9, 0.7 if grand else 0.38),
                auto_dismiss=True)
    if auto is None:
        ok = Bouton(fond=MENU_BLUE, text="OK", height=dp(48))
        ok.bind(on_release=pop.dismiss)
        contenu.add_widget(ok)
    pop.bind(on_dismiss=_message_suivant)
    pop.open()
    if auto:
        Clock.schedule_once(lambda dt: pop.dismiss(), auto)


def confirmer(titre, texte, si_oui):
    """Remplace messagebox.askyesno."""
    contenu = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(8))
    contenu.add_widget(et(texte, 17))
    boutons = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(10))
    pop = Popup(title=sans_emoji(titre), content=contenu, size_hint=(0.88, 0.34), auto_dismiss=False)
    oui = Bouton(fond="#2E7D32", text="Oui")
    non = Bouton(fond="#C62828", text="Non")
    oui.bind(on_release=lambda *a: (pop.dismiss(), si_oui()))
    non.bind(on_release=pop.dismiss)
    boutons.add_widget(oui)
    boutons.add_widget(non)
    contenu.add_widget(boutons)
    pop.open()


# ==========================================================================
# ÉTAT DU JEU (variables globales de la version PC)
# ==========================================================================
E = SimpleNamespace(
    lettre=0, chiffre=1, quiz_points=0, question=("", ""), animal="", points_animaux=0,
    conte=0, niv_en=0, mot_en=0, niv_fr=0, lecon_fr=0, couleur=0, forme=0, jour=0,
    mois=0, corps=0, table=2, table_q=("", ""), tables_points=0,
    heure={"h": 0, "m": 0}, heures_points=0, geo_q=("", "", []), geo_points=0,
    dictee_q=("", ""), dictee_points=0,
    mem_cartes=[], mem_vues=[], mem_trouvees=[], mem_bloque=False,
)
NIVEAUX_EN = list(english_curriculum.keys())
NIVEAUX_FR = list(francais_curriculum.keys())
COULEURS = list(couleurs_data.keys())
FORMES = list(formes_data.keys())
CORPS = list(corps_humain.keys())


def synchroniser_scores():
    E.quiz_points = progression["quiz_points"]
    E.points_animaux = progression["animaux_points"]
    E.tables_points = progression.get("tables_points", 0)
    E.heures_points = progression.get("heures_points", 0)
    E.geo_points = progression.get("geo_quiz_points", 0)
    E.dictee_points = progression.get("dictee_points", 0)


def ajouter_xp(points):
    progression["xp"] = progression.get("xp", 0) + points
    nouveau = 1 + progression["xp"] // 50
    if nouveau > progression.get("niveau", 1):
        progression["niveau"] = nouveau
        parler(f"Niveau {nouveau} atteint !")
    sauvegarder_progression()


def attribuer_badge(code):
    if code in BADGES and code not in progression["badges"]:
        progression["badges"].append(code)
        sauvegarder_progression()
        parler(f"Badge débloqué : {BADGES[code]['nom']}")
        message("Nouveau badge !", f"{sans_emoji(BADGES[code]['nom'])}\n{BADGES[code]['desc']}")


# ==========================================================================
# PAGES
# ==========================================================================
class Page(Screen):
    """Écran défilable : fond coloré + colonne de widgets."""

    def __init__(self, nom, fond, **kw):
        super().__init__(name=nom, **kw)
        with self.canvas.before:
            Color(*hexc(fond))
            self._fond = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._maj_fond, size=self._maj_fond)
        self.sv = ScrollView(do_scroll_x=False, bar_width=dp(4))
        self.col = BoxLayout(orientation="vertical", size_hint_y=None,
                             padding=[dp(18), dp(12)], spacing=dp(12))
        self.col.bind(minimum_height=self.col.setter("height"))
        self.sv.add_widget(self.col)
        self.add_widget(self.sv)
        self.construire()

    def _maj_fond(self, *a):
        self._fond.pos, self._fond.size = self.pos, self.size

    def ajouter(self, w):
        self.col.add_widget(w)
        return w

    def titre(self, emoji, texte, couleur="#222222", taille=22):
        if emoji:
            self.ajouter(image_emoji(emoji, 52))
        return self.ajouter(et(texte, taille, couleur, gras=True))

    def retour_accueil(self):
        b = BoutonEmoji(emoji="🏠", text="Accueil", fond="#4D4D4D", mode="gauche")
        b.bind(on_release=lambda *a: App.get_running_app().aller("accueil"))
        return self.ajouter(b)

    def action(self, texte, fond, cb, **kw):
        b = Bouton(fond=fond, text=texte, **kw)
        b.bind(on_release=lambda *a: cb())
        return self.ajouter(b)

    def on_pre_enter(self, *a):
        self.sv.scroll_y = 1
        self.rafraichir()

    def construire(self):
        pass

    def rafraichir(self):
        pass


# ---- ACCUEIL ----
class PageAccueil(Page):
    def construire(self):
        self.ajouter(et("Bienvenue sur NEXA KIDS !", 24, "#222222", gras=True))
        self.ajouter(et("Choisis une catégorie :", 16, "#555555", italique=True))
        for nom, cat in CATEGORIES.items():
            b = BoutonEmoji(emoji=cat["emoji"], text=f"{nom}   ({len(cat['items'])} modules)",
                            fond=CAT_BG, couleur_texte=CAT_FG, bordure=CAT_FG, height=dp(78),
                            font_size=sp(19))
            b.bind(on_release=partial(self._ouvrir, nom))
            self.ajouter(b)
        self.ajouter(et("Astuce : touche le bouton menu en haut à gauche", 13, "#888888", italique=True))

    def _ouvrir(self, nom, *a):
        App.get_running_app().ouvrir_categorie(nom)


# ---- SOUS-MENU (dynamique) ----
class PageSousMenu(Page):
    def construire(self):
        pass

    def charger(self, cat_name):
        self.col.clear_widgets()
        cat = CATEGORIES[cat_name]
        self.ajouter(image_emoji(cat["emoji"], 56))
        self.ajouter(et(cat_name, 26, CAT_FG, gras=True))
        self.ajouter(et("Choisis un module :", 15, CAT_FG, italique=True))
        for texte, ecran in cat["items"]:
            emoji, libelle = separer_emoji(texte)
            b = BoutonEmoji(emoji=emoji, text=libelle, fond=CAT_BG, couleur_texte=CAT_FG,
                            bordure=CAT_FG, height=dp(64), font_size=sp(17))
            b.bind(on_release=partial(self._aller, ecran))
            self.ajouter(b)
        r = BoutonEmoji(emoji="⬅️", text="Retour au menu principal", fond="#34495E",
                        couleur_texte="#64B5F6", height=dp(58))
        r.bind(on_release=lambda *a: App.get_running_app().aller("accueil"))
        self.ajouter(r)

    def _aller(self, ecran, *a):
        App.get_running_app().aller(ecran)


# ---- ALPHABET ----
class PageAlphabet(Page):
    def construire(self):
        self.titre("", "L'ALPHABET", "#800080")
        self.lbl_lettre = self.ajouter(et("", 110, "#222222", gras=True))
        self.lbl_mot = self.ajouter(et("", 30, "#222222", italique=True))
        self.action("Suivant  ›", "#0000FF", self.suivante)
        self.retour_accueil()

    def rafraichir(self):
        lettre = list(alphabet_data.keys())[E.lettre]
        self.lbl_lettre.text = lettre
        self.lbl_mot.text = alphabet_data[lettre]
        if lettre not in progression["lettres_vues"]:
            progression["lettres_vues"].append(lettre)
            sauvegarder_progression()
        if len(progression["lettres_vues"]) >= 26:
            attribuer_badge("alphabet")
        parler(f"{lettre}... comme... {alphabet_data[lettre]}", 0.1)

    def suivante(self):
        E.lettre = (E.lettre + 1) % len(alphabet_data)
        self.rafraichir()


# ---- CHIFFRES ----
class PageChiffres(Page):
    def construire(self):
        self.titre("", "APPRENDRE À COMPTER", "#222222", 22)
        self.lbl = self.ajouter(et("", 96, "#0000FF", gras=True))
        self.lbl_lettres = self.ajouter(et("", 22, "#222222", gras=True))
        self.action("Suivant  ›", "#800080", self.suivant)
        self.retour_accueil()

    def rafraichir(self):
        self.lbl.text = str(E.chiffre)
        self.lbl_lettres.text = nombre_en_lettres(E.chiffre).capitalize()
        parler(nombre_en_lettres(E.chiffre), 0.1)

    def suivant(self):
        E.chiffre = E.chiffre + 1 if E.chiffre < 1000 else 1
        self.rafraichir()


# ---- QUIZ MATHS ----
class PageQuiz(Page):
    def construire(self):
        self.titre("", "QUIZ MATHÉMATIQUES", "#222222")
        self.lbl_score = self.ajouter(et("", 18, "#222222", gras=True))
        self.lbl_question = self.ajouter(et("", 24, "#222222", gras=True))
        grille = GridLayout(cols=3, size_hint_y=None, height=dp(2 * 64 + 10), spacing=dp(10))
        for r in ["3", "4", "5", "6", "8", "10"]:
            b = Bouton(fond="#2E7D32", text=r, font_size=sp(24))
            b.bind(on_release=partial(self._rep, r))
            grille.add_widget(b)
        self.ajouter(grille)
        self.retour_accueil()

    def _rep(self, r, *a):
        self.verifier(r)

    def rafraichir(self):
        self.lbl_score.text = f"Score : {E.quiz_points} | Niv. {progression['niveau']}"
        self.nouvelle_question()

    def nouvelle_question(self):
        E.question = random.choice(questions_data) if random.random() < 0.5 else generer_question_math()
        self.lbl_question.text = E.question[0]
        parler(E.question[0], 0.1)

    def verifier(self, rep):
        if rep == E.question[1]:
            E.quiz_points += 1
            progression["quiz_points"] = E.quiz_points
            sauvegarder_progression()
            ajouter_xp(2)
            if E.quiz_points >= 10:
                attribuer_badge("quiz10")
            self.lbl_score.text = f"Score : {E.quiz_points} | Niv. {progression['niveau']}"
            parler("Bonne réponse !")
            message("Bravo !", "Bonne réponse !", auto=1.2)
        else:
            parler("Ce n'est pas ça.")
            message("Oups !", f"La réponse était {E.question[1]}.", auto=1.6)
        self.nouvelle_question()


# ---- ANIMAUX ----
class PageAnimaux(Page):
    def construire(self):
        self.titre("🦁", "JEU DES ANIMAUX", "#222222")
        self.lbl_score = self.ajouter(et("", 18, "#222222", gras=True))
        self.lbl_consigne = self.ajouter(et("", 24, "#222222", gras=True))
        grille = GridLayout(cols=3, size_hint_y=None, height=dp(110), spacing=dp(10))
        self.btns = []
        for _ in range(3):
            b = BoutonEmoji(emoji="", mode="icone", fond="#FFFFFF", bordure="#B8860B")
            grille.add_widget(b)
            self.btns.append(b)
        self.ajouter(grille)
        self.retour_accueil()

    def rafraichir(self):
        self.lbl_score.text = f"Score : {E.points_animaux}"
        self.nouvelle_question()

    def nouvelle_question(self):
        noms = list(animaux_jeu.keys())
        E.animal = random.choice(noms)
        self.lbl_consigne.text = f"Où est le {E.animal} ?"
        parler(f"Où est le {E.animal} ?", 0.1)
        choix = random.sample([n for n in noms if n != E.animal], 2) + [E.animal]
        random.shuffle(choix)
        for b, nom in zip(self.btns, choix):
            b.set_emoji(animaux_jeu[nom])
            b.unbind(on_release=getattr(b, "_cb", None)) if getattr(b, "_cb", None) else None
            b._cb = partial(self._clic, nom)
            b.bind(on_release=b._cb)

    def _clic(self, nom, *a):
        self.verifier(nom)

    def verifier(self, nom):
        if nom == E.animal:
            E.points_animaux += 1
            progression["animaux_points"] = E.points_animaux
            sauvegarder_progression()
            ajouter_xp(2)
            if E.points_animaux >= 10:
                attribuer_badge("animaux10")
            self.lbl_score.text = f"Score : {E.points_animaux}"
            parler("Bravo !")
            message("Super !", "C'est exact !", auto=1.2)
        else:
            parler("Essaie encore.")
            message("Essaie encore !", f"Trouve le {E.animal} !", auto=1.6)
        self.nouvelle_question()


# ---- ANGLAIS ----
class PageAnglais(Page):
    def construire(self):
        self.titre("🇬🇧", "COURS D'ANGLAIS", "#117A65")
        nav = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(54), spacing=dp(8))
        g = Bouton(fond="#117A65", text="‹", size_hint_x=None, width=dp(54), font_size=sp(26))
        g.bind(on_release=lambda *a: self.niveau(-1))
        self.lbl_niveau = Et(text="", font_size=sp(15), bold=True, size_hint_y=1, color=hexc("#222222"))
        d = Bouton(fond="#117A65", text="›", size_hint_x=None, width=dp(54), font_size=sp(26))
        d.bind(on_release=lambda *a: self.niveau(1))
        nav.add_widget(g)
        nav.add_widget(self.lbl_niveau)
        nav.add_widget(d)
        self.ajouter(nav)
        self.action("Vidéo", "#FF5722", self.video)
        self.emoji = self.ajouter(image_emoji("👋", 72))
        self.lbl_mot = self.ajouter(et("", 26, "#16A085", gras=True))
        self.action("Voir la traduction", "#1ABC9C", self.reveler)
        self.lbl_trad = self.ajouter(et("", 22, "#222222", italique=True))
        self.action("Mot suivant  ›", "#2E4053", self.suivant)
        self.retour_accueil()

    def rafraichir(self):
        niveau = NIVEAUX_EN[E.niv_en]
        self.lbl_niveau.text = niveau
        item = english_curriculum[niveau]["mots"][E.mot_en]
        self.emoji.img.source = os.path.join(RACINE, emoji_fichier(item["emoji"]))
        self.lbl_mot.text = item["en"]
        self.lbl_trad.text = ""

    def reveler(self):
        item = english_curriculum[NIVEAUX_EN[E.niv_en]]["mots"][E.mot_en]
        self.lbl_trad.text = f"= {item['fr']}"
        parler(f"{item['en']}... signifie... {item['fr']}")

    def suivant(self):
        E.mot_en = (E.mot_en + 1) % len(english_curriculum[NIVEAUX_EN[E.niv_en]]["mots"])
        self.rafraichir()

    def niveau(self, sens):
        E.mot_en = 0
        E.niv_en = (E.niv_en + sens) % len(NIVEAUX_EN)
        self.rafraichir()

    def video(self):
        ouvrir_lien(english_curriculum[NIVEAUX_EN[E.niv_en]]["video_link"])


# ---- FRANÇAIS ----
class PageFrancais(Page):
    def construire(self):
        self.titre("🇫🇷", "ESPACE FRANÇAIS", "#7D3C98")
        nav = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(54), spacing=dp(8))
        g = Bouton(fond="#7D3C98", text="‹", size_hint_x=None, width=dp(54), font_size=sp(26))
        g.bind(on_release=lambda *a: self.niveau(-1))
        self.lbl_niveau = Et(text="", font_size=sp(15), bold=True, size_hint_y=1, color=hexc("#5B2C6F"))
        d = Bouton(fond="#7D3C98", text="›", size_hint_x=None, width=dp(54), font_size=sp(26))
        d.bind(on_release=lambda *a: self.niveau(1))
        nav.add_widget(g)
        nav.add_widget(self.lbl_niveau)
        nav.add_widget(d)
        self.ajouter(nav)
        self.emoji = self.ajouter(image_emoji("🔤", 56))
        self.lbl_titre = self.ajouter(et("", 18, "#884EA0", gras=True))
        fiche = Carte()
        self.lbl_regle = et("", 16, "#222222", align="left")
        self.lbl_exemple = et("", 16, "#1B7F2A", italique=True, align="left")
        fiche.add_widget(self.lbl_regle)
        fiche.add_widget(self.lbl_exemple)
        self.ajouter(fiche)
        self.action("Écouter", "#AF7AC5", self.ecouter)
        self.action("Leçon suivante  ›", "#34495E", self.suivante)
        self.ajouter(et("Conjugaison Dynamique", 19, "#27AE60", gras=True))
        self.entree = self.ajouter(champ(text="manger", font_size=sp(20)))
        self.temps = self.ajouter(Choix(list(dict_temps.keys()), "Présent"))
        self.action("Conjuguer !", "#2ECC71", self.conjuguer)
        self.resultat = Carte(fond="#FFFFFF", bordure="#999999")
        self.lbl_res = et("Les verbes apparaîtront ici...", 17, "#222222", gras=True, align="left")
        self.resultat.add_widget(self.lbl_res)
        self.ajouter(self.resultat)
        self.retour_accueil()

    def _lecon(self):
        return francais_curriculum[NIVEAUX_FR[E.niv_fr]]["leçons"][E.lecon_fr]

    def rafraichir(self):
        self.lbl_niveau.text = NIVEAUX_FR[E.niv_fr]
        lecon = self._lecon()
        self.emoji.img.source = os.path.join(RACINE, emoji_fichier(lecon["emoji"]))
        self.lbl_titre.text = lecon["titre"]
        self.lbl_regle.text = lecon["regle"]
        self.lbl_exemple.text = lecon["exemple"]

    def ecouter(self):
        lecon = self._lecon()
        parler(f"Partie Grammaire. {lecon['titre']}. Règle : {lecon['regle']} {lecon['exemple']}")

    def suivante(self):
        E.lecon_fr = (E.lecon_fr + 1) % len(francais_curriculum[NIVEAUX_FR[E.niv_fr]]["leçons"])
        self.rafraichir()

    def niveau(self, sens):
        E.lecon_fr = 0
        E.niv_fr = (E.niv_fr + sens) % len(NIVEAUX_FR)
        self.rafraichir()

    def conjuguer(self):
        verbe = self.entree.text.strip().lower()
        temps = self.temps.valeur
        if not verbe:
            message("Attention", "Entre un verbe.", auto=1.5)
            return
        try:
            mode, temps_tech = dict_temps[temps]
            data = conjugateur.conjugate(verbe)
            formes = data["moods"][mode][temps_tech]
            self.lbl_res.text = f"--- {verbe.upper()} ({temps}) ---\n\n" + "\n".join(f"• {f}" for f in formes)
            parler(f"Conjugaison du verbe {verbe} au {temps}")
        except Exception:
            message("Erreur", f"Verbe '{verbe}' invalide.", auto=1.6)


# ---- CONTES ----
class PageContes(Page):
    def construire(self):
        self.titre("✨", "CONTES AFRICAINS", "#A04000")
        self.lbl_titre = self.ajouter(et("", 20, "#BA4A00", gras=True))
        carte = Carte()
        self.lbl_texte = et("", 17, "#222222")
        carte.add_widget(self.lbl_texte)
        self.ajouter(carte)
        self.action("Vidéo", "#FF5722", self.video)
        self.action("Histoire suivante", "#E67E22", self.suivant)
        self.retour_accueil()

    def rafraichir(self):
        self.lbl_titre.text = contes_data[E.conte]["titre"]
        self.lbl_texte.text = contes_data[E.conte]["histoire"]
        if E.conte not in progression["contes_lus"]:
            progression["contes_lus"].append(E.conte)
            sauvegarder_progression()
        if len(progression["contes_lus"]) >= len(contes_data):
            attribuer_badge("conteur")

    def suivant(self):
        E.conte = (E.conte + 1) % len(contes_data)
        self.rafraichir()
        self.sv.scroll_y = 1

    def video(self):
        ouvrir_lien(contes_data[E.conte]["video_link"])


# ---- GÉOGRAPHIE ----
class PageGeographie(Page):
    def construire(self):
        self.titre("🌍", "GÉOGRAPHIE AFRIQUE", "#2980B9", 20)
        self.ajouter(et("54 pays disponibles", 13, "#888888", italique=True))
        self.choix = self.ajouter(Choix(sorted(afrique_geographie.keys()), "Guinée",
                                        on_choix=lambda v: self.rafraichir()))
        self.action("Écouter", "#2ECC71", self.ecouter)
        fiche = Carte(bordure="#2980B9")
        self.drapeau = image_emoji("🌍", 64)
        self.lbl_nom = et("", 22, "#2980B9", gras=True)
        fiche.add_widget(self.drapeau)
        fiche.add_widget(self.lbl_nom)
        self.lignes = {}
        for cle, emoji in [("capitale", "🏢"), ("situation", "🌍"), ("superficie", "📐"),
                           ("population", "👥"), ("regions", "🗺️"), ("langues", "🗣️")]:
            ligne = ligne_icone(emoji, "", 16)
            self.lignes[cle] = ligne
            fiche.add_widget(ligne)
        self.ajouter(fiche)
        self.retour_accueil()

    def rafraichir(self):
        pays = self.choix.valeur
        if pays not in afrique_geographie:
            return
        i = afrique_geographie[pays]
        self.drapeau.img.source = os.path.join(RACINE, emoji_fichier(i["emoji"]))
        self.lbl_nom.text = pays
        self.lignes["capitale"].lab.text = f"Capitale : {i['capitale']}"
        self.lignes["situation"].lab.text = f"Région : {i['situation']}"
        self.lignes["superficie"].lab.text = f"Superficie : {i['superficie']}"
        self.lignes["population"].lab.text = f"Population : {i['population']}"
        self.lignes["regions"].lab.text = f"Divisions : {i['regions']}"
        self.lignes["langues"].lab.text = f"Langues : {i['langues']}"
        if pays not in progression["pays_vus"]:
            progression["pays_vus"].append(pays)
            sauvegarder_progression()
            ajouter_xp(1)
        if len(progression["pays_vus"]) >= 54:
            attribuer_badge("explo")

    def ecouter(self):
        pays = self.choix.valeur
        if pays in afrique_geographie:
            i = afrique_geographie[pays]
            parler(f"Le {pays}. Capitale : {i['capitale']}. Région : {i['situation']}.")


# ---- COULEURS & FORMES ----
class PageCouleurs(Page):
    def construire(self):
        self.titre("🎨", "COULEURS & FORMES", "#C2185B")
        self.lbl_nom = self.ajouter(et("", 30, "#222222", gras=True))
        self.pastille = self.ajouter(Pastille())
        self.action("Couleur suivante  ›", "#E91E63", self.couleur_suivante)
        self.forme_img = self.ajouter(image_emoji("⭕", 88))
        self.lbl_forme = self.ajouter(et("", 24, "#222222", gras=True))
        self.action("Forme suivante  ›", "#9C27B0", self.forme_suivante)
        self.retour_accueil()

    def rafraichir(self):
        nom = COULEURS[E.couleur]
        self.lbl_nom.text = nom
        self.pastille.mettre(couleurs_data[nom])
        forme = FORMES[E.forme]
        self.forme_img.img.source = os.path.join(RACINE, emoji_fichier(formes_data[forme]))
        self.lbl_forme.text = forme
        parler(f"{nom}. {forme}", 0.1)

    def couleur_suivante(self):
        E.couleur = (E.couleur + 1) % len(COULEURS)
        self.rafraichir()

    def forme_suivante(self):
        E.forme = (E.forme + 1) % len(FORMES)
        self.rafraichir()


# ---- JOURS & MOIS ----
class PageCalendrier(Page):
    def construire(self):
        self.titre("📅", "JOURS & MOIS", "#00695C")
        self.ajouter(et("Jour :", 16, "#222222", italique=True))
        self.lbl_jour = self.ajouter(et("", 40, "#00897B", gras=True))
        self.action("Jour suivant  ›", "#009688", self.jour_suivant)
        self.ajouter(et("Mois :", 16, "#222222", italique=True))
        self.lbl_mois = self.ajouter(et("", 40, "#00695C", gras=True))
        self.action("Mois suivant  ›", "#00695C", self.mois_suivant)
        self.retour_accueil()

    def rafraichir(self):
        self.lbl_jour.text = jours_semaine[E.jour]
        self.lbl_mois.text = mois_annee[E.mois]
        parler(f"{jours_semaine[E.jour]}. {mois_annee[E.mois]}", 0.1)

    def jour_suivant(self):
        E.jour = (E.jour + 1) % 7
        self.rafraichir()

    def mois_suivant(self):
        E.mois = (E.mois + 1) % 12
        self.rafraichir()


# ---- SCIENCES ----
class PageSciences(Page):
    def construire(self):
        self.titre("🧪", "LE CORPS HUMAIN", "#E65100")
        self.emoji = self.ajouter(image_emoji("👤", 120))
        self.lbl_nom = self.ajouter(et("", 32, "#BF360C", gras=True))
        self.action("Partie suivante  ›", "#FF9800", self.suivant)
        self.retour_accueil()

    def rafraichir(self):
        partie = CORPS[E.corps]
        self.emoji.img.source = os.path.join(RACINE, emoji_fichier(corps_humain[partie]))
        self.lbl_nom.text = partie
        parler(f"Le {partie.lower()}", 0.1)

    def suivant(self):
        E.corps = (E.corps + 1) % len(CORPS)
        self.rafraichir()


# ---- MÉMOIRE ----
class PageMemory(Page):
    def construire(self):
        self.titre("🧠", "JEU DE MÉMOIRE", "#4E342E")
        self.lbl_statut = self.ajouter(et("Touche deux cartes identiques !", 16, "#6D4C41", gras=True))
        grille = GridLayout(cols=4, size_hint_y=None, height=dp(4 * 76 + 3 * 8), spacing=dp(8))
        self.cartes = []
        for i in range(16):
            b = BoutonEmoji(emoji="", mode="icone", fond="#34495E", text="?", font_size=sp(28))
            b.bind(on_release=partial(self._clic, i))
            grille.add_widget(b)
            self.cartes.append(b)
        self.ajouter(grille)
        self.action("Nouvelle partie", "#795548", self.nouvelle_partie)
        self.retour_accueil()

    def _clic(self, i, *a):
        self.clic(i)

    def _cacher_carte(self, b):
        b.fond = hexc("#34495E")
        b._c.rgba = b.fond
        b.text = "?"
        b.set_emoji("")

    def _montrer_carte(self, b, emoji):
        b.fond = hexc("#FFFFFF")
        b._c.rgba = b.fond
        b.text = ""
        b.set_emoji(emoji)

    def rafraichir(self):
        self.nouvelle_partie()

    def nouvelle_partie(self):
        E.mem_bloque = False
        E.mem_vues = []
        E.mem_trouvees = []
        emojis = list(animaux_jeu.values())[:8]
        E.mem_cartes = emojis * 2
        random.shuffle(E.mem_cartes)
        for b in self.cartes:
            self._cacher_carte(b)
        self.lbl_statut.text = "Touche deux cartes identiques !"

    def clic(self, idx):
        if E.mem_bloque or idx in E.mem_vues or idx in E.mem_trouvees:
            return
        self._montrer_carte(self.cartes[idx], E.mem_cartes[idx])
        E.mem_vues.append(idx)
        if len(E.mem_vues) == 2:
            i, j = E.mem_vues
            if E.mem_cartes[i] == E.mem_cartes[j]:
                E.mem_trouvees.extend([i, j])
                E.mem_vues = []
                self.lbl_statut.text = f"Paires : {len(E.mem_trouvees) // 2}/8"
                parler("Bien joué !")
                if len(E.mem_trouvees) == 16:
                    self.lbl_statut.text = "GAGNÉ !"
                    progression["memory_best"] += 1
                    sauvegarder_progression()
                    ajouter_xp(10)
                    attribuer_badge("memory10")
                    message("Bravo !", "Toutes les paires trouvées !", auto=2)
            else:
                E.mem_bloque = True
                Clock.schedule_once(self.cacher_cartes, 0.8)

    def cacher_cartes(self, *a):
        for idx in E.mem_vues:
            self._cacher_carte(self.cartes[idx])
        E.mem_vues = []
        E.mem_bloque = False


# ---- TABLES DE MULTIPLICATION ----
class PageTables(Page):
    def construire(self):
        self.titre("✖️", "TABLES DE MULTIPLICATION", "#6A1B9A", 20)
        nav = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(54), spacing=dp(8))
        g = Bouton(fond="#6A1B9A", text="‹", size_hint_x=None, width=dp(54), font_size=sp(26))
        g.bind(on_release=lambda *a: self.changer("-"))
        self.lbl_table = Et(text="", font_size=sp(20), bold=True, size_hint_y=1, color=hexc("#222222"))
        d = Bouton(fond="#6A1B9A", text="›", size_hint_x=None, width=dp(54), font_size=sp(26))
        d.bind(on_release=lambda *a: self.changer("+"))
        nav.add_widget(g)
        nav.add_widget(self.lbl_table)
        nav.add_widget(d)
        self.ajouter(nav)
        self.lbl_score = self.ajouter(et("", 18, "#222222", gras=True))
        self.lbl_q = self.ajouter(et("", 40, "#6A1B9A", gras=True))
        self.entree = self.ajouter(champ(input_filter="int"))
        self.entree.bind(on_text_validate=lambda *a: self.verifier())
        self.action("Valider", "#9C27B0", self.verifier)
        self.retour_accueil()

    def rafraichir(self):
        self.lbl_table.text = f"Table du {E.table}"
        self.lbl_score.text = f"Score : {E.tables_points}"
        self.nouvelle_question()

    def nouvelle_question(self):
        a = E.table if E.table else random.randint(2, 10)
        b = random.randint(1, 10)
        E.table_q = (f"{a} × {b} = ?", str(a * b))
        self.lbl_q.text = E.table_q[0]
        parler(f"Combien font {a} fois {b} ?", 0.1)

    def verifier(self):
        rep = self.entree.text.strip()
        if rep == E.table_q[1]:
            E.tables_points += 1
            progression["tables_points"] = E.tables_points
            sauvegarder_progression()
            ajouter_xp(3)
            if E.tables_points >= 50:
                attribuer_badge("tables50")
            self.lbl_score.text = f"Score : {E.tables_points}"
            parler("Bonne réponse !")
            message("Bravo", "Exact !", auto=1.2)
        else:
            parler("Non.")
            message("Faux", f"La réponse était {E.table_q[1]}", auto=1.6)
        self.entree.text = ""
        self.nouvelle_question()

    def changer(self, sens):
        if sens == "+":
            E.table = min(10, E.table + 1) if E.table < 10 else 2
        else:
            E.table = max(2, E.table - 1) if E.table > 2 else 10
        self.lbl_table.text = f"Table du {E.table}"
        self.nouvelle_question()


# ---- LIRE L'HEURE ----
class PageHeure(Page):
    def construire(self):
        self.titre("⏰", "LIRE L'HEURE", "#283593")
        self.lbl_score = self.ajouter(et("", 18, "#222222", gras=True))
        self.ajouter(image_emoji("🕐", 72))
        self.lbl_visuel = self.ajouter(et("", 56, "#3949AB", gras=True))
        self.ajouter(et("Quelle heure est-il ?", 20, "#222222", gras=True))
        self.ajouter(et("Entre l'heure (0-23) :", 15, "#222222", italique=True))
        self.entree = self.ajouter(champ(input_filter="int"))
        self.entree.bind(on_text_validate=lambda *a: self.verifier())
        self.action("Valider", "#3F51B5", self.verifier)
        self.retour_accueil()

    def rafraichir(self):
        self.lbl_score.text = f"Score : {E.heures_points}"
        self.nouvelle_question()

    def nouvelle_question(self):
        E.heure = {"h": random.randint(0, 23), "m": random.choice([0, 15, 30, 45])}
        self.lbl_visuel.text = f"{E.heure['h']:02d}:{E.heure['m']:02d}"
        self.entree.text = ""
        parler("Quelle heure est-il ?", 0.1)

    def verifier(self):
        try:
            rep = int(self.entree.text.strip())
        except ValueError:
            message("Attention", "Entre un nombre (heures).", auto=1.5)
            return
        h, m = E.heure["h"], E.heure["m"]
        if rep == h:
            E.heures_points += 1
            progression["heures_points"] = E.heures_points
            sauvegarder_progression()
            ajouter_xp(2)
            if E.heures_points >= 20:
                attribuer_badge("horloge")
            self.lbl_score.text = f"Score : {E.heures_points}"
            message("Bravo", f"Oui ! {h:02d}:{m:02d}", auto=1.2)
        else:
            message("Faux", f"C'était {h} heures.", auto=1.6)
        self.nouvelle_question()


# ---- QUIZ GÉOGRAPHIE ----
class PageGeoQuiz(Page):
    def construire(self):
        self.titre("🗺️", "QUIZ GÉOGRAPHIE", "#37474F")
        self.lbl_score = self.ajouter(et("", 18, "#222222", gras=True))
        self.lbl_q = self.ajouter(et("", 22, "#222222", gras=True))
        self.btns = []
        for _ in range(3):
            b = Bouton(fond="#37474F", height=dp(60), font_size=sp(19))
            self.ajouter(b)
            self.btns.append(b)
        self.retour_accueil()

    def rafraichir(self):
        self.lbl_score.text = f"Score : {E.geo_points}"
        self.nouvelle_question()

    def nouvelle_question(self):
        pays = random.choice(list(afrique_geographie.keys()))
        bonne = afrique_geographie[pays]["capitale"]
        autres = [afrique_geographie[p]["capitale"] for p in afrique_geographie
                  if afrique_geographie[p]["capitale"] != bonne]
        choix = random.sample(autres, 2) + [bonne]
        random.shuffle(choix)
        E.geo_q = (pays, bonne, choix)
        self.lbl_q.text = f"Capitale du {pays} ?"
        for b, c in zip(self.btns, choix):
            b.text = c
            if getattr(b, "_cb", None):
                b.unbind(on_release=b._cb)
            b._cb = partial(self._clic, c)
            b.bind(on_release=b._cb)
        parler(f"Quelle est la capitale du {pays} ?", 0.1)

    def _clic(self, c, *a):
        self.verifier(c)

    def verifier(self, reponse):
        if reponse == E.geo_q[1]:
            E.geo_points += 1
            progression["geo_quiz_points"] = E.geo_points
            sauvegarder_progression()
            ajouter_xp(2)
            if E.geo_points >= 20:
                attribuer_badge("geo20")
            self.lbl_score.text = f"Score : {E.geo_points}"
            parler("Bonne réponse !")
            message("Bravo", "Exact !", auto=1.2)
        else:
            message("Faux", f"C'était {E.geo_q[1]}", auto=1.6)
        self.nouvelle_question()


# ---- MINI-DICTÉE ----
class PageDictee(Page):
    def construire(self):
        self.titre("📝", "MINI-DICTÉE", "#33691E")
        self.lbl_consigne = self.ajouter(et("", 17, "#222222", italique=True))
        self.action("Écouter le mot", "#8BC34A", self.ecouter)
        self.entree = self.ajouter(champ(font_size=sp(24)))
        self.entree.bind(on_text_validate=lambda *a: self.verifier())
        self.action("Valider", "#558B2F", self.verifier)
        self.lbl_res = self.ajouter(et("", 19, "#222222", gras=True))
        self.retour_accueil()

    def rafraichir(self):
        self.nouvelle_question()

    def nouvelle_question(self, *a):
        mot = random.choice(dictee_mots)
        E.dictee_q = (mot, mot)
        self.lbl_consigne.text = "Touche « Écouter le mot » puis écris le mot"
        self.entree.text = ""
        self.lbl_res.text = ""

    def ecouter(self):
        parler(E.dictee_q[0])

    def verifier(self):
        rep = self.entree.text.strip().lower()
        if rep == E.dictee_q[1].lower():
            E.dictee_points += 1
            progression["dictee_points"] = E.dictee_points
            sauvegarder_progression()
            ajouter_xp(2)
            if E.dictee_points >= 10:
                attribuer_badge("dictee10")
            self.lbl_res.text = f"Correct ! Score : {E.dictee_points}"
            self.lbl_res.color = hexc("#2E7D32")
        else:
            self.lbl_res.text = f"C'était : {E.dictee_q[1]}"
            self.lbl_res.color = hexc("#C62828")
        Clock.schedule_once(self.nouvelle_question, 1.2)


# ---- MON PROGRÈS ----
class PageProgres(Page):
    def construire(self):
        self.titre("🏆", "MON PROGRÈS", "#F57F17")
        self.carte = Carte(bordure="#F9A825", spacing=dp(2))
        self.ajouter(self.carte)
        self.action("Réinitialiser", "#E74C3C", self.reinitialiser)
        self.retour_accueil()

    def rafraichir(self):
        p = progression
        self.carte.clear_widgets()
        lignes = [
            ("🏅", f"Niveau : {p.get('niveau', 1)}   ({p.get('xp', 0)} XP)"),
            ("🎮", f"Quiz Math : {p.get('quiz_points', 0)}"),
            ("🦁", f"Animaux : {p.get('animaux_points', 0)}"),
            ("🧠", f"Memory : {p.get('memory_best', 0)} victoires"),
            ("✖️", f"Tables : {p.get('tables_points', 0)}"),
            ("⏰", f"Heures : {p.get('heures_points', 0)}"),
            ("🗺️", f"Quiz Géo : {p.get('geo_quiz_points', 0)}"),
            ("📝", f"Dictée : {p.get('dictee_points', 0)}"),
            ("📚", f"Lettres vues : {len(p.get('lettres_vues', []))}/26"),
            ("🌍", f"Pays visités : {len(p.get('pays_vus', []))}/{len(afrique_geographie)}"),
            ("📖", f"Contes lus : {len(p.get('contes_lus', []))}/{len(contes_data)}"),
        ]
        for emoji, texte in lignes:
            self.carte.add_widget(ligne_icone(emoji, texte, 16))
        self.carte.add_widget(et("BADGES :", 18, "#F57F17", gras=True, align="left"))
        if p["badges"]:
            for b in p["badges"]:
                emoji, nom = separer_emoji(BADGES[b]["nom"])
                self.carte.add_widget(ligne_icone(emoji, nom, 16))
        else:
            self.carte.add_widget(et("Aucun encore...", 16, "#555555", italique=True, align="left"))

    def reinitialiser(self):
        def faire():
            progression.clear()
            progression.update(_defauts())
            synchroniser_scores()
            sauvegarder_progression()
            self.rafraichir()
            message("OK", "Progression réinitialisée.", auto=1.5)
        confirmer("Confirmer", "Effacer toute la progression ?", faire)


# ---- PARAMÈTRES ----
class PageParametres(Page):
    def construire(self):
        self.titre("⚙️", "PARAMÈTRES", "#37474F")
        ligne = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56), spacing=dp(10))
        ligne.add_widget(et("Activer le son", 19, "#222222", size_hint_y=1))
        self.interrupteur = Switch(active=True, size_hint_x=None, width=dp(100))
        self.interrupteur.bind(active=self._son)
        ligne.add_widget(self.interrupteur)
        self.ajouter(ligne)
        self.ajouter(et("NEXA KIDS AFRICA v3.0\nÉdition Complète", 15, "#546E7A"))
        self.action("À propos", "#607D8B", App_a_propos)
        self.retour_accueil()
        self.action("Quitter", "#C62828", lambda: App.get_running_app().quitter())

    def rafraichir(self):
        self._maj = True
        self.interrupteur.active = bool(progression.get("sound_on", True))
        self._maj = False

    def _son(self, inst, valeur):
        if getattr(self, "_maj", False):
            return
        progression["sound_on"] = bool(valeur)
        sauvegarder_progression()
        if valeur:
            voix.dire("Son activé")


def App_a_propos():
    message("À propos",
            "NEXA KIDS AFRICA v3.0\n\n"
            "Logiciel éducatif pour les enfants africains\n\n"
            "Modules : Alphabet · Chiffres · Couleurs · Formes · Jours · Mois · "
            "Sciences · Tables · Heures · Animaux · Mémoire · Quiz Math · Quiz Géo · "
            "Français · Anglais · Contes · Dictée · Géographie (54 pays) · Progrès\n\n"
            "La progression est sauvegardée automatiquement sur l'appareil.", grand=True)


def ouvrir_lien(url):
    """Ouvre une vidéo dans le navigateur / YouTube."""
    try:
        if platform == "android":
            from jnius import autoclass
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            PythonActivity.mActivity.startActivity(intent)
        else:
            webbrowser.open(url)
    except Exception as e:
        print(f"Lien impossible : {e}")
        message("Oups", "Impossible d'ouvrir la vidéo (connexion Internet ?).", auto=2)


# ==========================================================================
# APPLICATION
# ==========================================================================
MENU_BG = "#C62828"
MENU_HEADER = "#0D47A1"
MENU_TEXT = "#64B5F6"

MENU_ITEMS = [
    ("🏠", "Accueil", "accueil", MENU_BLUE),
    ("📚", "Apprendre  ›", "cat:Apprendre", MENU_BLUE),
    ("🎮", "Jouer  ›", "cat:Jouer", MENU_BLUE),
    ("🌐", "Langues  ›", "cat:Langues", MENU_BLUE),
    ("🌍", "Découvrir  ›", "cat:Découvrir", MENU_BLUE),
    ("🏆", "Mon Espace  ›", "cat:Mon Espace", MENU_BLUE),
    None,
    ("🏆", "Mon Progrès", "progres", MENU_BLUE),
    ("⚙️", "Paramètres", "parametres", MENU_BLUE),
    ("ℹ️", "À propos", "about", MENU_BLUE),
    ("🚪", "Quitter", "quit", "#C62828"),
]


class NexaApp(App):
    title = "NEXA KIDS AFRICA"

    def build(self):
        CHEMIN_PROGRES[0] = os.path.join(self.user_data_dir, "nexa_kids_progress.json")
        charger_progression()
        synchroniser_scores()
        self.menu_ouvert = False

        self.racine = FloatLayout()
        colonne = BoxLayout(orientation="vertical")
        colonne.add_widget(self._barre())
        self.sm = ScreenManager(transition=NoTransition())
        colonne.add_widget(self.sm)
        self.racine.add_widget(colonne)

        pages = [
            PageAccueil("accueil", "#EEEEEE"), PageSousMenu("sousmenu", "#F0F0F0"),
            PageAlphabet("alphabet", "#FFF9E6"), PageChiffres("chiffres", "#E6F2FF"),
            PageQuiz("quiz", "#E6FFE6"), PageAnimaux("animaux", "#FFEAA7"),
            PageAnglais("anglais", "#E8F8F5"), PageFrancais("francais", "#F5EEF8"),
            PageContes("contes", "#FDF2E9"), PageGeographie("geographie", "#EBF5FB"),
            PageCouleurs("couleurs", "#FCE4EC"), PageCalendrier("calendrier", "#E0F2F1"),
            PageSciences("sciences", "#FFF3E0"), PageMemory("memory", "#EFEBE9"),
            PageTables("tables", "#F3E5F5"), PageHeure("heure", "#E8EAF6"),
            PageGeoQuiz("geo_quiz", "#ECEFF1"), PageDictee("dictee", "#F1F8E9"),
            PageProgres("progres", "#FFF8E1"), PageParametres("parametres", "#ECEFF1"),
        ]
        for p in pages:
            self.sm.add_widget(p)
        self.sousmenu = self.sm.get_screen("sousmenu")

        self._construire_menu()
        Window.bind(on_keyboard=self._touche)
        self.aller("accueil")
        return self.racine

    # ---- barre supérieure ----
    def _barre(self):
        barre = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(58),
                          padding=[dp(6), 0, dp(14), 0])
        with barre.canvas.before:
            Color(*hexc(MENU_BLUE))
            r = Rectangle(pos=barre.pos, size=barre.size)
        barre.bind(pos=lambda w, v: setattr(r, "pos", v), size=lambda w, v: setattr(r, "size", v))
        bouton = Hamburger(size_hint_x=None, width=dp(56))
        bouton.bind(on_release=lambda *a: self.ouvrir_menu())
        barre.add_widget(bouton)
        barre.add_widget(Label(text="NEXA KIDS AFRICA", bold=True, font_size=sp(19),
                               color=(1, 1, 1, 1), halign="right", valign="middle",
                               text_size=(Window.width - dp(90), None)))
        return barre

    # ---- menu latéral ----
    def _construire_menu(self):
        self.menu = FloatLayout()
        fond = Button(background_normal="", background_down="", background_color=(0, 0, 0, 0.55))
        fond.bind(on_release=lambda *a: self.fermer_menu())
        self.menu.add_widget(fond)
        panneau = BoxLayout(orientation="vertical", size_hint=(0.84, 1), pos_hint={"x": 0, "y": 0})
        with panneau.canvas.before:
            Color(*hexc(MENU_BG))
            rp = Rectangle(pos=panneau.pos, size=panneau.size)
        panneau.bind(pos=lambda w, v: setattr(rp, "pos", v), size=lambda w, v: setattr(rp, "size", v))
        entete = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(64), padding=[dp(16), dp(8)])
        with entete.canvas.before:
            Color(*hexc(MENU_HEADER))
            re_ = Rectangle(pos=entete.pos, size=entete.size)
        entete.bind(pos=lambda w, v: setattr(re_, "pos", v), size=lambda w, v: setattr(re_, "size", v))
        entete.add_widget(Label(text="MENU", bold=True, font_size=sp(22), color=hexc(MENU_TEXT),
                                halign="left", valign="middle"))
        x = Bouton(fond="#C62828", text="X", size_hint_x=None, width=dp(52), font_size=sp(20))
        x.bind(on_release=lambda *a: self.fermer_menu())
        entete.add_widget(x)
        panneau.add_widget(entete)
        sv = ScrollView(do_scroll_x=False)
        liste = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(4),
                          padding=[dp(6), dp(8)])
        liste.bind(minimum_height=liste.setter("height"))
        for item in MENU_ITEMS:
            if item is None:
                sep = Widget(size_hint_y=None, height=dp(14))
                liste.add_widget(sep)
                continue
            emoji, texte, action, barre = item
            b = BoutonEmoji(emoji=emoji, text=texte, fond=MENU_BG, couleur_texte=MENU_TEXT,
                            barre=barre, height=dp(58), font_size=sp(17))
            b.bind(on_release=partial(self._action_menu, action))
            liste.add_widget(b)
        sv.add_widget(liste)
        panneau.add_widget(sv)
        self.menu.add_widget(panneau)

    def ouvrir_menu(self):
        if not self.menu_ouvert:
            self.racine.add_widget(self.menu)
            self.menu_ouvert = True

    def fermer_menu(self):
        if self.menu_ouvert:
            self.racine.remove_widget(self.menu)
            self.menu_ouvert = False

    def _action_menu(self, action, *a):
        self.fermer_menu()
        if action == "about":
            App_a_propos()
        elif action == "quit":
            self.quitter()
        elif action.startswith("cat:"):
            self.ouvrir_categorie(action[4:])
        else:
            self.aller(action)

    # ---- navigation ----
    def aller(self, nom):
        self.fermer_menu()
        self.sm.current = nom

    def ouvrir_categorie(self, nom):
        self.fermer_menu()
        self.sousmenu.charger(nom)
        self.sm.current = "sousmenu"

    def quitter(self):
        confirmer("Quitter", "Veux-tu vraiment quitter ?", self.stop)

    def _touche(self, fenetre, touche, *args):
        if touche == 27:                      # bouton « Retour » d'Android / Échap
            if self.menu_ouvert:
                self.fermer_menu()
            elif self.sm.current != "accueil":
                self.aller("accueil")
            else:
                self.quitter()
            return True
        return False

    def on_pause(self):
        sauvegarder_progression()
        return True

    def on_stop(self):
        sauvegarder_progression()


if __name__ == "__main__":
    NexaApp().run()
