---
name: migrer-fiche
description: Analyse une fiche de 99_Archive (ancien vault, non-canon) et produit une proposition de migration vers 01_Lore selon le protocole en 9 points, déposée dans 05_IA_Inbox. Utilise ce skill dès que l'utilisateur demande de migrer, analyser, convertir ou reprendre une fiche d'archive — "migre [nom]", "analyse cette fiche d'archive", "commence la migration de X", ou quand il nomme/colle un chemin sous 99_Archive. Ne jamais utiliser sur des fichiers hors 99_Archive.
compatibility: Fonctionne avec le MCP obsidian-mcp-server connecté au vault Lamia (obsidian_search_notes, obsidian_get_note, obsidian_list_notes, obsidian_write_note). En Claude Code, si ce MCP est absent, bascule sur un accès disque direct (Read/Write/Glob/Grep/Bash) et git — voir "Deux modes d'accès au vault".
---

# Migrer une fiche — Lamia

Ce skill applique le protocole de migration en 9 points sur UNE fiche de
99_Archive à la fois : lecture complète de la source, comparaison au canon
déjà migré, puis dépôt d'un brouillon dans 05_IA_Inbox. Il ne modifie jamais
99_Archive au-delà de la lecture, et ne touche jamais 01_Lore directement.

## Décision actée (2026-07-17) — à ne pas rouvrir sans en parler à l'utilisateur

