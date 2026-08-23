#!/usr/bin/env python3
"""
find_dead_links.py — détecte les wikilinks morts dans un dump de contenu Obsidian.

Ce script ne parle jamais au vault directement (pas de réseau, pas de MCP) : il
travaille uniquement sur des fichiers JSON déjà récupérés via les tools MCP
`obsidian` (search_query) et déposés sur disque par l'appelant (Claude,
suivant les étapes du skill detecter-liens-morts). Stdlib uniquement, aucune
dépendance à installer.

Entrées attendues (voir SKILL.md Étape 1-2 pour comment les produire) :

  --dump FICHIER [FICHIER ...]
      Un ou plusieurs fichiers JSON, chacun une LISTE d'objets
      {"filename": "<path>", "result": "<contenu markdown complet>"}
      — c'est le format brut renvoyé par le tool search_query MCP quand la
      query inclut {"var": "content"}. Un fichier par lot (ex. un par
      sous-dossier de 01_Lore) pour éviter des réponses MCP trop grosses.
      C'est aussi le périmètre SOURCE : seuls les wikilinks sortants de ces
      fichiers sont analysés.

  --all-paths FICHIER
      JSON = liste de chemins (`filename`) — RÉSULTAT BRUT d'un search_query
      du type {"regexp": ["\\.md$", {"var": "path"}]} sur TOUT le vault
      (pas seulement le périmètre source). Sert à construire l'index de
      résolution (une fiche existe quelque part = pas un lien mort, même
      hors du périmètre source).

  --aliases FICHIER (optionnel)
      JSON = liste d'objets {"filename": "<path>", "result": [alias, ...]}
      — résultat brut d'un search_query du type
      {"and": [{"regexp": ["\\.md$", {"var": "path"}]}, {"var": "frontmatter.aliases"}]}
      Un alias vaut résolution au même titre qu'un nom de fichier : un lien
      qui matche un alias n'est PAS un lien mort, même si le fichier a un
      autre nom.

  --index-text FICHIER (optionnel)
      Texte brut de la section "Chantiers en cours" de 00_Systeme/Index.md
      (ou du fichier Index.md entier, un faux positif de sous-chaîne ici
      n'est pas grave). Sert uniquement à annoter "déjà tracké dans Index"
      — n'affecte jamais la détection elle-même.

  --out FICHIER
      Chemin du rapport JSON produit (voir la docstring de `build_report`
      pour la forme exacte).

Le rapport distingue deux catégories, car elles n'appellent pas la même
action de l'utilisateur :
  - "entites_absentes"   : aucune fiche ni alias ne matche nulle part dans le
                            vault → candidate à `creer-fiche`.
  - "quasi_doublons"      : le lien est bien mort, MAIS une fiche existante a
                            un nom proche (ex. [[Limbes]] vs `Les Limbes.md`
                            sans alias) → probablement un alias à ajouter ou
                            un lien à corriger, PAS une nouvelle fiche.
    Le rapprochement est une heuristique (difflib + comparaison après retrait
    d'article initial) : toujours à vérifier à l'œil, jamais un verdict
    certain.
"""

import argparse
import difflib
import json
import re
import sys
from collections import Counter, defaultdict

ARTICLES = ("le ", "la ", "les ", "l'", "l’")
PAREN_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")

ASSET_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp",
    ".pdf", ".mp3", ".mp4", ".wav", ".mov", ".m4a", ".ogg",
    ".excalidraw", ".canvas",
}

CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
WIKILINK_RE = re.compile(r"(!)?\[\[([^\[\]]+)\]\]")


def strip_code(content):
    """Retire les blocs de code (fences + inline) avant de chercher des
    wikilinks — un exemple de syntaxe dans un bloc de code n'est pas un
    vrai lien."""
    content = CODE_FENCE_RE.sub("", content)
    content = INLINE_CODE_RE.sub("", content)
    return content


def normalize(name):
    return name.strip().lower()


def strip_article(name_lower):
    for art in ARTICLES:
        if name_lower.startswith(art):
            return name_lower[len(art):]
    return name_lower


def basename_no_ext(path):
    name = path.rsplit("/", 1)[-1]
    if "." in name:
        name = name.rsplit(".", 1)[0]
    return name


