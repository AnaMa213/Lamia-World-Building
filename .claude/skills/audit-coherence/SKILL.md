---
name: audit-coherence
description: Audite la cohérence d'une fiche, d'un dossier/type ou d'une zone du vault Lamia — contradictions avec le canon, doublons, conflits de timeline, zones floues — et dépose un journal d'audit dans 05_IA_Inbox/Audits/. Utilise ce skill UNIQUEMENT sur demande explicite ("audite X", "vérifie la cohérence de Y", "est-ce que X contredit autre chose dans le vault", "check les doublons sur Z", "y a-t-il des zones floues dans W") — jamais de façon proactive après un simple ajout ou une simple modification. Ne pas confondre avec migrer-fiche (qui fait sa propre mini-vérification, mais uniquement pour une fiche en cours de migration depuis 99_Archive) ni avec brainstorm-lore (exploration créative, pas audit de l'existant).
compatibility: Fonctionne avec le MCP Obsidian (Local REST API) connecté au vault Lamia — tools vault_read, vault_list, vault_get_document_map, search_simple, search_query, tag_list, vault_write, open_file. En Claude Code, si le MCP est absent, replis en cascade (CLI Obsidian puis Fichiers/Git) — voir references/modes-repli.md.
---

# Auditer la cohérence — Lamia

Ce skill audite une cible (fiche, dossier, type d'entité) contre le reste du
vault selon 4 axes : contradictions, doublons, conflits de timeline, zones
floues. Il **ne modifie jamais la ou les fiches auditées** — lecture seule
sur les cibles ; ses seules écritures sont un nouveau fichier journal dans
`05_IA_Inbox/Audits/` et, à la première utilisation, la Base de triage
`Audits.base` (voir plus bas). Il ne tranche jamais une incohérence
lui-même : il la signale, l'utilisateur arbitre.

## Accès au vault — hiérarchie des modes

1. **Mode MCP (par défaut, seul possible dans claude.ai)** : le serveur MCP
   `obsidian` expose les tools cités en compatibility. Tout le flux de ce
   fichier est décrit dans ces tools.
2. **Mode CLI Obsidian (Claude Code, application Obsidian ouverte)** : repli
   si le MCP est absent ou tombe en cours de session.
3. **Mode Fichiers/Git (Claude Code, application fermée)** : dernier repli,
   accès disque direct au vault.

Pour les modes 2 et 3, lire `references/modes-repli.md` AU MOMENT de basculer
(équivalences opération par opération, règles git). Dans claude.ai (sandbox
sans accès au vault réel), un échec MCP se signale à l'utilisateur et la
tâche s'arrête — jamais improvisé, jamais présenté comme réussi.

> [!warning] `vault_write` écrase sans avertissement
> Le tool n'a aucun paramètre de protection : écrire sur un chemin existant
> remplace silencieusement le fichier. Règle absolue : ne jamais appeler
> `vault_write` sur un chemin sans avoir, dans la même session, (a) vérifié
> son inexistence via `vault_list` du dossier parent, OU (b) lu le fichier
> via `vault_read` et intégré son contenu dans ce qu'on écrit (fusion
> explicite).

## Syntaxe Obsidian — sources d'autorité

Le journal déposé est de l'Obsidian Flavored Markdown valide. Les skills
officiels installés font foi — ne pas improviser de mémoire :
`/mnt/skills/user/obsidian-markdown/SKILL.md` (wikilinks, callouts,
propriétés) et `/mnt/skills/user/obsidian-bases/SKILL.md` (à lire AVANT de
toucher un `.base`). Rappels : wikilinks pour tout lien interne ; une
propriété de type lien s'écrit entre guillemets (`cible: "[[Fiche]]"`) ;
dates frontmatter au format `AAAA-MM-JJ` pour être reconnues comme type Date.

## Étape 0 — Contexte (une fois par session, si pas déjà fait)

Charger `00_Systeme/Conventions.md` et `00_Systeme/Index.md` s'ils ne sont
pas déjà dans le contexte (`vault_read`), plus `00_Systeme/Regles_IA_Lore.md`
si les Règles IA du projet n'y sont pas non plus (cas d'une session Claude
Code hors projet). La notation §5 (`⚠️` incohérence en attente d'arbitrage,
`≈` approximatif, `?` inconnu ordonné, `(rumeur)`, `🔒` secret) est le
vocabulaire de sortie de ce skill — l'utiliser tel quel dans le rapport et
le journal.

