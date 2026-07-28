---
name: brainstorm-lore
description: Lance ou formalise une session de brainstorming sur un sujet de lore de l'univers Lamia, capture une idée volée sans structuration, ou enregistre le résultat dans une Fiche Brainstorm sous 05_IA_Inbox/Brainstorm/. Utilise ce skill dès que l'utilisateur veut réfléchir, explorer, challenger, creuser ou résoudre une question de lore (mécanique, contradiction, nouvelle entité, doctrine, hypothèse...) — même s'il ne dit pas explicitement "brainstorm" (ex. "on réfléchit à X", "j'ai une idée pour Y", "comment résoudre cette incohérence sur Z", "et si...", "réfléchissons sur la fiche ouverte/active"). Utilise-le aussi quand l'utilisateur demande de formaliser une discussion déjà tenue, OU quand il veut juste noter une idée vite fait sans en discuter maintenant ("note ça vite fait", "capture cette idée", "je creuserai plus tard", "garde ça quelque part") — dans ce dernier cas, capture minimale sans recherche ni structuration, voir Mode C.
compatibility: Fonctionne avec le MCP Obsidian (Local REST API) connecté au vault Lamia — tools vault_read, vault_list, vault_write, vault_append, vault_get_document_map, search_simple, search_query, active_file_get_path, open_file. En Claude Code, si le MCP est absent, replis en cascade (CLI Obsidian puis Fichiers/Git) — voir references/modes-repli.md.
---

# Brainstorm Lore — Lamia

Ce skill gère une session de brainstorming de lore de bout en bout : cadrage,
exploration challengée, puis mise en fiche dans l'inbox IA. Il a trois modes,
et NE tranche jamais lui-même une décision de canon (voir Garde-fous).

## Accès au vault — hiérarchie des modes

1. **Mode MCP (par défaut, seul possible dans claude.ai)** : le serveur MCP
   `obsidian` expose les tools cités ci-dessous. Tout le flux de ce fichier
   est décrit dans ces tools.
2. **Mode CLI Obsidian (Claude Code, application Obsidian ouverte)** : repli
   si le MCP est absent ou tombe en cours de session.
3. **Mode Fichiers/Git (Claude Code, application fermée)** : dernier repli,
   accès disque direct au vault.

Pour les modes 2 et 3, lire `references/modes-repli.md` AU MOMENT de basculer
(équivalences tool par tool, règles git). Dans claude.ai (sandbox sans accès
au vault réel), un échec MCP se signale à l'utilisateur et la tâche s'arrête
— jamais improvisé, jamais présenté comme réussi.

> [!warning] `vault_write` écrase sans avertissement
> Le tool n'a aucun paramètre de protection : écrire sur un chemin existant
> remplace silencieusement le fichier. Règle absolue : ne jamais appeler
> `vault_write` sur un chemin sans avoir, dans la même session, (a) vérifié
> son inexistence via `vault_list` du dossier parent, OU (b) lu le fichier
> via `vault_read` et intégré son contenu dans ce qu'on écrit (fusion
> explicite). Cette vérification n'est pas une politesse : c'est l'unique
> filet anti-perte de données.

## Étape 0 — Contexte (une fois par session, si pas déjà fait)

