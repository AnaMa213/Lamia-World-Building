# Modes de repli — Claude Code uniquement

À lire au moment de basculer, quand le MCP `obsidian` est absent ou tombe en
cours de session. Ces replis n'existent QUE là où un accès réel au vault est
possible (Claude Code sur la machine du vault). Dans claude.ai : échec MCP =
arrêt + signalement à l'utilisateur, jamais d'improvisation.

Hiérarchie : **MCP → CLI Obsidian → Fichiers/Git.** Tester dans cet ordre et
annoncer à l'utilisateur le mode utilisé.

## Repli 1 — CLI Obsidian (application Obsidian ouverte)

La CLI `obsidian` pilote l'instance Obsidian EN COURS D'EXÉCUTION : elle
exige que l'application soit ouverte. Vérifier la disponibilité avec
`obsidian help` ; si la commande échoue ou ne répond pas, passer au Repli 2.
Si plusieurs vaults sont ouverts, préfixer chaque commande de
`vault="<nom du vault Lamia>"`.

Équivalences avec le flux MCP du SKILL.md :

| Flux MCP | CLI |
|---|---|
| `vault_read` | `obsidian read path="01_Lore/… .md"` |
| `search_simple` | `obsidian search query="…" limit=10` |
| liens entrants (`backlinks`) | `obsidian backlinks file="Nom de la fiche"` |
| `vault_list` | `ls` du dossier (la CLI cible des fichiers, pas des dossiers) |
| `tags` du vault | `obsidian tags sort=count counts` |

Notes d'usage :
- `path=` prend un chemin exact depuis la racine du vault ; `file=` résout
  comme un wikilink (nom seul). Sans l'un ni l'autre, la CLI cible le
  fichier actif — pratique pour "la fiche ouverte", risqué partout ailleurs :
  toujours expliciter la cible.
- Il n'y a pas d'équivalent CLI de `search_query` (JsonLogic) : combiner
  `obsidian search` avec un triage manuel par zone des résultats, ou `Grep`
  sur disque pour un ciblage par chemin.

**Écriture.** Deux cas :
- Capture express (Mode C, une ligne de contenu) : la CLI convient —
  `obsidian create path="04_Brouillons/AAAA-MM-JJ HHhMM.md" content="---\nstatut: brouillon\n…" silent`.
  Toujours `silent` (sinon la note s'ouvre à l'écran), JAMAIS le flag
  `overwrite` : son absence est la protection contre l'écrasement.
- Fiche brainstorm complète : le contenu multiligne échappé (`\n`) dans un
  argument shell est fragile et illisible. Écrire plutôt le fichier
  directement sur disque (`Write`, comme au Repli 2) — Obsidian ouvert
  détecte le nouveau fichier tout seul — et réserver la CLI aux lectures et
  recherches. Puis appliquer le protocole git ci-dessous.

## Repli 2 — Fichiers/Git (application fermée)

Accès disque direct. Le vault est généralement la racine du repo git courant
en Claude Code — vérifier avec `ls` (présence de `00_Systeme/`, `01_Lore/`…)
avant toute écriture.

Équivalences :
- `vault_read` → `Read` (chemin relatif à la racine du vault). Timeline
  Master : toujours en entier, même en mode fichiers.
- `search_simple` / `search_query` → `Grep` (mots-clés, restreint au dossier
  voulu : `01_Lore/`, `05_IA_Inbox/Brainstorm/`…) et `Glob`
  (`01_Lore/**/*<terme>*.md`) pour repérer les candidats, puis `Read`.
  Le triage par zone du SKILL.md s'applique à l'identique.
- `vault_list` → `ls` / `Glob` sur le dossier (vérification de collision
  avant toute écriture, comme en MCP).
- `vault_write` → `Write` au même chemin, même contenu assemblé, mêmes
  règles (jamais écraser un fichier existant sans l'avoir lu et fusionné).
  Créer le dossier au besoin (`mkdir -p "05_IA_Inbox/Brainstorm"`).

## Protocole git (Replis 1 et 2, dès qu'un fichier est écrit sur disque)

Seulement si le vault est un dépôt git — vérifier d'abord avec
`git rev-parse --is-inside-work-tree`. Sinon, ignorer cette étape et le
mentionner dans la confirmation.

```bash
git add "05_IA_Inbox/Brainstorm/<nom du fichier>.md"
git commit -m "[brouillon IA] Brainstorm — <Sujet-en-un-mot>" -- "05_IA_Inbox/Brainstorm/<nom du fichier>.md"
```

Pour une capture express : même schéma sur `04_Brouillons/<fichier>.md`,
message `[brouillon IA] Capture rapide`.

Le préfixe `[brouillon IA]` garde l'historique git honnête : ce commit ne
vaut pas validation de l'auteur. Ne JAMAIS utiliser `git add -A`,
`git add .` ou `git commit -a` : stager et commiter uniquement le fichier
créé, jamais le reste de l'arbre de travail (qui peut contenir des
changements de l'utilisateur sans rapport).