## Étape 1 — Déterminer le périmètre

Le périmètre est configurable selon la demande :

- **Une fiche** : l'utilisateur nomme une fiche précise.
- **Un dossier/type** : "toutes les divinités", "le dossier Événements/Ère
  Sérénale" — auditer chaque fiche du sous-ensemble, individuellement ET les
  unes contre les autres (doublons potentiels DANS le sous-ensemble).
- **Zone large / vault entier** : possible, mais coûteux en appels d'outils.
  Si la demande est de type "audite tout le vault" sans autre précision,
  prévenir explicitement du coût et proposer de découper (par type, par ère,
  ou par dossier) plutôt que de lancer un balayage complet sans confirmation.

Résoudre le chemin réel de chaque cible AVANT toute lecture — via
`search_simple` sur le nom ou `vault_list` du dossier supposé — jamais un
chemin construit de mémoire ou depuis la doc : des divergences d'accents
existent entre Conventions et les dossiers réels. Si la cible nommée est
ambiguë (plusieurs fiches possibles dans les résultats), lister les
candidats et demander laquelle avant de continuer.

## Étape 2 — Rassembler le contexte

1. **Lire la ou les fiches cibles EN ENTIER** : `vault_read` sans `target`.
   La réponse contient `content`, `frontmatter`, `tags`, `links` et
   `backlinks` — relever le `statut` réel de chaque cible (jamais supposé).
   Ne jamais auditer à partir d'un extrait.
2. **Exploiter `links` et `backlinks`** de cette même réponse : les
   `backlinks` (fiches qui citent la cible) sont les candidates prioritaires
   aux contradictions et doublons — c'est le cross-référencement inverse
   gratuit ; les `links` disent ce que la cible mobilise. Une fiche liée
   absente des recherches par mots-clés est un angle mort classique.