Avant toute chose : `00_Systeme/Conventions.md` et `00_Systeme/Index.md`
doivent être chargés (statuts §1, types §2, notation §5, nommage §6,
arborescence §7). S'ils ne sont pas déjà dans le contexte de la conversation,
les lire via `vault_read`. Si les Règles IA du projet ne sont pas non plus
dans le contexte (cas d'une session Claude Code hors projet), lire aussi
`00_Systeme/Regles_IA_Lore.md`.

Si le sujet touche à une chronologie ou date des événements : charger
`01_Lore/Timeline Master.md` EN ENTIER (`vault_read` sans `target` — jamais
de lecture partielle pour ce fichier) avant de discuter de dates. Ne jamais
reconstruire une chronologie de mémoire. Utiliser la notation de Conventions
§5 (≈ · ? · (rumeur) · 🔒 · ⚠️) à l'identique quand des dates sont discutées.

## Choisir le mode

**Mode A — Piloter la session** : déclenché par une demande de lancer /
commencer un brainstorm ("lance un brainstorm sur...", "brainstormons sur...",
"j'ai une question sur X, réfléchissons"), ou quand aucune discussion
substantielle sur ce sujet précis n'existe encore dans la conversation.
Si l'utilisateur désigne "la fiche ouverte / active / que je regarde" comme
sujet : résoudre le chemin via `active_file_get_path`, puis `vault_read`
cette fiche avant de cadrer.

**Mode B — Formaliser seulement** : déclenché par une demande de consigner /
enregistrer / formaliser une réflexion déjà tenue ("formalise cette
discussion", "crée la fiche brainstorm de ce qu'on vient de dire", "consigne
ça"), quand la conversation en cours contient déjà l'essentiel du contenu.

**Mode C — Capture express** : déclenché quand l'utilisateur signale
explicitement qu'il ne veut PAS en discuter maintenant — "note ça vite fait",
"capture cette idée", "je creuserai plus tard", "garde ça quelque part". Le
signal distinctif vs Mode A/B : l'utilisateur exprime qu'il veut minimiser la
friction tout de suite, pas explorer ni structurer. Si le moindre doute
existe entre Mode C et Mode A (l'utilisateur semble vouloir en discuter un
minimum), pencher vers Mode A — Mode C est réservé aux cas sans ambiguïté.

Si le mode n'est pas clair entre A et B (ex. la conversation contient un peu
de matière mais l'utilisateur dit juste "brainstorm sur X"), poser UNE
question de clarification plutôt que deviner : "Tu veux que je lance une
nouvelle session dessus, ou que je formalise ce qu'on vient de dire ?"

---

## Mode A — Piloter la session

1. **Cadrer et rechercher l'existant.** Avant de proposer quoi que ce soit,
   chercher ce qui existe déjà sur le sujet. Deux tools complémentaires :

   - `search_simple` (mots-clés du sujet) : recherche large, scorée, avec
     contexte autour de chaque correspondance. Elle couvre TOUT le vault —
     le triage par zone est donc obligatoire (voir ci-dessous).
   - `search_query` (JsonLogic) : ciblage précis quand on sait ce qu'on
     cherche. Exemples utiles :
     - contenu dans le canon seulement :
       `{"and": [{"regexp": ["^01_Lore/", {"var": "path"}]}, {"regexp": ["(?i)drakéide", {"var": "content"}]}]}`
     - restreint aux statuts qui font foi :
       ajouter `{"in": [{"var": "frontmatter.statut"}, ["canon-verrouillé", "canon", "semi-canon"]]}`
     - sessions de brainstorm antérieures sur le même sujet :
       `{"and": [{"regexp": ["^05_IA_Inbox/Brainstorm/", {"var": "path"}]}, {"regexp": ["(?i)drakéide", {"var": "content"}]}]}`

   **Triage par zone** de tout résultat de recherche, d'après Conventions §7 :
   - `01_Lore/` : seuls candidats au canon. Lire la fiche et VÉRIFIER son
     `frontmatter.statut` — une `rumeur` décrit ce que les habitants croient,
     un `secret` (🔒) ne fuite jamais vers du contenu lecteur/joueur, un
     `obsolète` ne fait plus foi. Toujours rapporter le statut réel, jamais
     le supposer.
   - `05_IA_Inbox/` : propositions IA non validées, dont d'éventuels
     brainstorms antérieurs sur ce sujet — les signaler à l'utilisateur
     (reprendre ? contradictoire ?), jamais les citer comme canon.
   - `04_Brouillons/` : idées de l'auteur non triées — même règle.
   - `02_Romans/`, `03_Scenarios_JDR/` : portée œuvre (`portee:`), ne
     modifie pas le canon-univers.
   - `99_Archive/` : ancien vault NON-CANON, lecture seule. Ne jamais citer
     comme canon, même si le contenu semble pertinent.

   Puis `vault_read` les quelques fiches les plus pertinentes pour les lire
   réellement. La réponse inclut `links` et `backlinks` : les exploiter pour
   cartographier le voisinage du sujet (une fiche liée non trouvée par la
   recherche par mots-clés est un angle mort classique). Pour une fiche
   longue et périphérique, `vault_get_document_map` d'abord, puis lecture
   ciblée (`target`/`targetType`) ; pour une fiche centrale au sujet, lecture
   entière — une lecture partielle rate les contradictions.
   Ne jamais inventer un élément qui existe déjà — et ne jamais présenter une
   fiche non lue comme connue.

2. **Mener le brainstorm en plusieurs tours, pas en un seul message.**
   Poser des questions, proposer plusieurs pistes concurrentes plutôt
   qu'une seule idée à valider. Pour CHAQUE piste avant de la considérer :
   - la tester contre l'exploitabilité (une entité rivale du monde
     pourrait-elle en détourner la logique ?) ;
   - la confronter aux contradictions déjà connues du sujet ;
   - donner au moins un contre-argument ou un trade-off, même pour une idée
     qu'on préfère.
   Jamais de yes-man : une piste qui semble bonne à Claude n'est pas pour
   autant "retenue" — voir point 4.

3. **Suivre au fil de l'eau**, mentalement ou en brouillon de réponse :
   - Pistes explorées (toutes, y compris les fausses pistes)
   - Écarté + motif du rejet (dès qu'une piste est abandonnée)
   - Questions ouvertes (ce qui reste non tranché)

4. **"Retenu" = validé explicitement par l'utilisateur dans l'échange.**
   Claude ne fait jamais passer seul une idée en "Retenu" — c'est l'utilisateur
   qui décide (Conventions §1 : seul l'auteur attribue les statuts qui font
   foi). Quand une piste est retenue, noter aussi son statut visé (hypothèse ·
   doctrine de travail · à canoniser) : ce n'est jamais canon à ce stade.

5. Quand l'utilisateur signale que la session est terminée ("on s'arrête là",
   "formalise", "crée la fiche"), passer à **Assembler et enregistrer**.

## Mode B — Formaliser une discussion déjà tenue

1. Relire les tours pertinents de la conversation en cours pour en extraire :
   sujet, canon déjà mobilisé, pistes, retenu, écarté, questions ouvertes.
2. Si le tri retenu/écarté n'est pas évident à partir de la discussion,
   demander confirmation avant d'écrire — ne jamais trancher ce classement
   à la place de l'utilisateur.
3. Passer à **Assembler et enregistrer**.

## Mode C — Capture express

Comportement fondé sur Conventions §9 (« Flux de capture ») : pendant une
session, une idée = une note dans `04_Brouillons`, juste `statut: brouillon`
et une ligne de contenu. **JAMAIS de formatage complet à la capture** — pas
de recherche de canon, pas de pistes concurrentes, pas de section "En une
phrase", pas de gabarit. Le tri et la structuration se font plus tard, dans
une vraie session Mode A ou B. `04_Brouillons` est aussi la seule zone du
vault exemptée de la règle §8 (pas besoin de wikilink ni d'ajout à une MOC).

Étapes (ne PAS utiliser "Assembler et enregistrer" — ce chemin est plus
court, volontairement) :

1. Prendre l'idée telle qu'exprimée par l'utilisateur, nettoyée a minima
   (orthographe/grammaire) mais jamais reformulée, étoffée ou structurée.
2. Construire le nom de fichier : `AAAA-MM-JJ HHhMM.md` (date et heure de la
   capture — pas de sujet-en-un-mot, cette dérivation appartient déjà au
   "formatage" que ce mode évite).
3. `vault_list` sur `04_Brouillons` AVANT d'écrire (vault_write écrase
   silencieusement) : en cas de collision à la même minute, suffixer une
   lettre (`...HHhMM-b.md`).
4. Frontmatter minimal : `statut: brouillon`, `source: ai`,
   `tags:` (liste avec `capture-rapide`), `date: AAAA-MM-JJ`. Rien de plus —
   pas de `sujet:`, pas d'`entites_liees:` (pas pertinents pour ce type de
   note).
