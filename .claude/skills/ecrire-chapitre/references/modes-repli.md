# Modes de repli — ecrire-chapitre

À lire uniquement **au moment** de basculer hors Mode MCP, en Claude Code avec
accès réel au vault. Dans claude.ai ou Cowork sans accès au vault : pas de
repli possible — un échec MCP s'annonce à l'utilisateur et la tâche s'arrête.
Tu peux continuer à travailler sur un texte collé, en disant explicitement que
le contrôle lore n'a pas pu être fait.

Les garde-fous du SKILL.md s'appliquent à l'identique dans tous les modes :
lecture seule sur `01_Lore`, `00_Systeme` et `99_Archive` ; écriture additive
seulement sur les chapitres ; productions IA dans `05_IA_Inbox` ; jamais de
chemin construit de mémoire.

## Mode CLI Obsidian (application Obsidian ouverte)

Vérifier d'abord que `obsidian help` répond. Sinon → Mode Fichiers/Git.
Syntaxe et commandes : le SKILL.md du skill `obsidian-cli` fait foi.

| Opération (Mode MCP) | Équivalent CLI |
|---|---|
| `vault_read` d'une fiche | `obsidian read file="Nom"` — résout comme un wikilink (nom seul, sans chemin ni extension), ce qui contourne les divergences d'accents |
| chemin exact d'une fiche | `obsidian search query="Nom"` |
| `search_simple` | `obsidian search query="…" limit=10` |
| `backlinks` (champ de `vault_read`) | `obsidian backlinks file="Nom"` |
| `active_file_get_path` (chapitre ouvert) | pas d'équivalent fiable — demander le chapitre à l'utilisateur |
| `vault_list` | `ls` / `Glob` sur le disque |
| `vault_append` sur un chapitre | **`Edit` disque** (ajout en fin de fichier), jamais `obsidian create` |
| `search_query`, `vault_get_document_map`, champ `links` | pas d'équivalent — lire les fiches en entier (`read`) et `Grep` sur le dossier |

**Écriture des notes produites** (fiche de style, carnet) : préférer l'écriture
disque (`Write`) même en mode CLI — le contenu multiligne passe mal en
paramètre CLI (`\n` littéraux). Créer `05_IA_Inbox/Styles/` ou
`05_IA_Inbox/Chapitres/` au préalable si absent (`mkdir -p`).

## Mode Fichiers/Git (application fermée)

- Lecture : `Read` (fiches de lore EN ENTIER quand elles sont centrales au
  sujet), recherche : `Grep` / `Glob` sur le vault.
- `01_Lore/Timeline Master.md` : toujours lu en entier, jamais en extrait.
- Backlinks approximés par `Grep` sur `[[Nom` — attention aux alias
  (`[[Nom|Affiché]]`) et aux liens vers headings (`[[Nom#Section]]`) : le motif
  doit rester le début du wikilink.
- Chemins réels : `Glob` sur le nom de fichier, jamais un chemin déduit de la
  doc (divergences d'accents constatées entre Conventions et dossiers réels).
- **Ajout sur un chapitre** : `Read` du fichier puis `Edit` qui n'ajoute qu'en
  fin de fichier. Ne jamais `Write` sur un fichier de `02_Romans/` — un `Write`
  écrase, et ce qu'il écrase est de la prose non versionnée ailleurs.
- Écriture des notes produites : `Write` dans `05_IA_Inbox/…`, `mkdir -p` au
  besoin.

## Git (modes locaux uniquement)

Seulement si le vault est un dépôt git
(`git rev-parse --is-inside-work-tree`) :

```bash
git add "05_IA_Inbox/Styles/<fichier>.md"
git commit -m "[brouillon IA] Style — <Nom>" -- "05_IA_Inbox/Styles/<fichier>.md"
```

Ne JAMAIS `git add -A` / `git add .` / `git commit -a` : uniquement les
fichiers réellement créés par cette session.

**Cas particulier du chapitre.** Si tu as ajouté une section de propositions en
fin d'un fichier de `02_Romans/`, ne le commite pas de ta propre initiative :
c'est de la prose en cours, l'auteur décide quand elle entre dans l'historique.
Signale-lui simplement que le fichier a été modifié.
