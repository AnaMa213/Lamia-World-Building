#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyse_style.py — indicateurs quantitatifs de style sur un texte français.

Ce script ne juge pas. Il produit des mesures qui empêchent de décrire un
style « aux phrases courtes et nerveuses » quand la médiane est à 24 mots.
L'interprétation reste le travail de l'agent et de l'auteur.

Usage
-----
    python3 analyse_style.py texte.md
    python3 analyse_style.py variante.md --compare reference.md
    python3 analyse_style.py texte.md --json

Aucune dépendance : stdlib seulement (Python 3.8+).

Limites assumées
----------------
- Les temps verbaux sont détectés par terminaisons : c'est une heuristique,
  pas une analyse morphologique. Les chiffres indiquent une dominante, ils ne
  comptent pas des verbes.
- La segmentation en phrases se trompe sur les abréviations rares et sur les
  points de suspension en milieu de réplique.
- Le ratio de dialogue repose sur la typographie (tiret cadratin, guillemets
  français, guillemets droits). Un dialogue non marqué ne sera pas vu.
"""

import argparse
import json
import re
import statistics
import sys
import unicodedata
from collections import Counter
from pathlib import Path

# --------------------------------------------------------------------------
# Nettoyage
# --------------------------------------------------------------------------

RE_FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.DOTALL)
RE_CODEBLOCK = re.compile(r"```.*?```", re.DOTALL)
RE_HEADING = re.compile(r"^#{1,6}\s.*$", re.MULTILINE)
RE_CALLOUT = re.compile(r"^>\s.*$", re.MULTILINE)
RE_WIKILINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
RE_MDLINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
RE_EMPHASIS = re.compile(r"[*_`]{1,3}")
RE_HRULE = re.compile(r"^\s*(?:---|\*\*\*|___)\s*$", re.MULTILINE)


def nettoyer(texte: str) -> str:
    """Retire l'appareil Markdown pour ne garder que la prose."""
    texte = RE_FRONTMATTER.sub("", texte)
    texte = RE_CODEBLOCK.sub(" ", texte)
    texte = RE_HEADING.sub("", texte)
    texte = RE_CALLOUT.sub("", texte)
    texte = RE_HRULE.sub("", texte)
    texte = RE_WIKILINK.sub(lambda m: m.group(2) or m.group(1), texte)
    texte = RE_MDLINK.sub(r"\1", texte)
    texte = RE_EMPHASIS.sub("", texte)
    # normalise les apostrophes et les tirets pour la suite
    texte = texte.replace("’", "'").replace("‘", "'")
    return texte


# --------------------------------------------------------------------------
# Segmentation
# --------------------------------------------------------------------------

ABREVIATIONS = {
    "m", "mm", "mme", "mlle", "mgr", "dr", "pr", "st", "ste", "av", "apr",
    "cf", "etc", "ex", "n", "p", "vol", "chap", "fig", "art", "env", "j",
}