def extract_targets(content):
    """Retourne la liste des cibles de wikilinks (chaînes brutes, telles
    qu'écrites après résolution des alias/headings/blocks), en excluant les
    embeds d'assets (images, pdf, excalidraw, canvas) et les liens purement
    internes à la même note (#Heading sans nom de fiche)."""
    targets = []
    content = strip_code(content)
    for is_embed, raw in WIKILINK_RE.findall(content):
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        # [[Cible|Alias affiché]] -> garder la partie avant le premier |
        left = raw.split("|", 1)[0].strip()
        # [[Cible#Heading]] / [[Cible^blockid]] -> couper au premier # ou ^
        cut = len(left)
        for sep in ("#", "^"):
            idx = left.find(sep)
            if idx != -1:
                cut = min(cut, idx)
        left = left[:cut].strip()
        if not left:
            continue
        if "/" in left:
            left = left.rsplit("/", 1)[-1].strip()
        # extension éventuelle
        ext = ""
        if "." in left:
            ext = "." + left.rsplit(".", 1)[-1].lower()
        if is_embed and ext in ASSET_EXTENSIONS:
            continue
        if ext in ASSET_EXTENSIONS:
            # lien non-embed vers un asset (rare) : pas une fiche, on ignore
            continue
        if ext == ".md":
            left = left[: -len(ext)]
        left = left.strip(" \\")
        if left:
            targets.append(left)
    return targets


def load_dump(paths):
    """Charge un ou plusieurs fichiers de dump {filename, result} et
    retourne une liste de (path, content)."""
    out = []
    for p in paths:
        with open(p, encoding="utf-8") as fh:
            data = json.load(fh)
        for entry in data:
            path = entry.get("filename")
            content = entry.get("result")
            if not path or not isinstance(content, str):
                continue
            out.append((path, content))
    return out


