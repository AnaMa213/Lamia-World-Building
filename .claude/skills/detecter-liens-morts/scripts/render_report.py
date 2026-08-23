#!/usr/bin/env python3
"""
render_report.py — met en forme le report.json produit par
find_dead_links.py en une note markdown conforme aux conventions du vault
Lamia (frontmatter journal-chantier, notation ⚠️, sections cochables).

Usage :
    python3 render_report.py --report report.json --date 2026-08-20 \
        --scope "01_Lore" --out chantier.md

Le fichier produit est un BROUILLON à relire : ce script ne fait que mettre
en forme ce que find_dead_links.py a déjà calculé, il n'ajoute aucune
analyse. Toujours relire les sections avant de déposer via vault_write —
en particulier les clusters de variantes (heuristique de forme, pas de
lore) et les candidats de la section "fiche proche existante" (à vérifier
un par un : parfois un vrai alias manquant, parfois une coïncidence de
nommage sans rapport).
"""

import argparse
import json


def fmt_sources(sources, max_show=5):
    if len(sources) <= max_show:
        return ", ".join(f"[[{s.rsplit('/', 1)[-1][:-3]}]]" for s in sources)
    shown = sources[:max_show]
    rest = len(sources) - max_show
    txt = ", ".join(f"[[{s.rsplit('/', 1)[-1][:-3]}]]" for s in shown)
    return f"{txt}, +{rest} autre(s)"


def render(report, date, scope, self_name):
    lines = []
    lines.append("---")
    lines.append("statut: brouillon")
    lines.append("source: ai")
    lines.append("type: journal-chantier")
    lines.append("tags: [detecter-liens-morts]")
    lines.append(f"date: {date}")
    lines.append("---")
    lines.append("")
    lines.append("# Chantier — Liens morts")
    lines.append("")

    top_level_absentes = [x for x in report["entites_absentes"] if "fusionnee_dans" not in x]
    n_abs = len(top_level_absentes)
    n_quasi = len(report["quasi_doublons"])
    lines.append(
        f"**En une phrase :** Scan de `{scope}` ({report['fiches_scannees']} fiches, "
        f"{report['occurrences_wikilinks_total']} wikilinks) — {n_abs} entités "
        f"probablement absentes du vault, {n_quasi} liens cassés qui pointent "
        "peut-être vers une fiche déjà existante sous un autre nom."
    )
    lines.append("")
    lines.append(
        "> [!warning] Rien n'est arbitré — détection automatique à vérifier\n"
        "> Ce journal liste des wikilinks non résolus (aucune fiche ni alias "
        "correspondant nulle part dans le vault). Il ne crée aucune fiche, ne "
        "modifie aucune fiche existante. Les regroupements (« variantes "
        "probables ») et les rapprochements (« fiche proche existante ») sont "
        "des heuristiques de forme (orthographe, pluriel, article) — elles "
        "n'ont aucune connaissance du lore et peuvent se tromper. Chaque ligne "
        "reste `⚠️` à trancher par l'auteur."
    )
    lines.append("")

    lines.append("## Entités absentes du vault")
    lines.append(
        "*Candidates à `creer-fiche`, une par une — voir la fin de ce document.*"
    )
    lines.append("")
    for item in sorted(top_level_absentes, key=lambda x: -x["occurrences"]):
        tag = " · 🔁 déjà dans Index" if item["deja_tracke_index"] else ""
        lines.append(
            f"- [ ] ⚠️ **{item['cible']}** — {item['occurrences']} occurrence(s) "
            f"dans {item['nb_fiches_sources']} fiche(s) : {fmt_sources(item['sources'])}{tag}"
        )
        for v in item.get("variantes_probables", []):
            lines.append(
                f"    - variante probable : « {v['cible']} » "
                f"({v['occurrences']} occurrence(s), à vérifier — même entité ?)"
            )
    lines.append("")

    lines.append("## Liens cassés — fiche proche existante")
    lines.append(
        "*Probablement un alias à ajouter ou un lien à corriger, PAS une "
        "nouvelle fiche à créer — à vérifier un par un.*"
    )
    lines.append("")
    if not report["quasi_doublons"]:
        lines.append("*(aucun cas de ce type détecté)*")
    for item in report["quasi_doublons"]:
        tag = " · 🔁 déjà dans Index" if item["deja_tracke_index"] else ""
        cands = "; ".join(
            f"[[{c['name'].rsplit('/', 1)[-1][:-3]}]] ({c['confiance']})"
            for c in item["candidats_proches"]
        )
        lines.append(
            f"- [ ] ⚠️ **{item['cible']}** — {item['occurrences']} occurrence(s) "
            f"dans {item['nb_fiches_sources']} fiche(s) : {fmt_sources(item['sources'])} "
            f"— fiche(s) proche(s) : {cands}{tag}"
        )
    lines.append("")

    lines.append("## Texte à coller dans Index > Chantiers en cours")
    lines.append("")
    lines.append("```markdown")
    lines.append(f"#### Session {date} — Liens morts détectés (detecter-liens-morts)")
    lines.append("")
    for item in sorted(top_level_absentes, key=lambda x: -x["occurrences"])[:20]:
        lines.append(
            f"- [ ] **[CRÉER]** Fiche **{item['cible']}** "
            f"(lien cassé, {item['occurrences']} occurrence(s) — voir "
            f"[[{self_name}]])"
        )
    if len(top_level_absentes) > 20:
        lines.append(
            f"- [ ] … {len(top_level_absentes) - 20} autre(s) entité(s) absente(s) "
            f"— liste complète dans [[{self_name}]]"
        )
    for item in report["quasi_doublons"][:10]:
        best = item["candidats_proches"][0]["name"].rsplit("/", 1)[-1][:-3]
        lines.append(
            f"- [ ] **[CHANTIER]** Vérifier si `[[{item['cible']}]]` doit devenir "
            f"un alias de [[{best}]] ou être corrigé dans le texte "
            f"({item['nb_fiches_sources']} fiche(s) concernée(s))"
        )
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--scope", default="01_Lore")
    ap.add_argument("--out", required=True)
    ap.add_argument(
        "--self-name",
        help="Nom (sans extension) que portera la note une fois déposée dans "
        "le vault, ex. '2026-08-20 — Chantier — Liens-Morts' — utilisé pour "
        "que les auto-références ([[...]] vers 'voir la liste complète ici') "
        "pointent vers le bon fichier. Si omis, dérivé de --date.",
    )
    args = ap.parse_args()
    self_name = args.self_name or f"{args.date} — Chantier — Liens-Morts"

    report = json.load(open(args.report, encoding="utf-8"))
    md = render(report, args.date, args.scope, self_name)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"Rendu écrit : {args.out}")


if __name__ == "__main__":
    main()