5. Écrire dans `04_Brouillons/` via `vault_write`.
6. Confirmer en une ligne, sans reformuler le contenu ni proposer d'aller
   plus loin maintenant (l'utilisateur a explicitement signalé qu'il ne
   voulait pas en discuter tout de suite) : chemin du fichier, point final.

---

## Assembler et enregistrer

1. **Dériver le sujet-en-un-mot** (pour le nom de fichier uniquement — le
   frontmatter `sujet:` garde la phrase complète) :
   - le terme le plus spécifique et identifiant du sujet (entité ou concept
     central de la session) ;
   - si un seul mot est ambigu, concaténer en PascalCase sans espace
     (ex. `OrigineDrakéides`) ;
   - accents conservés, aucune ponctuation ;
   - pas d'article initial (Conventions §6 — l'article ne fait pas partie
     du nom).

2. **Construire le nom de fichier** :
   `AAAA-MM-JJ — Brainstorm — Sujet.md` (date du jour de la session).

3. **Vérifier les collisions et la Base de triage** : `vault_list` sur
   `05_IA_Inbox/Brainstorm` (inutile de créer le dossier : `vault_write` crée
   les dossiers parents manquants). Si un fichier du même nom existe déjà
   (même sujet, même jour) : `vault_read` la fiche existante, puis proposer
   à l'utilisateur de la compléter — la fusion se fait en intégrant le
   contenu lu section par section dans un nouveau contenu complet, réécrit
   via `vault_write` (le filet : on a lu avant d'écraser, et rien de
   l'existant n'est perdu). Pour n'ajouter des éléments qu'à une seule
   section, `vault_append` ou `vault_patch` (ciblage par heading) sont des
   alternatives plus chirurgicales. Ne jamais écraser à l'aveugle.
   Dans ce même listing, si `Brainstorms.base` est absent : le créer sans
   demander (copier le contenu d'`assets/Brainstorms.base` vers
   `05_IA_Inbox/Brainstorm/Brainstorms.base` via `vault_write`) — c'est la
   vue installée d'office pour cette inbox (voir « Vue de triage » plus
   bas). Si elle existe déjà, ne jamais la réécrire : l'utilisateur a pu la
   personnaliser.

