---
type: systeme
date: 2026-07-16
version: "1.0"
---
# Skills Obsidian disponibles (Claude Code)

> Fiche mémo : les skills liés à Obsidian accessibles via l'outil `Skill` dans
> cette session Claude Code, et ce que chacun permet. À distinguer des outils
> MCP `obsidian-mcp-server` (section 6), qui parlent directement au vault via
> l'API REST du plugin Obsidian Local REST API.

## 1. `obsidian:defuddle`

**Ce que ça fait :** extrait le contenu propre d'une page web en Markdown via
l'outil Defuddle CLI, en retirant la navigation, les pubs et le bruit.

**Quand l'utiliser :** dès qu'on donne une URL à lire/analyser (doc en ligne,
article, blog). Remplace `WebFetch` pour ces cas — plus économe en tokens.

**Ne pas utiliser pour :** les URLs qui pointent déjà vers un fichier `.md`
brut (autant les lire directement).

## 2. `obsidian:json-canvas`

**Ce que ça fait :** crée et édite des fichiers `.canvas` (format JSON Canvas)
— nœuds, arêtes, groupes, connexions.

**Quand l'utiliser :** pour des canvases visuels dans Obsidian — cartes
mentales, schémas de relations, flowcharts. Utile par exemple pour
visualiser des réseaux de personnages, de factions ou une chronologie
graphique de Lamia.

## 3. `obsidian:obsidian-bases`

**Ce que ça fait :** crée et édite des fichiers `.base` — vues façon base de
données sur un ensemble de notes (tables, cartes), avec filtres, formules et
agrégats (summaries).

**Quand l'utiliser :** pour construire des vues type tableau/liste filtrées
sur un type de note (ex. lister toutes les divinités par rang, tous les
événements d'une ère). Complète les vues Dataview déjà utilisées dans
[[Tableau de bord]].

## 4. `obsidian:obsidian-cli`

**Ce que ça fait :** pilote le vault Obsidian en ligne de commande — lire,
créer, chercher, gérer notes/tâches/propriétés ; recharger des plugins,
exécuter du JS, capturer des erreurs, screenshots, inspection du DOM.

**Quand l'utiliser :** opérations vault en CLI, et surtout développement/
débogage de plugins ou thèmes Obsidian (hors du périmètre lore actuel, mais
utile si un jour on développe un plugin custom pour Lamia).

## 5. `obsidian:obsidian-markdown`

**Ce que ça fait :** écrit/édite du Markdown "Obsidian Flavored" — wikilinks
`[[...]]`, embeds `![[...]]`, callouts `> [!note]`, propriétés (frontmatter),
et autre syntaxe spécifique à Obsidian.

**Quand l'utiliser :** systématiquement pour toute fiche de lore du vault —
c'est la syntaxe de référence pour respecter [[Conventions]] (wikilinks
obligatoires, frontmatter typé, etc.).

---

## 6. (Complément) Outils MCP `obsidian-mcp-server`

Pas des "skills" à proprement parler, mais des outils MCP qui parlent
directement au vault via le plugin Local REST API d'Obsidian. Chaque note est
adressée par son chemin relatif au vault, extension incluse
(ex. `01_Lore/Divinités/Nom.md`).

| Outil | Fonction |
|---|---|
| `obsidian_list_notes` | Lister les notes d'un dossier |
| `obsidian_get_note` | Lire le contenu d'une note |
| `obsidian_search_notes` | Recherche plein texte dans le vault |
| `obsidian_write_note` | Créer/remplacer une note |
| `obsidian_append_to_note` | Ajouter du contenu en fin de note |
| `obsidian_patch_note` | Édition ciblée (section, heading, bloc) |
| `obsidian_replace_in_note` | Remplacement de texte dans une note |
| `obsidian_delete_note` | Supprimer une note |
| `obsidian_manage_frontmatter` | Lire/modifier les propriétés YAML |
| `obsidian_manage_tags` | Gérer les tags (hiérarchiques `parent/enfant`) |
| `obsidian_list_tags` | Lister les tags utilisés dans le vault |
| `obsidian_open_in_ui` | Ouvrir une note dans l'appli Obsidian |

Ces outils sont "déférés" : ils doivent être chargés via `ToolSearch`
(`select:mcp__obsidian-mcp-server__...`) avant le premier appel dans une
session.

---

## 7. Scénarios de prompts par cas d'usage

Pour chaque cas, un exemple de prompt et les skills/outils que ça mobilise
normalement. Objectif : savoir quoi taper selon ce qu'on veut obtenir.

### 7.1 Création d'une fiche

> *"Crée-moi la fiche de la divinité Nyxara, déesse mineure du crépuscule,
> vénérée par les peuples des marches d'Aldania."*

- `obsidian:obsidian-markdown` → frontmatter conforme (`statut`, `source`,
  `type: divinite`, `rang`, etc.) + structure de fiche imposée par
  [[Conventions]] (Résumé/Histoire/Apparence/...).
- `obsidian_search_notes` (MCP) → vérifier qu'aucune fiche homonyme n'existe
  déjà avant de créer.
