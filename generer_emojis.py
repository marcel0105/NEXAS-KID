#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generer_emojis.py - Crée les images PNG des emojis (assets/emoji/*.png).

À lancer UNE FOIS sur un ordinateur (nécessite Pillow compilé avec raqm et la
police NotoColorEmoji.ttf, souvent présente sous Linux :
  /usr/share/fonts/truetype/noto/NotoColorEmoji.ttf).
  python3 generer_emojis.py [chemin/vers/NotoColorEmoji.ttf]
Les PNG générés sont à copier dans l'application (déjà fait dans ce dossier).
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import donnees

POLICE = sys.argv[1] if len(sys.argv) > 1 else "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
SORTIE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "emoji")
os.makedirs(SORTIE, exist_ok=True)
T = 128                                  # taille finale (carrée)
font = ImageFont.truetype(POLICE, 109)   # NotoColorEmoji n'existe qu'en 109 px


def dessin_secours(emoji):
    """Formes que la police emoji ne contient pas (▬ et ⬡)."""
    im = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bleu = (21, 101, 192, 255)
    if emoji.startswith("▬"):
        d.rounded_rectangle((8, 40, T - 8, T - 40), radius=10, fill=bleu)
    elif emoji.startswith("⬡"):
        import math
        pts = [(T / 2 + 54 * math.cos(math.radians(60 * k + 30)),
                T / 2 + 54 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
        d.polygon(pts, fill=(0, 150, 136, 255))
    else:
        return None
    return im


# Séquences que la police rend mal : on dessine un emoji équivalent plus simple
ALIAS = {"👨‍👩‍👧‍👦": "👪"}

n = 0
for e in donnees.tous_les_emojis():
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ALIAS.get(e, e), font=font, embedded_color=True)
    bb = im.getbbox()
    if bb is None:
        out = dessin_secours(e)
        if out is None:
            print("⚠️ pas de glyphe pour", repr(e))
            continue
    else:
        im = im.crop(bb)
        s = max(im.size)
        out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        out.paste(im, ((s - im.width) // 2, (s - im.height) // 2))
        out = out.resize((T, T), Image.LANCZOS)
    out.save(os.path.join(SORTIE, donnees.emoji_fichier(e).split("/")[-1]))
    n += 1
print(f"{n} images créées dans {SORTIE}")
