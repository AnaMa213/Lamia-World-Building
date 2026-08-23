#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_dumps.py -- Prepare tous les fichiers JSON requis par find_dead_links.py.

Lit les fichiers .md directement depuis le vault sur disque (pas de MCP),
écrit les dumps dans dump/, plus all_paths.json, aliases.json, index_text.txt.
Corrige aussi _raw_Créatures.json (wrapper MCP) → Créatures.json.

Usage: python3 create_dumps.py
"""
import json
import os
import sys

VAULT = r"D:\Lamia\Lamia - Worldbuilding"
HERE  = r"D:\Lamia\Lamia - Worldbuilding\.claude\skills\detecter-liens-morts"
DUMP  = os.path.join(HERE, "dump")

# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

def read_md(vault_rel_path):
    """Lit un .md depuis le vault (chemin relatif avec /)."""
    full = os.path.join(VAULT, vault_rel_path.replace("/", os.sep))
    with open(full, encoding="utf-8") as f:
        return f.read()


def make_dump(vault_paths, output_name):
    """Crée un dump JSON [{filename, result}] pour une liste de chemins vault."""
    entries = []
    for vp in vault_paths:
        try:
            content = read_md(vp)
            entries.append({"filename": vp, "result": content})
        except Exception as e:
            print(f"  WARN: impossible de lire {vp}: {e}", file=sys.stderr)
    out = os.path.join(DUMP, output_name)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {output_name} ({len(entries)} fiches)")
    return entries


def list_md_recursive(vault_subdir):
    """Liste tous les .md sous un sous-dossier vault (chemins relatifs /)."""
    base = os.path.join(VAULT, vault_subdir.replace("/", os.sep))
    out = []
    for root, dirs, files in os.walk(base):
        # Exclure les dossiers cachés
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in files:
            if fn.endswith(".md"):
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, VAULT).replace(os.sep, "/")
                out.append(rel)
    return sorted(out)


# ---------------------------------------------------------------------------
# 1. Fixer _raw_Créatures.json (wrapper MCP {type, text})
# ---------------------------------------------------------------------------
print("1. Correction de _raw_Créatures.json…")
raw_path = os.path.join(DUMP, "_raw_Créatures.json")
fixed_path = os.path.join(DUMP, "Créatures.json")
try:
    with open(raw_path, encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, list) and raw and "text" in raw[0]:
        inner = json.loads(raw[0]["text"])
    elif isinstance(raw, list) and raw and "filename" in raw[0]:
        inner = raw  # déjà bon format
    else:
        inner = raw
    with open(fixed_path, "w", encoding="utf-8") as f:
        json.dump(inner, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Créatures.json ({len(inner)} fiches)")
except Exception as e:
    print(f"  ERREUR Créatures: {e} — fallback: lecture directe du vault")
    make_dump(list_md_recursive("01_Lore/Créatures"), "Créatures.json")

# ---------------------------------------------------------------------------
# 2. Dumps des sous-dossiers reçus inline (lecture directe vault)
# ---------------------------------------------------------------------------
print("2. Création des dumps inline depuis le vault…")

# Essences
make_dump(list_md_recursive("01_Lore/Essences"), "Essences.json")

# Factions
make_dump(list_md_recursive("01_Lore/Factions"), "Factions.json")

# Magies
make_dump(list_md_recursive("01_Lore/Magies"), "Magies.json")

# Objets
make_dump(list_md_recursive("01_Lore/Objets"), "Objets.json")

# Peuples
make_dump(list_md_recursive("01_Lore/Peuples"), "Peuples.json")

# Systèmes
make_dump(list_md_recursive("01_Lore/Systèmes"), "Systèmes.json")

# Vocations
make_dump(list_md_recursive("01_Lore/Vocations"), "Vocations.json")

# Timeline Master (fichier à la racine de 01_Lore)
make_dump(["01_Lore/Timeline Master.md"], "Timeline.json")

# ---------------------------------------------------------------------------
# 3. all_paths.json — tous les .md du vault (sert à la résolution)
# ---------------------------------------------------------------------------
print("3. all_paths.json…")
all_paths = []
for root, dirs, files in os.walk(VAULT):
    dirs[:] = [d for d in dirs if not d.startswith(".")]
    for fn in files:
        if fn.endswith(".md"):
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, VAULT).replace(os.sep, "/")
            all_paths.append(rel)
all_paths.sort()
ap_path = os.path.join(HERE, "all_paths.json")
with open(ap_path, "w", encoding="utf-8") as f:
    json.dump([{"filename": p, "result": True} for p in all_paths], f,
              ensure_ascii=False, indent=2)
print(f"  ✓ all_paths.json ({len(all_paths)} fichiers)")

# ---------------------------------------------------------------------------
# 4. aliases.json — frontmatter.aliases de toutes les fiches .md du vault
# ---------------------------------------------------------------------------
print("4. aliases.json…")
import re

FM_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
ALIASES_RE = re.compile(r"^aliases\s*:\s*(.+)", re.MULTILINE)
ALIAS_LIST_ITEM = re.compile(r"^\s*-\s+(.+)", re.MULTILINE)

def extract_aliases(content):
    """Extrait les aliases depuis le frontmatter YAML d'une note."""
    m = FM_RE.match(content)
    if not m:
        return []
    fm_text = m.group(1)
    # cas 1 : aliases: [a, b]
    ma = re.search(r"^aliases\s*:\s*\[([^\]]*)\]", fm_text, re.MULTILINE)
    if ma:
        inside = ma.group(1)
        items = [s.strip().strip('"').strip("'") for s in inside.split(",")]
        return [i for i in items if i]
    # cas 2 : aliases: val (une valeur)
    ma = re.search(r"^aliases\s*:\s*(\S[^\n]*)", fm_text, re.MULTILINE)
    if ma:
        val = ma.group(1).strip().strip('"').strip("'")
        # si pas de tiret ci-dessous → valeur simple
        # chercher éventuellement des listes suivantes
        rest_start = ma.end()
        rest = fm_text[rest_start:]
        items = [val] if val else []
        for li in ALIAS_LIST_ITEM.finditer(rest):
            items.append(li.group(1).strip().strip('"').strip("'"))
        return [i for i in items if i and i != "[]"]
    # cas 3 : aliases:\n  - item
    ma = re.search(r"^aliases\s*:\s*\n((?:\s+-\s+.+\n?)*)", fm_text, re.MULTILINE)
    if ma:
        block = ma.group(1)
        return [li.group(1).strip().strip('"').strip("'")
                for li in ALIAS_LIST_ITEM.finditer(block)]
    return []

aliases_data = []
for p in all_paths:
    full = os.path.join(VAULT, p.replace("/", os.sep))
    try:
        with open(full, encoding="utf-8") as f:
            content = f.read()
        al = extract_aliases(content)
        if al:
            aliases_data.append({"filename": p, "result": al})
    except Exception:
        pass

al_path = os.path.join(HERE, "aliases.json")
with open(al_path, "w", encoding="utf-8") as f:
    json.dump(aliases_data, f, ensure_ascii=False, indent=2)
print(f"  ✓ aliases.json ({len(aliases_data)} fiches avec aliases)")

# ---------------------------------------------------------------------------
# 5. index_text.txt — section Chantiers en cours de Index.md
# ---------------------------------------------------------------------------
print("5. index_text.txt…")
index_content = read_md("00_Systeme/Index.md")
it_path = os.path.join(HERE, "index_text.txt")
with open(it_path, "w", encoding="utf-8") as f:
    f.write(index_content)
print(f"  ✓ index_text.txt ({len(index_content)} caractères)")

print("\nTout prêt. Lancer maintenant find_dead_links.py.")
