---
name: detecter-liens-morts
description: "Scanne le vault Lamia (par défaut 01_Lore) à la recherche de wikilinks morts — des entités citées dans le texte mais sans fiche ni alias nulle part dans le vault — et dépose un journal `AAAA-MM-JJ — Chantier — Liens-Morts.md` dans 05_IA_Inbox/Chantiers/ listant les fiches à créer, avec le texte prêt à coller dans la section Chantiers en cours d'Index. Distingue les entités réellement absentes (candidates à creer-fiche) des liens cassés qui pointent probablement vers une fiche déjà existante sous un autre nom (ex. [[Limbes]] alors que la fiche s'appelle Les Limbes.md sans alias). Déclenche sur « cherche les liens morts », « quelles fiches il me manque », « scanne le vault pour les entités sans fiche », ou toute demande de repérer des entités mentionnées mais jamais fichées. Propose ensuite de traiter les entités une par une avec creer-fiche — jamais en masse. Ne crée ni ne modifie aucune fiche lui-même. Distinct d'audit-coherence (contradictions sur une fiche déjà là)."
compatibility: "MCP obsidian (search_query, vault_read, vault_list, vault_write) + un environnement avec accès Bash/Python (Claude Code, Cowork) pour exécuter scripts/find_dead_links.py et scripts/render_report.py — la détection à l'œil sur un vault de cette taille (des milliers d'occurrences de wikilinks) n'est pas fiable sans script. En claude.ai (pas de Bash), voir la note en fin d'Étape 2."
---

# Détecter les liens morts — Lamia

Ce skill répond à une question simple mais coûteuse à vérifier à l'œil sur un
vault de plusieurs centaines de wikilinks : *quelles entités sont citées
dans le canon mais n'ont encore aucune fiche ?* Il scanne le texte brut des
fiches (le tool MCP `vault_read` ne renvoie que les liens déjà résolus —
un lien mort n'apparaît jamais dans son champ `links`, il faut le chercher
soi-même dans le contenu), et dépose un journal dans `05_IA_Inbox/Chantiers/`
que l'utilisateur traite ensuite fiche par fiche, généralement via
`creer-fiche`.

Il ne crée et ne modifie jamais de fiche — uniquement le journal de
détection. La création reste, comme partout ailleurs dans ce vault, un geste
validé par l'utilisateur entité par entité.

## Pourquoi un script, pas une lecture à l'œil

Un vault de la taille du canon Lamia (~140 fiches dans `01_Lore` au moment de
la conception de ce skill) contient plusieurs milliers d'occurrences de
wikilinks. Une revue manuelle par Claude — même consciencieuse — en oublie
et en invente : c'est un travail de correspondance de chaînes de caractères
à grande échelle, exactement le genre de tâche où un script Python est plus
fiable qu'un LLM lisant du texte. Les deux scripts fournis
(`scripts/find_dead_links.py` et `scripts/render_report.py`) ne dépendent
que de la bibliothèque standard Python (aucune installation requise) et ne
parlent jamais au vault directement : ils travaillent sur des fichiers JSON
que Claude a lui-même récupérés via les tools MCP et déposés sur disque.
Voir la docstring de chaque script pour le détail des formats d'entrée/sortie
— ne pas deviner leur interface, la lire.

## Étape 0 — Contexte (une fois par session, si pas déjà fait)

