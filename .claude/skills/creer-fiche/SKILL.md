---
name: creer-fiche
description: "Crée une nouvelle fiche d'entité canon-candidate pour le vault Lamia (Divinité, Personnage, Lieu, Événement, ou tout autre type disposant d'un template dans 00_Systeme/Templates) à partir d'une fiche existante, d'autres infos du vault, ou d'une discussion en amont — conception collaborative section par section, jamais un jet automatique. Dépose le résultat dans 05_IA_Inbox/Fiches/ (jamais dans 01_Lore). Déclenche dès que l'utilisateur veut créer, concevoir, imaginer ou mettre en fiche une nouvelle entité de l'univers — « créons une nouvelle fiche Divinité », « crée-moi une fiche pour X », « créons une fiche ensemble », « faisons le point sur quoi mettre dans cette fiche » — même sans nommer explicitement le type. Distinct de brainstorm-lore (exploration ouverte sans structure de fiche finale, dépose dans 05_IA_Inbox/Brainstorm) ; distinct de migrer-fiche (reprend une fiche EXISTANTE de 99_Archive, ne conçoit rien de neuf) ; distinct de traiter-chantier (modifie des fiches déjà existantes dans 01_Lore, ne crée jamais de fiche neuve)."
compatibility: "Mode MCP (seul mode implémenté dans cette version) : tools vault_read, vault_list, vault_write, vault_get_document_map, search_simple, search_query, tag_list, active_file_get_path, open_file — connecteur obsidian (Local REST API). Le mode Local (CLI Obsidian / Fichiers-Git, pour Claude Code) n'est pas encore couvert dans cette v1 — à ajouter dans une itération suivante une fois le mode MCP validé."
---

# Créer une fiche — Lamia

Ce skill conçoit et écrit une NOUVELLE fiche d'entité (Divinité, Personnage,
Lieu, Événement, Faction, Concept, Système, Ère, ou tout futur type doté d'un
template) pour l'univers de Lamia. Il ne se contente jamais de générer une
fiche d'un coup : il rassemble le contexte existant, construit le contenu
section par section AVEC l'utilisateur, puis écrit dans `05_IA_Inbox/Fiches/`
— jamais directement dans `01_Lore` (protocole `Regles_IA_Lore.md` : toute
initiative de contenu neuve passe par l'Inbox).

## Accès au vault — hiérarchie des modes

1. **Mode MCP (seul mode disponible dans cette version, seul possible dans
   claude.ai)** : le serveur MCP `obsidian` expose les tools cités en
   compatibility. Tout le flux ci-dessous est décrit dans ces tools.
2. **Mode Local (non implémenté)** : dans une session Claude Code avec accès
   disque réel, ce skill n'a pas encore de repli CLI/Fichiers-Git vérifié —
   le signaler à l'utilisateur plutôt que d'improviser des commandes non
   testées, et proposer de compléter cette section une fois le mode MCP
   validé à l'usage.

Dans claude.ai, un échec MCP se signale à l'utilisateur et la tâche s'arrête
— jamais improvisé, jamais présenté comme réussi.

> [!warning] `vault_write` écrase sans avertissement
> Aucune écriture sans, dans la même session, (a) vérification d'inexistence
> via `vault_list` du dossier parent, OU (b) lecture du fichier existant et
> fusion explicite de son contenu.

## Étape 0 — Contexte (une fois par session, si pas déjà fait)

Charger, si pas déjà dans le contexte de la conversation : `00_Systeme/Conventions.md`,
`00_Systeme/Index.md`, `00_Systeme/Regles_IA_Lore.md` (`vault_read`).
Conventions §2 (types), §3 (frontmatter), §4 (structure des fiches), §6
(nommage) gouvernent tout ce skill.

Si l'entité à créer est datée (personnage avec naissance/mort, événement,
ère...) : charger `01_Lore/Timeline Master.md` EN ENTIER (`vault_read` sans
`target`) avant de proposer une date — jamais de mémoire.

## Étape 1 — Déterminer le type et charger le bon template

