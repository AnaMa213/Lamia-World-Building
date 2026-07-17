---
name: brainstorm-lore
description: Lance ou formalise une session de brainstorming sur un sujet de lore de l'univers Lamia, capture une idée volée sans structuration, ou enregistre le résultat dans une Fiche Brainstorm sous 05_IA_Inbox/Brainstorm/. Utilise ce skill dès que l'utilisateur veut réfléchir, explorer, challenger, creuser ou résoudre une question de lore (mécanique, contradiction, nouvelle entité, doctrine, hypothèse...) — même s'il ne dit pas explicitement "brainstorm" (ex. "on réfléchit à X", "j'ai une idée pour Y", "comment résoudre cette incohérence sur Z", "et si..."). Utilise-le aussi quand l'utilisateur demande de formaliser une discussion déjà tenue, OU quand il veut juste noter une idée vite fait sans en discuter maintenant ("note ça vite fait", "capture cette idée", "je creuserai plus tard", "garde ça quelque part") — dans ce dernier cas, capture minimale sans recherche ni structuration, voir Mode C.
compatibility: Fonctionne avec le MCP obsidian-mcp-server connecté au vault Lamia (obsidian_search_notes, obsidian_get_note, obsidian_list_notes, obsidian_write_note). En Claude Code, si ce MCP est absent, bascule sur un accès disque direct (Read/Write/Glob/Grep/Bash) et git — voir "Deux modes d'accès au vault".
---

# Brainstorm Lore — Lamia

Ce skill gère une session de brainstorming de lore de bout en bout : cadrage,
exploration challengée, puis mise en fiche dans l'inbox IA. Il a deux modes,
et NE tranche jamais lui-même une décision de canon (voir Garde-fous).

## Deux modes d'accès au vault

Ce skill dépend normalement du MCP `obsidian-mcp-server`. Deux cas de figure :

- **Mode MCP (par défaut)** : les tools `obsidian_get_note`,
  `obsidian_search_notes`, `obsidian_write_note`, `obsidian_list_notes` sont
  disponibles → comportement décrit plus bas, inchangé.
- **Mode Fichiers/Git (Claude Code uniquement)** : si ces tools sont absents,
  ou si l'un d'eux échoue en cours de session (connexion MCP tombée), ET que
  Claude a un accès disque direct au vault (cas Claude Code — le vault est
  généralement la racine du repo git courant). Chaque étape MCP ci-dessous a
  son équivalent Fichiers, indiqué par « **Si MCP indisponible :** ».

⚠️ Ce mode de repli n'existe QUE là où un accès disque réel au vault est
possible. Dans claude.ai (sandbox isolée, sans accès au vault réel), un échec
MCP doit être signalé à l'utilisateur et la tâche interrompue — jamais
improvisé, jamais présenté comme réussi.

## Étape 0 — Contexte (une fois par session, si pas déjà fait)

Avant toute chose : `00_Systeme/Conventions.md` et `00_Systeme/Index.md`
doivent être chargés (statuts, types, notation §5, nommage §6). S'ils ne
sont pas déjà dans le contexte de la conversation en cours, les lire d'abord
via `obsidian_get_note`.
**Si MCP indisponible :** lire ces mêmes fichiers avec `Read` (chemins relatifs
à la racine du vault — par défaut la racine du repo Claude Code ; vérifier
avec `ls` si le vault est ailleurs).

Si le sujet touche à une chronologie ou date des événements : charger
`01_Lore/Timeline Master.md` EN ENTIER avant de discuter de dates. Ne jamais
reconstruire une chronologie de mémoire.
**Si MCP indisponible :** `Read` ce même fichier en entier — ne jamais résumer
une chronologie de mémoire, même en mode Fichiers.

## Choisir le mode