Charger `00_Systeme/Conventions.md` et `00_Systeme/Index.md` (`vault_read`) —
notamment Conventions §6 (nommage, suffixes d'homonymie type `Kael (lieu)`)
et §8 (navigabilité, section Chantiers en cours d'Index). Le contenu
d'Index.md sert aussi de base au recoupement « déjà tracké » de l'Étape 4 —
pas besoin de le relire une seconde fois.

## Étape 1 — Cadrer le scan avec l'utilisateur

Périmètre par défaut, décidé lors de la conception de ce skill : **source =
`01_Lore` uniquement** (le canon), **résolution = tout le vault** (une fiche
qui existe dans `04_Brouillons` ou même `99_Archive` compte comme résolue :
ce n'est plus un lien mort à proprement parler, même si elle mérite peut-être
un autre chantier — migration, promotion — hors du périmètre de ce skill).

Ne pas re-proposer ce choix par défaut à chaque lancement — seulement si
l'utilisateur demande explicitement d'élargir (ex. « scanne aussi mes
brouillons ») : dans ce cas, élargir la regexp de périmètre source à
l'Étape 2 en conséquence (`^01_Lore/|^04_Brouillons/|^05_IA_Inbox/`, etc.),
et le dire clairement dans le journal produit (Étape 4).

## Étape 2 — Récupérer les données du vault (MCP → fichiers JSON)

Trois appels `search_query`, dont les résultats sont écrits sur disque —
jamais analysés « à l'œil » dans la conversation :

1. **Tous les chemins `.md` du vault** (résolution) :
   `{"regexp": ["\\.md$", {"var": "path"}]}` → écrire le tableau des
   `filename` dans un fichier JSON (`all_paths.json`).
2. **Tous les alias** (une fiche peut être résolue par un alias, pas
   seulement son nom de fichier) :
   `{"and": [{"regexp": ["\\.md$", {"var": "path"}]}, {"var": "frontmatter.aliases"}]}`
   → écrire le résultat brut (liste de `{"filename", "result": [alias,...]}`)
   dans `aliases.json`.
3. **Le contenu de chaque fiche du périmètre source**, DÉCOUPÉ PAR
   SOUS-DOSSIER de premier niveau (`vault_list` sur `01_Lore` donne la
   liste des sous-dossiers à itérer — ne pas la deviner ni la coder en dur,
   la taxonomie évolue). Une requête par sous-dossier :
   `{"and": [{"regexp": ["^01_Lore/<Sous-dossier>/", {"var": "path"}]}, {"var": "content"}]}`.

   ⚠️ **Sur ce vault, une requête `content` non découpée dépasse la limite
   de taille d'un résultat MCP** (constaté à la conception : une requête sur
   tout `01_Lore` en un seul appel échoue avec « exceeds maximum allowed
   tokens »). Le découpage par sous-dossier n'est pas une prudence
   optionnelle, c'est nécessaire. Si un sous-dossier est encore trop gros
   (ex. `Divinités/` a lui-même des sous-dossiers `Primordiales/`,
   `Majeur/`...), découper un niveau plus profond.

   Quand un appel dépasse la limite, le serveur MCP écrit le résultat complet
   dans un fichier sur le disque de la session et le signale dans le message
   d'erreur (chemin donné explicitement) — **copier ce fichier directement
   avec `Bash` (`cp`) vers le dossier de travail**, ne JAMAIS le lire d'abord
   avec `Read`/`cat` dans la conversation : le format qu'il contient est déjà
   le JSON attendu par `find_dead_links.py` (`[{"filename":..., "result":...}]`),
   recopier son contenu dans le contexte de la conversation pour le
   reformater ne fait que gaspiller des tokens pour rien.

**Si Bash est indisponible (claude.ai)** : pas de repli fiable pour ce skill
sur un vault de cette taille — le signaler à l'utilisateur plutôt que de
tenter une revue manuelle des milliers d'occurrences (risque élevé de faux
négatifs). Proposer de relancer ce skill depuis Claude Code ou Cowork.

## Étape 3 — Lancer l'analyse

```bash
python3 scripts/find_dead_links.py \
  --dump dump/<sous-dossier-1>.json dump/<sous-dossier-2>.json ... \
  --all-paths all_paths.json \
  --aliases aliases.json \
  --index-text index_text.txt \
  --out report.json
```