def load_all_paths(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    paths = []
    for entry in data:
        # accepte soit une liste de strings, soit une liste de {"filename": ...}
        if isinstance(entry, str):
            paths.append(entry)
        elif isinstance(entry, dict) and entry.get("filename"):
            paths.append(entry["filename"])
    return paths


def load_aliases(path):
    if not path:
        return {}
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    out = defaultdict(list)
    for entry in data:
        filename = entry.get("filename")
        result = entry.get("result")
        if not filename or not isinstance(result, list):
            continue
        for alias in result:
            if isinstance(alias, str) and alias.strip():
                out[filename].append(alias.strip())
    return out


def build_resolution_index(all_paths, aliases_by_file):
    """normalized_name -> chemin canonique de la fiche qui répond de ce nom
    (basename ou alias)."""
    index = {}
    for path in all_paths:
        base = basename_no_ext(path)
        index.setdefault(normalize(base), path)
    for path, aliases in aliases_by_file.items():
        for alias in aliases:
            index.setdefault(normalize(alias), path)
    return index


def find_near_matches(target_norm, resolution_index, limit=3, cutoff=0.78):
    keys = list(resolution_index.keys())
    matches = []
    seen_names = set()

    def add(name, confiance):
        if name not in seen_names:
            matches.append({"name": name, "confiance": confiance})
            seen_names.add(name)

    # 1. correspondance forte : égalité après retrait d'un article initial
    #    (ex. "Limbes" == "les limbes")
    stripped = strip_article(target_norm)
    for key in keys:
        if key != target_norm and strip_article(key) == stripped:
            add(resolution_index[key], "forte (article retiré)")

    # 2. correspondance forte : égalité après retrait d'un suffixe
    #    d'homonymie entre parenthèses (Conventions §6 : "Kael (lieu)")
    #    (ex. "Lamia" == "lamia (planète)")
    stripped_paren = PAREN_SUFFIX_RE.sub("", target_norm).strip()
    if stripped_paren and stripped_paren != target_norm:
        for key in keys:
            key_stripped = PAREN_SUFFIX_RE.sub("", key).strip()
            if key_stripped == stripped_paren:
                add(resolution_index[key], "forte (suffixe d'homonymie retiré)")
    for key in keys:
        key_stripped = PAREN_SUFFIX_RE.sub("", key).strip()
        if key_stripped and key_stripped != key and key_stripped == target_norm:
            add(resolution_index[key], "forte (suffixe d'homonymie retiré)")

    # 3. correspondance approximative (difflib) sur ce qui reste — cutoff
    #    volontairement strict : sur des noms courts (<8 caractères), le
    #    ratio de difflib produit facilement des faux positifs (ex. "Lamia"
    #    ~ "Lumina" à 0.73) ; on exige une similarité plus franche.
    remaining = [k for k in keys if resolution_index[k] not in seen_names]
    local_cutoff = cutoff if len(target_norm) >= 8 else max(cutoff, 0.85)
    close = difflib.get_close_matches(target_norm, remaining, n=limit, cutoff=local_cutoff)
    for key in close:
        add(resolution_index[key], "approximative (difflib)")

    return matches[:limit]


def cluster_dead_targets(entites_absentes, min_len=5, cutoff=0.85):
    """Regroupe entre elles les cibles mortes qui sont probablement la même
    entité sous une graphie différente (pluriel, variante, forme longue vs
    courte — ex. "Grande Bataille de Cyroldan" / "Bataille de Cyroldan").
    Ne fusionne JAMAIS silencieusement : ajoute juste un champ
    "variantes_probables" sur l'item qui a le plus d'occurrences dans
    chaque cluster, à vérifier à l'œil — l'heuristique n'a aucune
    connaissance du lore, seulement de la forme des chaînes."""
    n = len(entites_absentes)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    norms = [normalize(item["cible"]) for item in entites_absentes]
    word_re = re.compile(r"[^a-zàâäéèêëïîôöùûüç0-9]+")

    for i in range(n):
        for j in range(i + 1, n):
            a, b = norms[i], norms[j]
            if a == b:
                union(i, j)
                continue
            related = False
            if len(a) >= min_len and len(b) >= min_len:
                shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
                if re.search(r"(?<![\wàâäéèêëïîôöùûüç])" + re.escape(shorter) + r"(?![\wàâäéèêëïîôöùûüç])", longer):
                    related = True
                elif difflib.SequenceMatcher(None, a, b).ratio() >= cutoff:
                    related = True
            if related:
                union(i, j)

    clusters = defaultdict(list)
    for idx in range(n):
        clusters[find(idx)].append(idx)

    for members in clusters.values():
        if len(members) < 2:
            continue
        members.sort(key=lambda idx: -entites_absentes[idx]["occurrences"])
        main_idx = members[0]
        entites_absentes[main_idx]["variantes_probables"] = [
            {
                "cible": entites_absentes[i]["cible"],
                "occurrences": entites_absentes[i]["occurrences"],
                "sources": entites_absentes[i]["sources"],
            }
            for i in members[1:]
        ]
        for i in members[1:]:
            entites_absentes[i]["fusionnee_dans"] = entites_absentes[main_idx]["cible"]


def build_report(dump_entries, resolution_index, index_text):
    scanned = 0
    total_occurrences = 0
    # target_norm -> {"forms": Counter(display forms), "sources": set, "count": int}
    agg = defaultdict(lambda: {"forms": Counter(), "sources": set(), "count": 0})

    for path, content in dump_entries:
        scanned += 1
        for raw_target in extract_targets(content):
            norm = normalize(raw_target)
            total_occurrences += 1
            if norm in resolution_index:
                continue  # résolu, pas un lien mort
            agg[norm]["forms"][raw_target] += 1
            agg[norm]["sources"].add(path)
            agg[norm]["count"] += 1

    entites_absentes = []
    quasi_doublons = []

    for norm, data in agg.items():
        display = data["forms"].most_common(1)[0][0]
        near = find_near_matches(norm, resolution_index)
        already_in_index = bool(index_text) and display.lower() in index_text.lower()
        item = {
            "cible": display,
            "occurrences": data["count"],
            "nb_fiches_sources": len(data["sources"]),
            "sources": sorted(data["sources"]),
            "deja_tracke_index": already_in_index,
        }
        if near:
            item["candidats_proches"] = near
            quasi_doublons.append(item)
        else:
            entites_absentes.append(item)

    entites_absentes.sort(key=lambda x: -x["occurrences"])
    quasi_doublons.sort(key=lambda x: -x["occurrences"])

    cluster_dead_targets(entites_absentes)

    return {
        "fiches_scannees": scanned,
        "occurrences_wikilinks_total": total_occurrences,
        "cibles_mortes_distinctes": len(agg),
        "entites_absentes": entites_absentes,
        "quasi_doublons": quasi_doublons,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dump", nargs="+", required=True)
    ap.add_argument("--all-paths", required=True)
    ap.add_argument("--aliases")
    ap.add_argument("--index-text")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    dump_entries = load_dump(args.dump)
    all_paths = load_all_paths(args.all_paths)
    aliases_by_file = load_aliases(args.aliases)
    resolution_index = build_resolution_index(all_paths, aliases_by_file)

    index_text = ""
    if args.index_text:
        with open(args.index_text, encoding="utf-8") as fh:
            index_text = fh.read()

    report = build_report(dump_entries, resolution_index, index_text)

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    print(f"Fiches scannées : {report['fiches_scannees']}", file=sys.stderr)
    print(f"Occurrences de wikilinks total : {report['occurrences_wikilinks_total']}", file=sys.stderr)
    print(f"Cibles mortes distinctes : {report['cibles_mortes_distinctes']}", file=sys.stderr)
    print(f"  - entités absentes : {len(report['entites_absentes'])}", file=sys.stderr)
    print(f"  - quasi-doublons (fiche proche existante) : {len(report['quasi_doublons'])}", file=sys.stderr)
    print(f"Rapport écrit : {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