1. `vault_list` sur `00_Systeme/Templates` — TOUJOURS relire cette liste à
   chaque session plutôt que la supposer figée : si un nouveau template y a
   été ajouté depuis la dernière fois, ce skill doit le prendre en compte
   automatiquement, sans modification de sa part.
2. Faire correspondre le type demandé par l'utilisateur (mot français,
   éventuellement au pluriel ou sans accent) à un type de Conventions §2
   (liste fermée : `divinite`, `personnage`, `peuple`, `faction`, `lieu`,
   `creature`, `magie`, `objet`, `ere`, `evenement`, `legende`, `concept`,
   `oeuvre`, `systeme`) puis au nom de fichier du template correspondant
   (ex. type `divinite` → `Divinité.md`).
3. **Si un template existe pour ce type** : `vault_read` le template en
   entier. Il contient de la syntaxe Templater (`<% tp.date.now(...) %>`,
   `<% tp.file.title %>`) — le MCP ne peut PAS l'exécuter : à l'Étape 5, ces
   placeholders sont remplacés à la main (date réelle du jour, titre réel de
   la fiche), jamais laissés tels quels dans le fichier final.
4. **Si le type est dans Conventions §2 mais SANS template** (`peuple`,
   `creature`, `magie`, `objet`, `legende`, `oeuvre` à ce jour) : le dire
   explicitement plutôt qu'improviser une structure de mémoire. Proposer le
   choix : construire depuis les champs génériques de Conventions §3 (+
   "En une phrase", "Relations", "Contradictions potentielles" — Conventions
   §4), ou attendre qu'un template soit ajouté. Ne jamais choisir à la place
   de l'utilisateur.
5. **Si le type demandé n'existe PAS dans Conventions §2** : ce n'est pas à
   ce skill de l'inventer — Conventions dit explicitement "Ajouter un
   nouveau type = modifier CE fichier d'abord". Signaler et proposer une
   discussion séparée sur les Conventions plutôt que de créer une fiche d'un
   type non reconnu.

## Étape 2 — Rassembler l'existant

Même discipline que le Mode A de `brainstorm-lore` :

1. `search_simple` (mots-clés du nom/sujet) et `search_query` (JsonLogic,
   ciblage par `type` et `statut` dans `01_Lore`) pour voir ce qui existe
   déjà.
2. **Triage par zone** (Conventions §7) : `01_Lore` = seul canon possible
   (vérifier le `statut` réel) ; `05_IA_Inbox`/`04_Brouillons` = non validé,
   à signaler mais jamais cité comme canon ; `99_Archive` = non-canon,
   jamais mobilisé.
3. **Vérification de doublon — critique ici plus que partout ailleurs** :
   si une entité de même nom (ou très proche) existe déjà quelque part dans
   le vault, arrêter et le signaler à l'utilisateur AVANT de continuer — ce
   skill crée des entités neuves, il ne doit jamais en dupliquer une déjà
   là.
4. `vault_read` en entier les fiches liées pertinentes trouvées, exploiter
   `links`/`backlinks` pour cartographier le voisinage (une fiche liée non
   trouvée par mots-clés est un angle mort classique).

## Étape 3 — Construire le contenu, section par section, jamais de yes-man

Suivre l'ordre des sections du template chargé à l'Étape 1. Pour chaque
section :

- Proposer une piste, jamais l'imposer ; donner au moins un contre-argument
  ou un risque même pour une idée qui semble bonne.
- Distinguer explicitement, dans la conversation (pas nécessairement comme
  titres dans la fiche finale, qui garde la structure du template) : **canon
  existant** mobilisé (avec la fiche source et son statut réel),
  **hypothèse** (avec le niveau de confiance), **proposition créative**
  (clairement assumée comme inventée) — c'est le FORMAT DE SORTIE exigé par
  `Regles_IA_Lore.md` pour toute proposition de lore.
- Champs `OBLIGATOIRE` selon Conventions §3 (ex. `rang` pour `divinite`,
  `importance` pour `evenement`) : ne jamais les laisser vides — les
  demander explicitement si l'utilisateur ne les a pas donnés.
- Sections psychologiques (Désir conscient → Faille intime) : facultatives
  pour une entité mineure (Conventions §4) — le signaler comme option
  plutôt que forcer leur remplissage.