(`index_text.txt` = coller le contenu de la section « Chantiers en cours »
d'Index.md, déjà en contexte depuis l'Étape 0 — sert uniquement à
l'annotation « déjà tracké dans Index », jamais à la détection elle-même.)

Le script affiche un résumé sur stderr (fiches scannées, occurrences,
nombre de cibles mortes). Lire ce résumé avant d'aller plus loin : si le
nombre de « cibles mortes distinctes » semble aberrant (proche de 0 sur un
gros vault = suspect, un bug de périmètre a probablement exclu l'essentiel ;
plusieurs centaines = probablement du bruit à filtrer, relire la docstring
du script sur les faux positifs connus) plutôt que de foncer sur le
formatage.

`report.json` distingue déjà deux catégories (voir la docstring de
`build_report` dans le script pour la définition exacte) :
- `entites_absentes` : aucune fiche ni alias ne correspond nulle part dans
  le vault → candidates à `creer-fiche`.
- `quasi_doublons` : le lien est mort, mais une fiche existante a un nom
  proche (`candidats_proches`, avec un niveau de confiance) → probablement
  un alias à ajouter ou une coquille à corriger, PAS une nouvelle fiche.

Le script regroupe aussi entre elles les entités absentes qui semblent être
la même chose sous une graphie différente (`variantes_probables` —
pluriel, forme longue/courte, coquille). C'est une heuristique de forme
(comparaison de chaînes), **jamais une lecture du lore** : toujours la
vérifier à l'Étape 4, ne jamais la présenter comme tranchée.

## Étape 4 — Mettre en forme et relire AVANT de déposer

```bash
python3 scripts/render_report.py --report report.json --date <AAAA-MM-JJ> \
  --scope "01_Lore" --out chantier.md
```

Puis, avant tout dépôt dans le vault :

1. **Relire le fichier produit en entier** — le script formate fidèlement
   ce que `find_dead_links.py` a calculé, mais ne connaît rien au lore. En
   particulier :
   - Vérifier que les entrées en tête de liste (les plus fréquentes) sont
     bien des entités de lore et pas un artefact de parsing (accolades
     Templater échappées, syntaxe Dataview, fragment de code non filtré par
     le retrait des blocs de code du script). Sur ce vault à la conception,
     aucun faux positif de ce type n'a été observé après filtrage des blocs
     de code — mais la taxonomie du vault évolue, à re-vérifier à chaque
     run si le nombre de lignes explose sans raison apparente.
   - Vérifier les `variantes_probables` : sont-elles vraiment la même
     entité, ou deux choses différentes qui partagent un mot (ex. deux
     royaumes distincts contenant tous deux « Cyroldan ») ? Retirer ou
     corriger à la main si besoin — le fichier est un brouillon, l'éditer
     avant dépôt est normal.
   - Vérifier les `quasi_doublons` un par un : un rapprochement
     « approximatif (difflib) » est une piste, pas un verdict — certains se
     révéleront être deux entités sans rapport qui partagent juste des
     lettres.
2. **Si le nombre d'entités absentes est très élevé** (constaté à la
   conception : ~80 sur un premier scan d'un vault jamais audité sous cet
   angle — dette accumulée normale pour un premier passage, pas une
   anomalie), le signaler explicitement à l'utilisateur avant de proposer
   de tout traiter — même logique que `audit-coherence` sur « tout le
   vault » : un gros volume se présente, ne se déverse pas d'un coup.

## Étape 5 — Déposer le journal

Nom de fichier : `AAAA-MM-JJ — Chantier — Liens-Morts.md`, dans
`05_IA_Inbox/Chantiers/` — même convention que les journaux de
`traiter-chantier`. `vault_write` écrase sans avertissement : `vault_list`
sur `05_IA_Inbox/Chantiers/` avant d'écrire pour vérifier qu'aucun fichier du
même nom n'existe déjà (peu probable sauf second run le même jour — dans ce
cas, proposer de suffixer `— 2` ou de fusionner, jamais écraser à l'aveugle).
Relire ensuite (`vault_read`) pour confirmer la persistance réelle —
`vault_write` a déjà été observé ailleurs dans ce vault retourner un succès
sans persister.

## Étape 6 — Confirmer et proposer la suite

Présenter à l'utilisateur, sans rien écrire dans Index (`00_Systeme` reste
fermé en écriture à l'IA) :

- Le chemin du journal déposé, et un résumé chiffré (X entités absentes, Y
  quasi-doublons, Z déjà trackées dans Index).
- Les 5 à 10 entités les plus citées (celles qui ont le plus d'impact si
  elles restent non fichées) — pas la liste complète en conversation, elle
  est dans le fichier.
- Le texte à coller dans Index > Chantiers en cours (déjà généré par
  `render_report.py`, section dédiée du fichier) — rappeler qu'Index reste
  fermé en écriture à l'IA, ce texte est à coller par l'utilisateur.