**Mode A — Piloter la session** : déclenché par une demande de lancer /
commencer un brainstorm ("lance un brainstorm sur...", "brainstormons sur...",
"j'ai une question sur X, réfléchissons"), ou quand aucune discussion
substantielle sur ce sujet précis n'existe encore dans la conversation.

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

1. **Cadrer et rechercher le canon existant.** Avant de proposer quoi que ce
   soit, chercher ce qui existe déjà sur le sujet :
   `obsidian_search_notes` (mode text, `pathPrefix: "01_Lore"`, mots-clés du
   sujet, `maxMatchesPerHit: 3-5`), puis `obsidian_get_note` (format content)
   sur les quelques fiches les plus pertinentes pour les lire réellement.
   **Si MCP indisponible :** `Grep` (mots-clés du sujet, dossier `01_Lore/`)
   et `Glob` (`01_Lore/**/*<terme>*.md`) pour repérer les fiches candidates,
   puis `Read` directement les plus pertinentes.
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
   qui décide (cf. hypothesis-to-doctrine : l'auteur tranche). Quand une piste
   est retenue, noter aussi son statut visé (hypothèse · doctrine de travail ·
   à canoniser) : ce n'est jamais canon à ce stade.

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
   "formatage" que ce mode évite). En cas de collision (même minute),
   ajouter une lettre (`...HHhMM-b.md`).
3. Frontmatter minimal : `statut: brouillon`, `source: ia`,
   `tags: [capture-rapide]`, `date: AAAA-MM-JJ`. Rien de plus — pas de
   `sujet:`, pas d'`entites_liees:` (ce ne sont pas des champs pertinents
   pour ce type de note).
4. Écrire directement dans `04_Brouillons/` via `obsidian_write_note`
   (`overwrite: false`).
   **Si MCP indisponible :** `Write` au même chemin. Puis, seulement si le
   vault est un dépôt git : `git add "04_Brouillons/<fichier>.md"` et
   `git commit -m "[brouillon IA] Capture rapide" -- "04_Brouillons/<fichier>.md"`
   — jamais `git add -A`/`-A`/`-a`, uniquement ce fichier.
5. Confirmer en une ligne, sans reformuler le contenu ni proposer d'aller
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
   - pas d'article initial (cf. Conventions §6 — l'article ne fait pas partie
     du nom).

2. **Construire le nom de fichier** :
   `AAAA-MM-JJ — Brainstorm — Sujet.md` (date du jour de la session).

3. **Vérifier les collisions** : `obsidian_list_notes` sur
   `05_IA_Inbox/Brainstorm` (créer ce chemin implicitement s'il n'existe pas
   encore, en écrivant simplement dedans). Si un fichier du même nom existe
   déjà (même sujet, même jour), proposer à l'utilisateur de compléter la
   session existante plutôt que d'écraser.
   **Si MCP indisponible :** `Bash` (`mkdir -p "05_IA_Inbox/Brainstorm"`) puis
   `Glob`/`ls` sur ce dossier pour la même vérification de collision.

4. **Remplir le gabarit** `assets/template.md` (placeholders `{{...}}`) :
   - `{{SUJET_COMPLET}}` : la question/le sujet en une phrase
   - `{{ENTITES_LIEES}}` : liste YAML des fiches réellement trouvées à
     l'étape de recherche, en wikilinks (`  - "[[Nom de la fiche]]"`) —
     jamais une entité qui n'a pas été vérifiée comme existante
   - `{{DATE}}` : date du jour, format `AAAA-MM-JJ`
   - `{{TITRE_FICHIER}}` : nom du fichier sans l'extension `.md`
   - `{{RESUME_UNE_PHRASE}}`, `{{QUESTION_OBJECTIF}}`, `{{CANON_EXISTANT}}`,
     `{{PISTES_EXPLOREES}}`, `{{RETENU}}`, `{{ECARTE}}`,
     `{{QUESTIONS_OUVERTES}}`, `{{A_REPORTER}}` : contenu de la session,
     un item par ligne en liste à puces (voir Mode A/B).
   - `{{A_REPORTER}}` : une checklist actionnable, une ligne par décision
     retenue, ex. `- [ ] [[Fiche cible]] ← [décision]`.