- Type `evenement` : rappeler (le template le fait déjà via un callout) que
  la fiche devra être reportée dans [[Timeline Master]] lors du passage en
  canon — ce skill ne le fait jamais lui-même (hors `01_Lore`, hors de sa
  portée).
- Jamais de wikilink vers une entité non vérifiée par recherche : si une
  fiche n'existe pas, le dire plutôt que créer un lien mort silencieusement.

## Étape 4 — Nommage et vérification des collisions

1. Nom de fichier = nom réel de l'entité (Conventions §6) : espaces et
   accents autorisés, pas d'article initial (→ `aliases`), suffixe `(type)`
   uniquement en cas d'homonyme avéré avec une autre entité.
2. `vault_list` sur `05_IA_Inbox/Fiches` ET sur le sous-dossier `01_Lore`
   probable du type (ex. `01_Lore/Lieux` pour un lieu) avant d'écrire —
   jamais un chemin supposé.
3. Collision détectée : `vault_read` l'existant, proposer de compléter
   plutôt qu'écraser (fusion explicite) ou de suffixer.

## Étape 5 — Remplir le template et écrire la fiche

1. Reprendre le contenu brut du template (Étape 1), remplacer les
   placeholders Templater par les valeurs réelles (date du jour, titre).
2. Frontmatter : `statut: brouillon` (toujours — jamais `canon` ni
   `canon-verrouillé`, réservé à l'auteur), `source: ai` (convention
   actuelle du vault pour les skills réécrits — Conventions/Regles_IA_Lore
   disent encore `ia`, mais brainstorm-lore et audit-coherence ont déjà
   basculé sur `ai` ; ce skill suit la même convention), `type:` (slug
   Conventions §2), champs additionnels remplis à l'Étape 3.
3. `vault_write` vers `05_IA_Inbox/Fiches/<Nom>.md` — uniquement après
   l'Étape 4.

## Étape 6 — Base de triage et confirmation

`assets/Fiches.base` : si `05_IA_Inbox/Fiches/Fiches.base` est absent lors du
premier dépôt, le créer sans demander (copier le contenu d'`assets/Fiches.base`
via `vault_write`). Si elle existe déjà, ne jamais la réécrire — l'utilisateur
a pu la personnaliser.

Confirmer à l'utilisateur : chemin de la fiche créée, type, un récap bref de
ce qui est canon-sourcé / hypothèse / proposition créative, et rappel
explicite que rien n'est validé tant que la fiche reste en `05_IA_Inbox` —
c'est à l'utilisateur de la déplacer vers `01_Lore`, de mettre à jour la MOC
de son type, et (si `evenement`) de la reporter dans [[Timeline Master]].
Proposer d'ouvrir la fiche dans Obsidian (`open_file`) — ne l'ouvrir que si
accepté.

## Garde-fous

- Jamais de yes-man : chaque section retenue est validée explicitement par
  l'utilisateur dans l'échange.
- Jamais écrire ailleurs que `05_IA_Inbox/Fiches` — jamais dans `01_Lore`,
  jamais dans `00_Systeme`.
- Jamais poser `statut: canon` ou `canon-verrouillé`.
- Jamais `vault_delete`, `vault_move` ou `vault_patch` depuis ce skill —
  uniquement `vault_write` pour créer une fiche neuve.
- Jamais de chemin construit de mémoire — toujours résolu via
  `vault_list`/recherche avant lecture ou écriture.
- Jamais dupliquer une entité déjà existante (Étape 2, point 3) sans
  signaler le doublon potentiel en premier.
- Jamais improviser la structure d'un type sans template (Étape 1, point 4)
  — signaler l'absence, laisser l'utilisateur choisir.
- Jamais toucher aux MOC ni à Timeline Master depuis ce skill — sortie
  non-canon, hors de sa portée.
- `vault_write` écrase sans avertissement : vérification préalable
  obligatoire (voir encart après l'Accès au vault).
- Si un tool MCP échoue en cours de session alors qu'il semblait
  disponible : dans claude.ai, arrêter et signaler l'échec — jamais
  fabriquer un succès.