RE_PARA = re.compile(r"\n\s*\n")
RE_MOT = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿŒœÆæ]+(?:'[A-Za-zÀ-ÖØ-öø-ÿŒœÆæ]+)*")
RE_FIN_PHRASE = re.compile(r"([.!?…]+)")


def decouper_paragraphes(texte: str):
    return [p.strip() for p in RE_PARA.split(texte) if p.strip()]


def decouper_phrases(texte: str):
    """Segmentation simple, avec garde sur les abréviations courantes."""
    morceaux = RE_FIN_PHRASE.split(texte)
    phrases, courant = [], ""
    for i in range(0, len(morceaux), 2):
        segment = morceaux[i]
        ponct = morceaux[i + 1] if i + 1 < len(morceaux) else ""
        courant += segment + ponct
        dernier_mot = RE_MOT.findall(segment)
        garde = (
            ponct == "."
            and dernier_mot
            and strip_accents(dernier_mot[-1]).lower() in ABREVIATIONS
        )
        if ponct and not garde:
            nettoye = courant.strip()
            if RE_MOT.search(nettoye):
                phrases.append(nettoye)
            courant = ""
    reste = courant.strip()
    if RE_MOT.search(reste):
        phrases.append(reste)
    return phrases


def strip_accents(mot: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", mot)
        if unicodedata.category(c) != "Mn"
    )


def mots(texte: str):
    return RE_MOT.findall(texte)


# --------------------------------------------------------------------------
# Indicateurs
# --------------------------------------------------------------------------

PONCTUATION = {
    "virgule": ",",
    "point_virgule": ";",
    "deux_points": ":",
    "tiret_cadratin": "—",
    "tiret_demi": "–",
    "parenthese": "(",
    "exclamation": "!",
    "interrogation": "?",
    "suspension": "…",
    "guillemet_fr": "«",
}

RE_DIALOGUE_DEBUT = re.compile(r'^\s*(?:[—–-]\s|«|")')
RE_ADV_MENT = re.compile(r"\b\w+ment\b", re.IGNORECASE)

# incises : « dit-il », « répondit-elle », « murmura-t-elle »…
RE_INCISE = re.compile(
    r"\b[A-Za-zÀ-ÖØ-öø-ÿ]+-(?:t-)?(?:il|elle|ils|elles|je|on|nous|vous)\b"
)
RE_INCISE_NEUTRE = re.compile(
    r"\b(?:dit|dis|dirent)-(?:t-)?(?:il|elle|ils|elles|je)\b", re.IGNORECASE
)

# heuristiques de temps (3e personne surtout)
RE_IMPARFAIT = re.compile(r"\b\w{2,}(?:ait|aient|ais)\b", re.IGNORECASE)
RE_PASSE_SIMPLE = re.compile(
    r"\b(?:\w{2,}(?:èrent|irent|urent|inrent)|fut|furent|eut|eurent|"
    r"vint|vinrent|prit|prirent|fit|firent|dit|dirent|vit|virent|"
    r"put|purent|sut|surent|alla|allèrent)\b",
    re.IGNORECASE,
)
RE_PRESENT_MARQUEUR = re.compile(
    r"\b(?:est|sont|a|ont|fait|font|dit|disent|va|vont|peut|peuvent|"
    r"voit|voient|prend|prennent)\b",
    re.IGNORECASE,
)

# verbes-filtres : interposent une conscience entre le lecteur et la sensation
RE_FILTRE = re.compile(
    r"\b(?:vit|voyait|sentit|sentait|remarqua|remarquait|entendit|entendait|"
    r"comprit|comprenait|songea|songeait|pensa|pensait|s'aperçut|"
    r"réalisa|réalisait|observa|observait)\b",
    re.IGNORECASE,
)

STOPWORDS = set("""
a à ai aie aient ais ait alors après as au aucun aucune aussi autant autre
autres aux avaient avais avait avant avec avez aviez avions avons ayant beaucoup
bien c ça car ce ceci cela celle celles celui cent cependant certain certaine
ces cet cette ceux chaque chez ci comme commentd dans de dedans dehors déjà
depuis des dès deux devant devait doit donc dont du elle elles en encore entre
er es est et étaient étais était étant été êtes être eu eux fait faire fais
fait faites fut furent hors ici il ils j jamais je jusque l la là le lequel les
leur leurs lui m ma mais malgré me même mes mien moi moins mon n ne ni non nos
notre nous nul on ont ou où par parce pas peu peut plus plutôt pour pourquoi
puis qu quand que quel quelle quelles quels qui quoi s sa sans se sera serait
ses si sien soit son sont sous soyez sur t ta te tel telle tes toi ton tous
tout toute toutes très tu un une va vais vers veut vos votre vous y était
étaient d'un d'une l'un l'une qu'il qu'elle c'est j'ai n'est d'être
""".split())


def indicateurs(texte_brut: str, nom: str) -> dict:
    texte = nettoyer(texte_brut)
    paragraphes = decouper_paragraphes(texte)
    phrases = decouper_phrases(texte)
    tous_mots = mots(texte)
    n_mots = len(tous_mots)

    if n_mots == 0:
        raise SystemExit(f"[{nom}] Aucun mot exploitable après nettoyage.")

    longueurs_phr = [len(mots(p)) for p in phrases]
    longueurs_phr = [n for n in longueurs_phr if n > 0]
    longueurs_par = [len(mots(p)) for p in paragraphes]
    longueurs_par = [n for n in longueurs_par if n > 0]

    def pour_mille(n):
        return round(n * 1000 / n_mots, 1)

    para_dialogue = [p for p in paragraphes if RE_DIALOGUE_DEBUT.match(p)]
    mots_dialogue = sum(len(mots(p)) for p in para_dialogue)

    bas = [strip_accents(m).lower() for m in tous_mots]
    freq = Counter(bas)
    # pour la fréquence lexicale, on retient le segment après l'élision
    # (« l'ombre » → « ombre », « n'avait » → « avait ») avant d'écarter
    # les mots-outils : sinon les formes élidées polluent le classement.
    stop = {strip_accents(s) for s in STOPWORDS}
    noyaux = Counter()
    formes = {}  # clé sans accent -> forme accentuée la plus courante
    for brut in tous_mots:
        m = strip_accents(brut).lower()
        noyau = m.split("'")[-1]
        if len(noyau) > 2 and noyau not in stop and m not in stop:
            noyaux[noyau] += 1
            formes.setdefault(noyau, brut.lower().split("'")[-1])
    pleins = Counter({formes.get(k, k): v for k, v in noyaux.items()})

    imparfait = len(RE_IMPARFAIT.findall(texte))
    passe_simple = len(RE_PASSE_SIMPLE.findall(texte))
    present = len(RE_PRESENT_MARQUEUR.findall(texte))
    total_temps = imparfait + passe_simple + present
    if total_temps == 0:
        dominante = "indéterminé"
    else:
        dominante = max(
            (("imparfait", imparfait), ("passé simple", passe_simple),
             ("présent", present)),
            key=lambda t: t[1],
        )[0]

    res = {
        "nom": nom,
        "volume": {
            "mots": n_mots,
            "phrases": len(longueurs_phr),
            "paragraphes": len(longueurs_par),
        },
        "phrase": {
            "moyenne": round(statistics.mean(longueurs_phr), 1),
            "mediane": round(statistics.median(longueurs_phr), 1),
            "ecart_type": round(statistics.pstdev(longueurs_phr), 1),
            "min": min(longueurs_phr),
            "max": max(longueurs_phr),
            "pct_courtes_moins_8": round(
                100 * sum(1 for n in longueurs_phr if n < 8) / len(longueurs_phr), 1),
            "pct_longues_plus_30": round(
                100 * sum(1 for n in longueurs_phr if n > 30) / len(longueurs_phr), 1),
        },
        "paragraphe": {
            "moyenne": round(statistics.mean(longueurs_par), 1),
            "mediane": round(statistics.median(longueurs_par), 1),
            "max": max(longueurs_par),
            "pct_une_phrase": round(
                100 * sum(1 for p in paragraphes
                          if len(decouper_phrases(p)) == 1) / len(paragraphes), 1),
        },
        "dialogue": {
            "pct_paragraphes": round(100 * len(para_dialogue) / len(paragraphes), 1),
            "pct_mots": round(100 * mots_dialogue / n_mots, 1),
            "incises_p1000": pour_mille(len(RE_INCISE.findall(texte))),
            "incises_neutres_p1000": pour_mille(len(RE_INCISE_NEUTRE.findall(texte))),
        },
        "ponctuation_p1000": {
            nom_p: pour_mille(texte.count(signe))
            for nom_p, signe in PONCTUATION.items()
        },
        "lexique": {
            "adverbes_ment_p1000": pour_mille(len(RE_ADV_MENT.findall(texte))),
            "verbes_filtres_p1000": pour_mille(len(RE_FILTRE.findall(texte))),
            "ttr": round(len(freq) / n_mots, 3),
            "pct_hapax": round(
                100 * sum(1 for c in freq.values() if c == 1) / len(freq), 1),
            "mot_moyen_lettres": round(
                sum(len(m) for m in tous_mots) / n_mots, 2),
            "top_mots_pleins": pleins.most_common(15),
        },
        "temps_heuristique": {
            "imparfait": imparfait,
            "passe_simple": passe_simple,
            "present_marqueurs": present,
            "dominante": dominante,
        },
    }
    return res


# --------------------------------------------------------------------------
# Affichage
# --------------------------------------------------------------------------

def afficher(r: dict):
    v, ph, pa, di, po, lx, tp = (
        r["volume"], r["phrase"], r["paragraphe"], r["dialogue"],
        r["ponctuation_p1000"], r["lexique"], r["temps_heuristique"],
    )
    print(f"\n=== {r['nom']} ===")
    print(f"{v['mots']} mots · {v['phrases']} phrases · {v['paragraphes']} paragraphes")
    if v["mots"] < 1500:
        print("  ⚠ Échantillon court (<1500 mots) : indicateurs peu fiables.")

    print("\n-- Phrase --")
    print(f"  moyenne {ph['moyenne']} · médiane {ph['mediane']} · "
          f"écart-type {ph['ecart_type']} · amplitude {ph['min']}–{ph['max']}")
    print(f"  courtes (<8 mots) {ph['pct_courtes_moins_8']} % · "
          f"longues (>30 mots) {ph['pct_longues_plus_30']} %")

    print("\n-- Paragraphe --")
    print(f"  moyenne {pa['moyenne']} mots · médiane {pa['mediane']} · "
          f"max {pa['max']} · d'une seule phrase {pa['pct_une_phrase']} %")

    print("\n-- Dialogue --")
    print(f"  paragraphes de dialogue {di['pct_paragraphes']} % · "
          f"mots en dialogue {di['pct_mots']} %")
    print(f"  incises {di['incises_p1000']}/1000 mots "
          f"(dont neutres « dit-il » {di['incises_neutres_p1000']})")

    print("\n-- Ponctuation (pour 1000 mots) --")
    ligne = " · ".join(f"{k.replace('_', ' ')} {val}" for k, val in po.items())
    print(f"  {ligne}")

    print("\n-- Lexique --")
    print(f"  adverbes en -ment {lx['adverbes_ment_p1000']}/1000 · "
          f"verbes-filtres {lx['verbes_filtres_p1000']}/1000")
    print(f"  TTR {lx['ttr']} · hapax {lx['pct_hapax']} % · "
          f"mot moyen {lx['mot_moyen_lettres']} lettres")
    print("  mots pleins fréquents : " +
          ", ".join(f"{m} ({c})" for m, c in lx["top_mots_pleins"]))

    print("\n-- Temps (heuristique par terminaisons, pas une analyse morpho) --")
    print(f"  imparfait {tp['imparfait']} · passé simple {tp['passe_simple']} · "
          f"marqueurs de présent {tp['present_marqueurs']} → "
          f"dominante : {tp['dominante']}")


PLATS = [
    ("phrase.moyenne", "longueur moyenne de phrase", 15),
    ("phrase.mediane", "longueur médiane de phrase", 20),
    ("phrase.ecart_type", "variance de longueur (écart-type)", 25),
    ("phrase.pct_courtes_moins_8", "% de phrases courtes", 30),
    ("phrase.pct_longues_plus_30", "% de phrases longues", 30),
    ("paragraphe.moyenne", "longueur moyenne de paragraphe", 30),
    ("dialogue.pct_mots", "% de mots en dialogue", 30),
    ("dialogue.incises_p1000", "densité d'incises", 40),
    ("ponctuation_p1000.point_virgule", "point-virgule", 50),
    ("ponctuation_p1000.tiret_cadratin", "tiret cadratin", 50),
    ("ponctuation_p1000.suspension", "points de suspension", 50),
    ("ponctuation_p1000.virgule", "virgule", 25),
    ("lexique.adverbes_ment_p1000", "adverbes en -ment", 35),
    ("lexique.verbes_filtres_p1000", "verbes-filtres", 40),
    ("lexique.ttr", "richesse lexicale (TTR)", 20),
]


def lire(chemin_pointe: str, d: dict):
    for cle in chemin_pointe.split("."):
        d = d[cle]
    return d


def comparer(a: dict, b: dict):
    """a = texte analysé, b = référence."""
    print(f"\n=== Comparaison : {a['nom']} vs référence {b['nom']} ===")
    print(f"{'indicateur':38} {'texte':>10} {'référence':>10} {'écart':>10}")
    print("-" * 72)
    ecarts = []
    absents = []
    for chemin, libelle, seuil in PLATS:
        va, vb = lire(chemin, a), lire(chemin, b)
        if vb == 0 and va == 0:
            pct, marque = None, ""
        elif vb == 0:
            # trait présent dans le texte mais absent de la référence :
            # pas de pourcentage calculable, mais divergence bien réelle
            pct, marque = None, "  ⚠"
            absents.append((libelle, va))
        else:
            pct = (va - vb) / abs(vb) * 100
            marque = "  ⚠" if abs(pct) > seuil else ""
            if abs(pct) > seuil:
                ecarts.append((libelle, va, vb, pct))
        aff = "—" if pct is None else f"{pct:+.0f} %"
        print(f"{libelle:38} {va:>10} {vb:>10} {aff:>10}{marque}")

    print("\n-- Écarts marqués (au-delà du seuil de tolérance) --")
    if not ecarts and not absents:
        print("  aucun : le texte reste dans l'enveloppe du style de référence.")
    else:
        for libelle, va, vb, pct in ecarts:
            sens = "au-dessus" if pct > 0 else "en dessous"
            print(f"  • {libelle} : {va} contre {vb} ({pct:+.0f} %, {sens})")
        for libelle, va in absents:
            print(f"  • {libelle} : {va} dans le texte, nul dans la référence "
                  "— trait absent du style visé")
    print("\n  Rappel : un écart n'est pas une faute. Il peut être un choix "
          "assumé\n  (scène d'action, changement de POV). Il doit juste être vu.")

    ma, mb = a["volume"]["mots"], b["volume"]["mots"]
    if max(ma, mb) > 2 * min(ma, mb):
        print(f"\n  ⚠ Volumes très différents ({ma} vs {mb} mots) : la richesse "
              "lexicale\n    (TTR) décroît mécaniquement avec la longueur — "
              "ignorer cette ligne ici.")

    print(f"\n  Temps dominant — texte : {a['temps_heuristique']['dominante']} · "
          f"référence : {b['temps_heuristique']['dominante']}")
    if a["temps_heuristique"]["dominante"] != b["temps_heuristique"]["dominante"]:
        print("  ⚠ Dominante temporelle différente : à vérifier en priorité, "
              "c'est\n    l'écart de style le plus visible en lecture.")


def charger(chemin: str) -> str:
    p = Path(chemin)
    if not p.exists():
        raise SystemExit(f"Fichier introuvable : {chemin}")
    return p.read_text(encoding="utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser(
        description="Indicateurs quantitatifs de style (français).")
    ap.add_argument("fichier", help="texte à analyser (.md ou .txt)")
    ap.add_argument("--compare", metavar="REF",
                    help="fichier de référence à comparer")
    ap.add_argument("--json", action="store_true",
                    help="sortie JSON brute au lieu du rapport lisible")
    args = ap.parse_args()

    a = indicateurs(charger(args.fichier), Path(args.fichier).name)

    if args.json:
        out = {"texte": a}
        if args.compare:
            out["reference"] = indicateurs(
                charger(args.compare), Path(args.compare).name)
        json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    afficher(a)
    if args.compare:
        b = indicateurs(charger(args.compare), Path(args.compare).name)
        afficher(b)
        comparer(a, b)
    print("\nCes chiffres sont des indicateurs, pas un verdict : ils ne mesurent "
          "ni le\nsous-texte, ni le choix des détails, ni ce que l'auteur décide "
          "de taire.\n")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # sortie tronquée par un « | head »
        sys.stderr.close()