- Proposer explicitement d'enchaîner sur `creer-fiche`, **une entité à la
  fois**, en commençant par celle que l'utilisateur choisit (proposer les
  plus citées en premier par défaut, jamais imposer un ordre) — jamais
  invoquer `creer-fiche` automatiquement, jamais traiter plusieurs entités
  d'affilée sans un nouvel accord explicite à chaque fois. Même logique que
  `traiter-chantier` : un chantier à la fois par défaut.
- Pour la section « fiche proche existante » : ce n'est pas du ressort de
  `creer-fiche` — proposer plutôt `traiter-chantier` si l'utilisateur valide
  qu'il s'agit bien d'un alias à ajouter sur une fiche existante.

## Garde-fous

- Jamais écrire ailleurs que `05_IA_Inbox/Chantiers/` — jamais dans
  `01_Lore`, jamais dans `Index` directement (toujours donner le texte à
  coller, jamais le coller soi-même).
- Jamais créer ni modifier de fiche depuis ce skill, même une entité
  évidente citée 60 fois — la création passe toujours par `creer-fiche`,
  validée par l'utilisateur, une fiche à la fois.
- Jamais présenter un regroupement (`variantes_probables`) ou un
  rapprochement (`quasi_doublons`) comme certain — ce sont des heuristiques
  de forme sans connaissance du lore, toujours à vérifier avant dépôt
  (Étape 4).
- Jamais traiter un lien résolu ailleurs dans le vault (`04_Brouillons`,
  `99_Archive`...) comme un lien mort — la résolution se fait sur tout le
  vault, seule la recherche des liens SORTANTS se limite au périmètre
  source. Un lien qui pointe vers une fiche non-canon n'est pas « mort », il
  pose un problème différent (zone/canon), hors du périmètre de ce skill —
  signaler si observé, ne pas le traiter comme si c'était la même chose.
- Jamais analyser à l'œil un résultat `search_query` volumineux directement
  depuis la conversation quand il a été sauvegardé sur disque par le
  serveur MCP — le copier avec `Bash`/`cp`, jamais le faire transiter par
  `Read` pour ensuite le réécrire.
- Jamais lancer un scan « tout le vault » sans le signaler et sans l'accord
  de l'utilisateur — le périmètre par défaut (`01_Lore` seul) a été choisi
  précisément pour rester exploitable en un nombre raisonnable d'appels MCP.
- Sur un volume élevé de résultats, prévenir avant de proposer un
  traitement en masse — jamais enchaîner plusieurs `creer-fiche` sans
  validation à chaque étape.
- `vault_write` écrase sans avertissement : vérifier l'absence du fichier
  cible (`vault_list`) avant d'écrire, relire après pour confirmer la
  persistance.
- Si un tool MCP échoue en cours de session alors qu'il semblait
  disponible : arrêter et signaler l'échec plutôt que de fabriquer un
  résultat partiel présenté comme complet.

---

## Journal des modifications de ce skill

- 2026-08-20 : création. Conçu et validé en conditions réelles sur le vault
  Lamia (141 fiches de `01_Lore`, 4551 occurrences de wikilinks scannées) —
  premier run : 84 entités absentes distinctes après regroupement des
  variantes, 7 liens cassés avec fiche proche existante, 6 déjà trackées
  dans Index. Découverte notable ayant orienté la conception : le champ
  `links` de `vault_read` ne contient que les liens déjà résolus (confirmé
  sur `Alketeria.md` : `[[Lumars]]` cité 7 fois dans le texte, 0 fois dans
  `links`) — d'où la nécessité de parser le contenu brut plutôt que de
  s'appuyer sur les métadonnées MCP. Le cutoff de similarité approximative
  (`difflib`) a été resserré de 0.72 à 0.78 (0.85 sur les chaînes courtes)
  après avoir observé un faux rapprochement (« Lamia » ~ « Lumina » à 0.73)
  lors du premier run — un rapprochement fort dédié au suffixe d'homonymie
  entre parenthèses (Conventions §6, ex. `Lamia (planète)`) a été ajouté en
  complément, qui a d'ailleurs révélé un cas réel d'homonymie non
  désambiguïsée (`[[Lamia]]` seul pourrait viser `Lamia (planète)` ou
  `Lamia (ange)`).