`00_Systeme/Conventions.md` §11 dit qu'une fiche migrée va directement dans
`01_Lore/` en `statut: brouillon`. Ce skill suit une règle différente,
tranchée explicitement par l'utilisateur : **le brouillon migré est déposé
dans `05_IA_Inbox/`, et le déplacement vers `01_Lore` reste le geste de
l'utilisateur, jamais celui de l'IA.** Conventions §11 est donc obsolète sur
ce point précis et devrait être corrigée par l'utilisateur lui-même
(00_Systeme reste fermé en écriture à l'IA) — le signaler une fois si
l'occasion se présente, sans reproposer le débat à chaque migration.

## Deux modes d'accès au vault

Ce skill dépend normalement du MCP `obsidian-mcp-server`. Deux cas de figure :

- **Mode MCP (par défaut)** : les tools `obsidian_get_note`,
  `obsidian_search_notes`, `obsidian_write_note`, `obsidian_list_notes` sont
  disponibles → comportement décrit plus bas, inchangé.
- **Mode Fichiers/Git (Claude Code uniquement)** : si ces tools sont absents,
  ou si l'un d'eux échoue en cours de session, ET que Claude a un accès
  disque direct au vault (racine du repo git courant). Chaque étape MCP a son
  équivalent Fichiers, indiqué par « **Si MCP indisponible :** ».

⚠️ Ce mode de repli n'existe QUE là où un accès disque réel au vault est
possible. Dans claude.ai, un échec MCP doit être signalé à l'utilisateur et
la tâche interrompue — jamais improvisé.

## Étape 0 — Contexte (une fois par session, si pas déjà fait)

Charger `00_Systeme/Conventions.md` et `00_Systeme/Index.md` s'ils ne sont
pas déjà dans le contexte de la conversation en cours (`obsidian_get_note`,
**si MCP indisponible :** `Read`). Ce skill dépend fortement du contenu EXACT
et À JOUR de Conventions §1 (statuts), §2 (types), §3 (frontmatter), §4
(structure des fiches), §5 (datation), §6 (nommage), §7 (arborescence) —
ne jamais travailler sur un souvenir d'une version antérieure du fichier.

## Étape 1 — Identifier et lire la fiche source

Si l'utilisateur nomme une fiche sans chemin précis, chercher dans
`99_Archive` (`obsidian_search_notes`, `pathPrefix: "99_Archive"`).
**Si MCP indisponible :** `Grep`/`Glob` sur `99_Archive/`.
Si plusieurs fiches correspondent, présenter les candidats et demander
laquelle avant de continuer.

Lire la fiche cible EN ENTIER (`obsidian_get_note`, format content).
**Si MCP indisponible :** `Read` en entier.
Ne jamais analyser à partir d'un extrait ou d'un résumé.

## Étape 2 — Rechercher le canon existant et la chronologie

Chercher ce qui existe déjà sur le même sujet/entité dans `01_Lore`
(`obsidian_search_notes`, `pathPrefix: "01_Lore"`), puis lire réellement les
fiches les plus pertinentes (`obsidian_get_note`).
**Si MCP indisponible :** `Grep`/`Glob` sur `01_Lore/`, puis `Read`.

Si la fiche source contient des éléments datés : charger
`01_Lore/Timeline Master.md` EN ENTIER (jamais de mémoire).
**Si MCP indisponible :** `Read` ce fichier en entier.

## Étape 3 — Produire l'analyse en 9 points

Présenter les 9 points dans la conversation, dans cet ordre, avant d'écrire
quoi que ce soit :

1. **Type proposé** — un type de la liste fermée (Conventions §2).
   Justifier si ambigu. Si la fiche mélange plusieurs entités ou portées,
   le signaler comme risque de scission (règle une-entité-une-note, §4).
2. **En une phrase** — le résumé d'une ligne obligatoire (§4).
3. **Statut proposé** — une recommandation parmi les 7 statuts (§1), justifiée
   par la nature du contenu. C'est une recommandation dans le rapport, PAS
   ce qui sera écrit dans le frontmatter : le brouillon déposé reste
   TOUJOURS `statut: brouillon` (§11 — aucune promotion automatique, seul
   l'auteur promeut en semi-canon/canon à la relecture).
4. **Éléments datés** → lister les entrées à créer ou vérifier dans
   [[Timeline Master]] (§5). Identifier seulement — ne jamais éditer
   Timeline Master directement depuis ce skill (fichier central à fort
   impact, modification réservée à un geste explicite de l'utilisateur).
5. **Liens** — entités déjà existantes (vérifiées à l'Étape 2) à wikilinker,
   et entités mentionnées mais absentes du vault (candidates futures,
   listées seulement, jamais créées par ce skill).
6. **Contradictions et doublons** — comparaison réelle avec le canon lu à
   l'Étape 2 et avec Timeline Master si pertinent. Jamais supposé.
7. **Risques** — doublon de rôle avec une entité existante, note à scinder,
   zone floue à trancher plus tard.
8. **Destination** — dossier cible selon la table type→dossier de
   Conventions §7, et nom de fichier selon la règle des homonymes (§6 :
   `Nom (type).md` en cas de collision, le nom nu devient alias des deux).
   ⚠️ Le dossier réel des événements est `01_Lore/Évenements/` (un seul
   accent) malgré `Événements/` écrit en Conventions §7 — piège MCP connu,
   utiliser la forme qui fonctionne.
9. **Action recommandée** — migrer / scinder / fusionner avec [[X existant]]
   / obsolète (contenu périmé, ne migre pas).

## Étape 4 — Assembler le brouillon migré

Construire la note reformatée :

- **Frontmatter** conforme à Conventions §3 (champs de base + champs
  spécifiques au type retenu au point 1 — ex. `rang` est OBLIGATOIRE pour
  `divinite`, `importance` pour `evenement`). Si un champ obligatoire ne
  peut pas être rempli depuis la source, marquer `⚠️ à compléter` plutôt que
  d'inventer une valeur. `statut: brouillon`, `source: ia` toujours.
- **Corps** : "En une phrase :" en premier (§4). Pour `divinite`/`personnage`,
  suivre l'ordre de sections de §4 (Résumé/Histoire/Apparence/Désir
  conscient/Besoin profond/Croyance fausse/Faille intime/Relations/
  Contradictions potentielles) — les 4 sections psychologiques restent
  facultatives pour une entité mineure. Pour les autres types, utiliser le
  template correspondant dans `00_Systeme/Templates/` s'il existe. **S'il
  n'existe aucun template pour ce type (ex. `peuple`, actuellement absent
  des Templates), le dire explicitement plutôt que d'improviser une
  structure silencieusement** — proposer une structure minimale
  (Résumé / Relations / Contradictions potentielles) et signaler le manque.
- **Contradictions potentielles** : rempli avec les constats du point 6
  (règle §4 : rempli à la création, vidé après arbitrage par l'utilisateur).
- Au moins un wikilink réel vers une entité existante (§8).
- Noter dans le rapport (pas dans un fichier verrouillé) quelle MOC de
  `Index` devra être mise à jour — Index reste fermé en écriture à l'IA.

## Étape 5 — Enregistrer

Nom de fichier : `AAAA-MM-JJ — Proposition — Migration [Nom].md` (aligné sur
les migrations déjà déposées dans 05_IA_Inbox). Écrire dans `05_IA_Inbox/`
via `obsidian_write_note` (`overwrite: false`).

**Si MCP indisponible :** créer le fichier avec `Write`, même chemin, même
contenu. Puis, seulement si le vault est un dépôt git
(`git rev-parse --is-inside-work-tree`) :
```bash
git add "05_IA_Inbox/<nom du fichier>.md"
git commit -m "[brouillon IA] Migration — <Nom>" -- "05_IA_Inbox/<nom du fichier>.md"
```
Ne JAMAIS `git add -A`/`git add .`/`git commit -a` : uniquement ce fichier.

Ne PAS toucher `99_Archive` à ce stade : la bannière `> Migré vers [[X]]`
n'est ajoutée qu'au moment où l'utilisateur valide et déplace réellement le
brouillon vers `01_Lore` — c'est son geste, jamais une action automatique de
ce skill.

## Étape 6 — Confirmer

Présenter : les 9 points, le chemin du fichier créé (+ commit git s'il a eu
lieu), et un rappel explicite que rien n'est canon — ni la fiche déposée
(brouillon), ni Timeline Master (pas touché), ni la MOC (pas touchée), ni
l'archive (pas de bannière) — tant que l'utilisateur n'a pas validé et
déplacé lui-même le contenu vers 01_Lore.

## Garde-fous

- Jamais `canon` ou `canon-verrouillé` écrit par ce skill — toujours
  `brouillon` + `source: ia`, quel que soit le statut recommandé au point 3.
- Jamais de wikilink vers une entité non vérifiée par recherche à l'Étape 2.
- Jamais de valeur inventée pour un champ frontmatter obligatoire — signaler
  le manque (`⚠️ à compléter`) plutôt que remplir.
- Jamais toucher `99_Archive` au-delà de la lecture et, plus tard, de la
  bannière de migration validée.
- Jamais éditer `Timeline Master` ou `Index` directement depuis ce skill —
  seulement identifier et lister ce qui s'y rapporte, dans le rapport.
- En Mode Fichiers/Git : ne jamais `git add`/`git commit` autre chose que le
  fichier déposé — jamais l'arbre de travail entier.
- Si un tool MCP échoue en cours de session, basculer en Mode Fichiers/Git
  UNIQUEMENT si un accès disque réel existe ; sinon, arrêter et signaler
  l'échec — jamais fabriquer un succès.
