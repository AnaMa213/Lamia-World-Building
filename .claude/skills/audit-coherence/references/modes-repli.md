# Modes de repli — audit-coherence

À lire uniquement AU MOMENT de basculer hors Mode MCP, en Claude Code avec
accès réel au vault. Dans claude.ai : pas de repli possible — un échec MCP
s'annonce à l'utilisateur et la tâche s'arrête.

Les garde-fous du SKILL.md s'appliquent à l'identique dans tous les modes :
lecture seule sur les cibles, seules écritures = journal + `Audits.base`,
jamais `00_Systeme` ni `99_Archive`, jamais de chemin construit de mémoire.

## Mode CLI Obsidian (application Obsidian ouverte)

Vérifier d'abord que `obsidian help` répond. Sinon → Mode Fichiers/Git.
Syntaxe et commandes : `/mnt/skills/user/obsidian-cli/SKILL.md` fait foi.

| Opération (Mode MCP) | Équivalent CLI |
|---|---|
| `vault_read` d'une fiche | `obsidian read file="Nom"` — résout comme un wikilink (nom seul, sans chemin ni extension), ce qui contourne les divergences d'accents |
| chemin exact d'une fiche | `obsidian search query="Nom"` |
| `search_simple` | `obsidian search query="…" limit=10` |
| `backlinks` (champ de `vault_read`) | `obsidian backlinks file="Nom"` — équivalent natif, à utiliser systématiquement à l'Étape 2 |
| `tag_list` | `obsidian tags sort=count counts` |
| `vault_list` | `ls` / `Glob` sur le disque |
| `search_query`, `vault_get_document_map`, champ `links` | pas d'équivalent CLI — lire les fiches en entier (`read`) et `Grep` sur le dossier du vault |

**Écriture du journal** : préférer l'écriture disque (`Write`) même en mode
CLI — le contenu multiligne du journal passe mal en paramètre CLI (`\n`
littéraux). `obsidian create name="…" content="…" silent` reste acceptable
pour un journal très court. Créer `05_IA_Inbox/Audits/` au préalable si
absent (`mkdir -p`). `Audits.base` : copie disque du fichier
`assets/Audits.base` si absente, jamais réécrite si présente.

## Mode Fichiers/Git (application fermée)

- Lecture : `Read` (fiches EN ENTIER), recherche : `Grep`/`Glob` sur le
  vault.
- Backlinks approximés par `Grep` sur `[[Nom` — attention aux alias
  (`[[Nom|Affiché]]`) et aux liens vers headings (`[[Nom#Section]]`) : le
  motif de recherche doit rester le début du wikilink, pas sa forme exacte.
- Chemins réels : `Glob` sur le nom de fichier, jamais un chemin déduit de
  la doc (divergences d'accents constatées entre Conventions et dossiers
  réels).
- Écriture : `Write` du journal (et de `Audits.base` si absente) dans
  `05_IA_Inbox/Audits/`, `mkdir -p` au besoin.

## Git (modes locaux uniquement)

Seulement si le vault est un dépôt git
(`git rev-parse --is-inside-work-tree`) :

```bash
git add "05_IA_Inbox/Audits/<fichier>.md"
git commit -m "[brouillon IA] Audit — <Cible>" -- "05_IA_Inbox/Audits/<fichier>.md"
```

Si `Audits.base` vient d'être créée dans la même session, l'ajouter aux
deux commandes (fichier par fichier). Ne JAMAIS `git add -A` / `git add .` /
`git commit -a` : uniquement les fichiers réellement créés par cette
session d'audit.
