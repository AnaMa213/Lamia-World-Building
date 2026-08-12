# Modes de repli — brainstorm-lore

À lire uniquement AU MOMENT de basculer hors Mode MCP, en Claude Code avec
accès réel au vault. Dans claude.ai : pas de repli possible — un échec MCP
s'annonce à l'utilisateur et la tâche s'arrête.

Les garde-fous du SKILL.md s'appliquent à l'identique dans tous les modes :
jamais de canon promu, jamais d'écriture dans `00_Systeme` ni `99_Archive`,
jamais de chemin construit de mémoire, jamais de wikilink non vérifié.

## Mode CLI Obsidian (application Obsidian ouverte)

Vérifier d'abord que `obsidian help` répond. Sinon → Mode Fichiers/Git.
Syntaxe et commandes : `/mnt/skills/user/obsidian-cli/SKILL.md` fait foi.

| Opération (Mode MCP) | Équivalent CLI |
|---|---|
| `vault_read` d'une fiche | `obsidian read file="Nom"` — résout comme un wikilink (nom seul, sans chemin ni extension), ce qui contourne les divergences d'accents |
| chemin exact d'une fiche | `obsidian search query="Nom"` |
| `search_simple` | `obsidian search query="…" limit=10` |
| `search_query` (JsonLogic) | pas d'équivalent CLI — lire les fiches candidates en entier (`read`) et filtrer à la main, ou `Grep` sur le dossier du vault |
| `active_file_get_path` (Mode A, "fiche active") | pas d'équivalent CLI connu — demander à l'utilisateur le nom de la fiche ouverte plutôt que deviner |
| `backlinks` (champ de `vault_read`) | `obsidian backlinks file="Nom"` |
| `vault_list` | `ls` / `Glob` sur le disque |
| `vault_get_document_map`, champ `links` | pas d'équivalent CLI — lire la fiche en entier (`read`) |

**Écriture de la fiche brainstorm ou de la capture Mode C** : préférer
l'écriture disque (`Write`) même en mode CLI — le contenu multiligne passe
mal en paramètre CLI (`\n` littéraux). Créer `05_IA_Inbox/Brainstorm/` (ou
`04_Brouillons/` pour le Mode C) au préalable si absent (`mkdir -p`).
`Brainstorms.base` : copie disque du fichier `assets/Brainstorms.base` si
absente, jamais réécrite si présente.

**Ajout dans une fiche brainstorm existante** (fusion, "Assembler et
enregistrer" étape 3) : pas d'équivalent CLI pour un ciblage de section —
utiliser `Edit` après avoir relu le fichier en entier.

## Mode Fichiers/Git (application fermée)

- Lecture : `Read` (fiches EN ENTIER), recherche : `Grep`/`Glob` sur le
  vault.
- Backlinks approximés par `Grep` sur `[[Nom` — attention aux alias
  (`[[Nom|Affiché]]`) et aux liens vers headings (`[[Nom#Section]]`) : le
  motif de recherche doit rester le début du wikilink, pas sa forme exacte.
- "Fiche active" (Mode A) : pas d'équivalent fichier — demander le nom à
  l'utilisateur.
- Chemins réels : `Glob` sur le nom de fichier, jamais un chemin déduit de
  la doc (divergences d'accents constatées entre Conventions et dossiers
  réels, ex. `01_Lore/Évenements/` à un seul accent).
- Écriture : `Write` de la fiche (et de `Brainstorms.base` si absente) dans
  `05_IA_Inbox/Brainstorm/`, ou de la capture dans `04_Brouillons/` (Mode
  C), `mkdir -p` au besoin. Pour une fusion dans une fiche existante :
  `Read` intégral puis `Edit` ciblé, jamais une réécriture qui perdrait du
  contenu non relu.

## Git (modes locaux uniquement)

Seulement si le vault est un dépôt git
(`git rev-parse --is-inside-work-tree`) :

```bash
git add "05_IA_Inbox/Brainstorm/<fichier>.md"
git commit -m "[brouillon IA] Brainstorm — <Sujet>" -- "05_IA_Inbox/Brainstorm/<fichier>.md"
```

Pour une capture Mode C : même logique sur `04_Brouillons/<fichier>.md`,
message `"[brouillon IA] Capture — <horodatage>"`. Si `Brainstorms.base`
vient d'être créée dans la même session, l'ajouter aux deux commandes
(fichier par fichier). Ne JAMAIS `git add -A` / `git add .` /
`git commit -a` : uniquement les fichiers réellement créés par cette
session.