3. **Recherche croisée** sur les entités, concepts et dates référencés dans
   la cible. Deux tools complémentaires :
   - `search_simple` (mots-clés) : large, scorée, avec contexte — couvre
     TOUT le vault, donc triage par zone obligatoire (point 4).
   - `search_query` (JsonLogic) : ciblage structurel. Exemples utiles :
     - canon partageant un tag de la cible :
       `{"and": [{"regexp": ["^01_Lore/", {"var": "path"}]}, {"in": ["<tag>", {"var": "tags"}]}]}`
     - fiches datées sur la même ère (candidates aux conflits de timeline) :
       `{"and": [{"regexp": ["^01_Lore/", {"var": "path"}]}, {"==": [{"var": "frontmatter.ere"}, "<ère>"]}]}`
     - restreindre aux statuts qui font foi :
       ajouter `{"in": [{"var": "frontmatter.statut"}, ["canon-verrouillé", "canon", "semi-canon"]]}`
   - `tag_list` en complément : le vocabulaire global des tags du vault.
     Deux tags quasi identiques (singulier/pluriel, variantes d'orthographe)
     sont un indice de doublon d'entités ou d'hygiène de tags à signaler en
     zone floue. `tag_list` ne dit PAS quelles fiches portent un tag — pour
     ça, `search_query` avec `{"in": [...]}` comme ci-dessus.
4. **Trier tout résultat de recherche par zone** (Conventions §7) :
   - `01_Lore/` : seule zone qui peut fonder une contradiction canon — en
     vérifiant le `statut` réel de chaque fiche mobilisée.
   - `05_IA_Inbox/`, `04_Brouillons/` : non validé — jamais source de
     contradiction canon ; un recoupement avec la cible se signale en zone
     floue (avec mention de la zone).
   - `02_Romans/`, `03_Scenarios_JDR/` : portée œuvre — un écart avec le
     canon-univers se signale, mais comme tension de portée, pas comme
     contradiction interne au canon.
   - `99_Archive/` : ancien vault NON-CANON, lecture seule — jamais mobilisé
     dans un constat, quel que soit son contenu.
5. **Si la cible contient des éléments datés** : charger
   `01_Lore/Timeline Master.md` EN ENTIER (`vault_read` sans `target` —
   jamais de mémoire, jamais de lecture partielle pour ce fichier).
6. **Lire réellement les fiches candidates** retenues aux points 2-3 —
   jamais travailler sur un titre ou un extrait de recherche seul. Pour une
   fiche longue et périphérique : `vault_get_document_map` d'abord, puis
   lecture ciblée (`target`/`targetType`) ; pour une fiche centrale au
   constat pressenti, lecture entière — une lecture partielle rate les
   contradictions.

## Étape 3 — Analyser selon les 4 axes

Pour chaque axe, ne signaler QUE ce qui a été réellement vérifié à l'Étape 2
— jamais une supposition présentée comme un constat.

1. **Contradictions avec le canon** : faits incompatibles entre la cible et
   une fiche de `01_Lore` dont le statut fait foi (`canon-verrouillé`,
   `canon`, `semi-canon`) — dates, relations, événements, attributs. Citer
   les deux fiches, leur statut, et les passages précis en tension. Une
   tension impliquant une fiche `rumeur` (croyance des habitants, pas
   fait-monde), `obsolète` ou `brouillon` se classe en zone floue avec
   mention du statut, pas en contradiction canon. Une fiche `secret` peut
   être citée dans le journal (interne au vault), en rappelant 🔒.
2. **Doublons** : deux entités qui semblent remplir le même rôle narratif,
   ou deux fiches dont le contenu se recoupe fortement au point de
   constituer un doublon plutôt que deux entités distinctes. Distinguer les
   deux cas dans le rapport (doublon de rôle vs doublon de contenu).
3. **Conflits de timeline** : incompatibilité entre la datation de la cible
   (`ere`/`annee` en frontmatter, ou dates dans le corps) et
   [[Timeline Master]] ou une autre fiche datée.
4. **Zones floues** : ambiguïtés, informations manquantes, questions non
   tranchées, tensions avec du non-validé ou d'autres portées — repérées
   pendant l'analyse, même si elles ne sont ni contradiction ni doublon à
   proprement parler.

Ne jamais arbitrer un constat : le signaler avec la notation `⚠️`
(Conventions §5), jamais le résoudre à la place de l'utilisateur.

## Étape 4 — Présenter le rapport en conversation

Structurer par les 4 axes ci-dessus. Chaque constat cite les fiches
concernées en wikilinks, avec leur statut. Si un axe n'a rien à signaler, le
dire brièvement plutôt que de l'omettre silencieusement (pour que l'absence
de constat soit distinguable d'un audit non fait).

## Étape 5 — Déposer le journal

1. **Nom de fichier** : `AAAA-MM-JJ — Audit — <Cible>.md` (cible = nom de la
   fiche, ou nom du dossier/type si périmètre élargi).
2. **`vault_list` sur `05_IA_Inbox/Audits` AVANT d'écrire** (inutile de
   créer le dossier : `vault_write` crée les parents manquants). Si un
   fichier du même nom existe déjà (même cible, même jour) : `vault_read`
   l'existant, puis proposer de le compléter — fusion en intégrant le
   contenu lu dans un nouveau contenu complet réécrit via `vault_write`
   (le filet : on a lu avant d'écraser) — ou de suffixer `— 2`. Jamais
   écraser à l'aveugle.
3. **Dans ce même listing**, si `Audits.base` est absente : la créer sans
   demander (copier le contenu d'`assets/Audits.base` vers
   `05_IA_Inbox/Audits/Audits.base` via `vault_write`) — vue installée
   d'office, même décision que `Brainstorms.base`. Si elle existe déjà, ne
   jamais la réécrire : l'utilisateur a pu la personnaliser.
4. **Contenu du journal** — cases à cocher, prêtes à être collées dans la
   section "Chantiers en cours" de `Index` (Conventions §8) :

```markdown
---
statut: brouillon
source: ai
tags: [audit-coherence]
cible: "[[<Fiche>]]"
date: <AAAA-MM-JJ>
---
# <nom du fichier sans extension>

**En une phrase :** <résumé — ex. "2 contradictions, 1 doublon de rôle, 0 conflit de timeline, 3 zones floues sur [[Cible]]">

> [!warning] Constats non arbitrés — rien ne fait foi
> Chaque ligne reste à trancher par l'auteur ; ce journal ne modifie aucune
> fiche du vault.

## Contradictions avec le canon
- [ ] ⚠️ <constat — fiches et statuts cités, wikilinks>

## Doublons
- [ ] ⚠️ <constat>

## Conflits de timeline
- [ ] ⚠️ <constat>

## Zones floues
- [ ] ⚠️ <constat>
```

   `cible:` est un wikilink entre guillemets quand le périmètre est une
   fiche unique (la propriété devient un lien réel dans Obsidian et dans la
   Base) ; texte libre entre guillemets pour un dossier/type. Omettre les
   sections sans aucun constat plutôt que d'y laisser une case vide
   trompeuse.
5. **Confirmer à l'utilisateur** : chemin du journal (+ mention de la Base
   si elle vient d'être installée), et rappel que rien n'est arbitré —
   c'est à lui de trancher chaque point, puis de reporter ce qu'il retient
   dans les Chantiers de `Index` (verrouillé pour l'IA) et, le cas échéant,
   de corriger les fiches concernées lui-même (ou via `traiter-chantier`).
   Proposer d'ouvrir le journal dans Obsidian (`open_file`) — ne l'ouvrir
   que si l'utilisateur accepte : il n'est pas forcément devant la machine
   où tourne le vault.

## Vue de triage des audits (installée d'office)

`assets/Audits.base` est copiée automatiquement vers
`05_IA_Inbox/Audits/Audits.base` dès le premier journal écrit dans ce
dossier (Étape 5, point 3) — aucune demande explicite requise. Elle sert de
MOC de facto pour l'inbox audits et comble l'angle mort Conventions §8-(2)
(une fiche de 05_IA_Inbox n'est listée dans aucune MOC) : les colonnes
Journal / Cible / Session / Statut se trient en cliquant sur leur en-tête
dans Obsidian. Une fois installée, ne plus jamais la réécrire
automatiquement : si l'utilisateur l'a modifiée (nouvelles colonnes,
filtres), une réécriture silencieuse l'effacerait. Ne jamais modifier une
Base existante sans lire d'abord `/mnt/skills/user/obsidian-bases/SKILL.md`.

## Garde-fous

- Jamais modifier la ou les fiches auditées — ni leur statut, ni leur
  section "Contradictions potentielles" (le §4 des Conventions dit qu'elle
  est vidée "après arbitrage" : l'arbitrage est le geste de l'utilisateur,
  pas de ce skill). Seules écritures autorisées : le nouveau journal, et
  `Audits.base` à sa première installation.
- Jamais arbitrer un constat — le signaler avec `⚠️`, ne jamais le résoudre.
- Jamais inventer une contradiction ou un doublon non réellement vérifié à
  l'Étape 2 — mieux vaut sous-signaler que fabriquer un constat.
- Une contradiction canon n'implique que des fiches `01_Lore` dont le statut
  fait foi — toute autre tension (rumeur, obsolète, non-validé, autre
  portée, 99_Archive) se signale en zone floue avec sa provenance, ou pas
  du tout pour 99_Archive.
- Le statut d'une fiche mobilisée est celui lu dans son frontmatter, jamais
  un statut supposé — et il est rapporté explicitement dans les constats.
- Jamais de `vault_delete`, `vault_move` ou `vault_patch` depuis ce skill,
  et jamais d'écriture dans `00_Systeme` ni `99_Archive`.
- `vault_write` écrase sans avertissement : aucune écriture sans
  vérification préalable d'inexistence (`vault_list`) ou sans
  lecture-et-fusion explicite du fichier existant.
- Jamais de chemin construit de mémoire ou depuis la doc — toujours résolu
  via recherche ou listing avant lecture.
- Sur une demande d'audit très large ("tout le vault") sans précision,
  prévenir du coût et proposer un découpage avant de lancer quoi que ce
  soit d'exhaustif.
- Si un tool MCP échoue en cours de session alors qu'il semblait
  disponible : basculer sur un repli UNIQUEMENT en Claude Code avec accès
  réel au vault (lire alors `references/modes-repli.md`) ; dans claude.ai,
  arrêter et signaler l'échec — jamais fabriquer un succès.