4. **Remplir le gabarit** `assets/template.md` (placeholders `{{...}}`) :
   - `{{SUJET_COMPLET}}` : la question/le sujet en une phrase
   - `{{ENTITES_LIEES}}` : liste YAML des fiches réellement trouvées à
     l'étape de recherche, en wikilinks entre guillemets
     (`  - "[[Nom de la fiche]]"` — les guillemets sont obligatoires pour
     un lien en frontmatter) — jamais une entité qui n'a pas été vérifiée
     comme existante
   - `{{DATE}}` : date du jour, format `AAAA-MM-JJ`
   - `{{TITRE_FICHIER}}` : nom du fichier sans l'extension `.md`
   - `{{RESUME_UNE_PHRASE}}`, `{{QUESTION_OBJECTIF}}`, `{{CANON_EXISTANT}}`,
     `{{PISTES_EXPLOREES}}`, `{{RETENU}}`, `{{ECARTE}}`,
     `{{QUESTIONS_OUVERTES}}`, `{{A_REPORTER}}` : contenu de la session,
     un item par ligne en liste à puces (voir Mode A/B).
   - Dans `{{CANON_EXISTANT}}`, chaque fiche mobilisée porte son statut réel
     lu en frontmatter, ex. `- [[Voile des Éthers]] (statut: semi-canon) —
     élément mobilisé`. Le statut conditionne le poids de l'argument.
   - `{{A_REPORTER}}` : une checklist actionnable, une ligne par décision
     retenue, ex. `- [ ] [[Fiche cible]] ← [décision]`.

5. **Écrire le fichier** via `vault_write` (path
   `05_IA_Inbox/Brainstorm/<nom du fichier>.md`) — uniquement après la
   vérification de l'étape 3. Ne jamais ajouter le double-marqueur
   `revision: ia-a-valider` ici : ce protocole concerne la modification de
   fichiers existants, pas la création dans 05_IA_Inbox (déjà
   `statut: brouillon` + `source: ai`).