- `obsidian_write_note` (MCP) → dépose la note au bon endroit
  (`01_Lore/Divinités/Nyxara.md`), `statut: brouillon` par défaut sauf
  validation explicite.
- Rappel : une note neuve doit contenir au moins un wikilink existant et
  être ajoutée à la MOC de son type (§8 Conventions) — sinon c'est un
  orphelin à corriger.

### 7.2 Modification d'une fiche existante

> *"Dans la fiche de l'Ordre du Cercle Brisé, ajoute une section sur leur
> rivalité avec les Gardiens et corrige leur date de fondation à 1204 È.V."*

- `obsidian_get_note` (MCP) → relit la fiche actuelle avant toute édition.
- Si la fiche est `canon` ou `canon-verrouillé` : audit d'impact d'abord —
  chercher les notes liées (`obsidian_search_notes`) qui pourraient devenir
  incohérentes.
- `obsidian_patch_note` ou `obsidian_replace_in_note` (MCP) → édition ciblée
  plutôt que réécriture complète, pour ne pas perdre le reste de la fiche.
- `obsidian:obsidian-markdown` → garde la syntaxe (wikilinks, callouts) et
  le format de date correct (`JJ Mois AAAA È.V.`).

### 7.3 Brainstorm d'idée dans une fiche en brouillon

> *"J'ai une idée : et si les Cinq du Voile étaient en fait les restes d'un
> sixième dieu oublié ? Note ça vite fait, je creuserai plus tard."*

- Pas de formatage complet à la capture (§9 Conventions) : une idée = une
  note dans `04_Brouillons`, juste `statut: brouillon` + une ligne de
  contenu.
- `obsidian_write_note` ou `obsidian_append_to_note` (MCP) → capture rapide,
  sans structure imposée.
- `obsidian:obsidian-markdown` reste utile a minima pour le frontmatter,
  mais aucune section obligatoire ici — la règle du §8 (liens/MOC) ne
  s'applique pas à `04_Brouillons`.
- Le tri/formatage se fera plus tard, lors d'une relecture dédiée.

### 7.4 Réflexion sans écriture sur un sujet

> *"Est-ce que la chronologie de la Grande Guerre divine tient debout si
> Nyxara est apparue après la fin de l'Ère Sérénale ? On n'écrit rien,
> je veux juste réfléchir avec toi."*

- Aucun skill d'écriture n'est déclenché : on reste en lecture/consultation.
- `obsidian_search_notes` / `obsidian_get_note` (MCP) → rassembler le
  contexte ([[Timeline Master]], fiches d'ères, fiches concernées) pour
  nourrir la discussion.
- Si une incohérence apparaît, elle est signalée en conversation — pour
  qu'elle passe dans les "Chantiers en cours" de [[Index]], il faut le
  demander explicitement (ça, c'est une écriture).

### 7.5 Import et synthèse d'une source externe

> *"Regarde cet article sur les mythes de crépuscule dans les traditions
> nordiques, et fais-moi une note d'inspiration à trier dans l'Inbox IA."*

- `obsidian:defuddle` → extrait le texte propre de la page web (au lieu de
  `WebFetch`, plus économe en tokens).
- `obsidian:obsidian-markdown` → mise en forme de la note de synthèse.
- `obsidian_write_note` (MCP) → dépôt dans `05_IA_Inbox/`, `source: ia`,
  à valider/reclasser ensuite par l'auteur.

### 7.6 Vérification de cohérence avant passage en canon

> *"Je veux valider la fiche d'Aldania en `canon`. Vérifie d'abord que rien
> ne la contredit ailleurs dans le vault."*

- `obsidian_search_notes` + `obsidian_list_tags` (MCP) → repère toutes les
  notes qui référencent Aldania (lieux, événements, personnages liés).
- Pas de skill d'écriture tant que l'arbitrage n'est pas tranché : on
  rapporte les contradictions trouvées, l'auteur décide (seul lui attribue
  `canon`/`canon-verrouillé`, §1 Conventions).
- Une fois validé : `obsidian_manage_frontmatter` (MCP) pour passer le
  `statut`, et vider la section "Contradictions potentielles" de la fiche.

### 7.7 Vue/tableau filtré sur un ensemble de fiches

> *"Fais-moi une vue qui liste toutes les divinités par rang, avec leur
> état (active/voilée/bannie/morte)."*

- `obsidian:obsidian-bases` → génère un fichier `.base` avec filtre
  `type: divinite`, colonnes `rang`/`etat`, éventuellement groupé.
- Alternative légère : Dataview directement dans une note (déjà en place
  dans [[Tableau de bord]]) si on ne veut pas un fichier `.base` séparé.

### 7.8 Carte visuelle de relations

> *"Fais-moi un canvas qui montre les alliances et rivalités entre les
> grandes factions de l'Ère du Voile."*

- `obsidian:json-canvas` → crée un `.canvas` avec un nœud par faction et des
  arêtes annotées (allié / rival / vassal).
- Peut référencer les fiches existantes (nœuds de type "note liée") plutôt
  que dupliquer le contenu.
