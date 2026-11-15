# NEXA KIDS AFRICA – version Kivy (Android)

## Tester sur PC
    pip install kivy plyer pyttsx3
    python main.py

## Fabriquer l'APK (Linux ou WSL2 sous Windows)
    pip install buildozer cython
    buildozer android debug      # 1re fois : 20-40 min, télécharge le SDK/NDK
    # APK : bin/nexakids-3.0-*-debug.apk  -> copier sur le téléphone et installer

Alternative sans installer : Google Colab / GitHub Actions avec buildozer.

## Contenu
- main.py : interface et logique (19 écrans, menu latéral, bouton Retour Android)
- donnees.py : toutes les données (conjugaison, 54 pays, contes, anglais, français…)
- generer_emojis.py : régénère assets/emoji (Kivy n'affiche pas les emojis en texte, ils sont des images)
- Voix : synthèse vocale du téléphone via plyer ; progression sauvegardée dans le dossier privé de l'app.