5. **Écrire le fichier** via `obsidian_write_note` (target: path
   `05_IA_Inbox/Brainstorm/<nom du fichier>.md`, `overwrite: false`). Ne
   jamais ajouter le double-marqueur `revision: ia-a-valider` ici : ce
   protocole concerne la modification de fichiers existants, pas la création
   dans 05_IA_Inbox (déjà `statut: brouillon` + `source: ia`).

   **Si MCP indisponible :** créer le fichier avec `Write`, même chemin, même
   contenu assemblé. Puis, seulement si le vault est dans un dépôt git
   (vérifier d'abord avec `git rev-parse --is-inside-work-tree`) :
   ```bash
   git add "05_IA_Inbox/Brainstorm/<nom du fichier>.md"
   git commit -m "[brouillon IA] Brainstorm — <Sujet-en-un-mot>" -- "05_IA_Inbox/Brainstorm/<nom du fichier>.md"
   ```
   Le message de commit reprend le sujet-en-un-mot dérivé à l'étape 1, préfixé
   par `[brouillon IA]` pour que l'historique git reflète honnêtement le
   statut (pas une validation de l'utilisateur). Ne JAMAIS utiliser
   `git add -A`, `git add .` ou `git commit -a` : stager et commiter
   uniquement ce fichier précis, jamais le reste de l'arbre de travail (qui
   peut contenir des changements de l'utilisateur sans rapport). Si le vault
   n'est pas un dépôt git, ignorer l'étape git et le mentionner simplement
   dans la confirmation.

6. **Confirmer à l'utilisateur** : chemin du fichier créé (+ mention du commit
   git s'il a eu lieu, avec son message), recap bref (Retenu / Écarté /
   questions ouvertes / À reporter), et rappel que rien n'engage le canon
   tant que le contenu n'est pas reporté dans 01_Lore par l'utilisateur.

---

## Garde-fous (rappel)

- Jamais de yes-man : chaque piste "Retenu" a été challengée, et validée
  explicitement par l'utilisateur — pas par défaut, pas par enthousiasme.
- Jamais de wikilink vers une entité non vérifiée par recherche : si une
  fiche n'existe pas, le dire ("absent des notes du vault") plutôt que de
  créer un lien mort silencieusement.
- Jamais promouvoir un statut à `canon` ou `canon-verrouillé` depuis ce
  skill — la fiche reste `brouillon`/`source: ia` par nature.
- Si la session couvre plusieurs sujets réellement distincts (pas juste des
  sous-aspects d'une même question), le signaler et proposer de scinder en
  plusieurs fiches plutôt que de tout mettre dans une seule.
- Le contenu de la fiche brainstorm n'est jamais cité comme canon ailleurs
  dans la conversation tant qu'il n'a pas été reporté dans 01_Lore.
- Si un tool MCP échoue en cours de session alors qu'il semblait disponible
  (connexion tombée), basculer en Mode Fichiers/Git UNIQUEMENT si un accès
  disque réel au vault existe (Claude Code) ; sinon, arrêter et signaler
  l'échec à l'utilisateur — jamais fabriquer un succès ou improviser une
  autre source.
- En Mode Fichiers/Git : ne jamais `git add`/`git commit` autre chose que le
  fichier de la fiche créée — jamais l'arbre de travail entier, même si
  d'autres changements semblent liés.
- En Mode C : ne jamais appliquer le gabarit ou la structure du Mode A/B à
  une capture express — si Claude se surprend à chercher le canon existant
  ou à structurer l'idée en sections, c'est le signal que ce n'est plus une
  capture express mais une session Mode A, à proposer explicitement plutôt
  qu'à faire glisser silencieusement.