6. **Confirmer à l'utilisateur** : chemin du fichier créé, recap bref
   (Retenu / Écarté / questions ouvertes / À reporter), et rappel que rien
   n'engage le canon tant que le contenu n'est pas reporté dans 01_Lore par
   l'utilisateur. Proposer d'ouvrir la fiche dans Obsidian (`open_file`) —
   ne l'ouvrir que si l'utilisateur accepte : il n'est pas forcément devant
   la machine où tourne le vault.

---

## Vue de triage des brainstorms (installée d'office)

`assets/Brainstorms.base` est copiée automatiquement vers
`05_IA_Inbox/Brainstorm/Brainstorms.base` dès la première fiche écrite dans
ce dossier (Assembler et enregistrer, étape 3) — aucune demande explicite
requise. Elle sert de MOC de facto pour l'inbox brainstorm et comble
l'angle mort Conventions §8-(2) (une fiche de 05_IA_Inbox n'est listée dans
aucune MOC) : les colonnes Fiche / Sujet / Session / Statut se trient en
cliquant sur leur en-tête dans Obsidian. Elle coexiste avec Dataview
(Tableau de bord) sans le remplacer — deux systèmes de vues, chacun sur son
périmètre. Une fois installée, ne plus jamais la réécrire automatiquement :
si l'utilisateur l'a modifiée (nouvelles colonnes, filtres), une réécriture
silencieuse l'effacerait.

---

## Garde-fous (rappel)

- Jamais de yes-man : chaque piste "Retenu" a été challengée, et validée
  explicitement par l'utilisateur — pas par défaut, pas par enthousiasme.
- Jamais de wikilink vers une entité non vérifiée par recherche : si une
  fiche n'existe pas, le dire ("absent des notes du vault") plutôt que de
  créer un lien mort silencieusement.
- Jamais promouvoir un statut à `canon` ou `canon-verrouillé` depuis ce
  skill — la fiche reste `brouillon`/`source: ai` par nature (Conventions
  §1 : seul l'auteur attribue ces statuts).
- Jamais d'écriture dans `00_Systeme` (verrouillé) ni dans `99_Archive`
  (lecture seule), et jamais de `vault_delete` ni de `vault_move` depuis ce
  skill : il crée des fiches, il ne supprime ni ne déplace rien.
- `vault_write` écrase sans avertissement : aucune écriture sans
  vérification préalable d'inexistence (`vault_list`) ou sans
  lecture-et-fusion explicite du fichier existant.
- Tout résultat de recherche est trié par zone (voir Mode A, étape 1) : une
  correspondance dans `99_Archive`, `04_Brouillons` ou `05_IA_Inbox` n'est
  jamais du canon, quel que soit son contenu.
- Le statut d'une fiche mobilisée est celui lu dans son frontmatter, jamais
  un statut supposé — et il est rapporté explicitement dans la fiche
  brainstorm.
- Si la session couvre plusieurs sujets réellement distincts (pas juste des
  sous-aspects d'une même question), le signaler et proposer de scinder en
  plusieurs fiches plutôt que de tout mettre dans une seule.
- Le contenu de la fiche brainstorm n'est jamais cité comme canon ailleurs
  dans la conversation tant qu'il n'a pas été reporté dans 01_Lore.
- Si un tool MCP échoue en cours de session alors qu'il semblait disponible
  (connexion tombée) : basculer sur un repli UNIQUEMENT en Claude Code avec
  accès réel au vault (lire alors `references/modes-repli.md`) ; dans
  claude.ai, arrêter et signaler l'échec — jamais fabriquer un succès ou
  improviser une autre source.
- En Mode C : ne jamais appliquer le gabarit ou la structure du Mode A/B à
  une capture express — si Claude se surprend à chercher le canon existant
  ou à structurer l'idée en sections, c'est le signal que ce n'est plus une
  capture express mais une session Mode A, à proposer explicitement plutôt
  qu'à faire glisser silencieusement.
