---
name: traiter-chantier
description: "Reprend et exécute avec l'utilisateur une tâche déjà listée dans la sous-section « Ouverts » des « Chantiers en cours » de Index (souvent issue d'un brainstorm ou d'un audit) — décision tranchée ensemble, puis écrite directement sur les fiches concernées (double marqueur ia-a-valider en frontmatter revision + callout, additif) via le MCP obsidian-lamia, ou en Mode Fichiers/Git en repli. Déclenche dès que l'utilisateur veut avancer, traiter, trancher ou clore un chantier ouvert, demande ce qu'il reste à trancher ou d'ouvert, ou cite le libellé d'une ligne de chantier — « on traite le chantier sur X », « attaquons les chantiers », « reprenons la tâche sur Y », « il reste quoi à trancher » — même sans dire « chantier ». Si le sujet correspond à une ligne déjà ouverte des Chantiers, ce skill prime sur brainstorm-lore (réflexion neuve, brouillon en Inbox) ; distinct d'audit-coherence (constate sans modifier) — seul ce skill écrit dans des fiches existantes de 01_Lore."
compatibility: Fonctionne avec le MCP obsidian-lamia connecté au vault Lamia (obsidian_get_note, obsidian_search_notes, obsidian_list_notes, obsidian_manage_frontmatter, obsidian_patch_note, obsidian_append_to_note, obsidian_replace_in_note, obsidian_write_note). En Claude Code, si ce MCP est absent, bascule sur un accès disque direct (Read/Edit/Glob/Grep/Bash) et git — voir "Deux modes d'accès au vault".
---

# Traiter un chantier — Lamia

Ce skill reprend une tâche déjà actée comme "en attente" dans Index (section
"Chantiers en cours > Ouverts"), la tranche en collaboration avec
l'utilisateur, puis inscrit la décision directement sur la ou les fiches
concernées — c'est le seul skill du vault à exercer le protocole d'écriture
directe de `Regles_IA_Lore.md` plutôt que de déposer un brouillon dans
`05_IA_Inbox`.

## Deux modes d'accès au vault

- **Mode MCP (par défaut)** : `obsidian_get_note`, `obsidian_search_notes`,
  `obsidian_list_notes`, `obsidian_manage_frontmatter`, `obsidian_patch_note`,
  `obsidian_append_to_note`, `obsidian_replace_in_note`, `obsidian_write_note`
  disponibles → comportement décrit plus bas, inchangé.
- **Mode Fichiers/Git (Claude Code uniquement)** : si ces tools sont absents,
  ou si l'un d'eux échoue en cours de session, ET que Claude a un accès
  disque direct au vault (racine du repo git courant). Chaque étape MCP a son
  équivalent Fichiers, indiqué par « **Si MCP indisponible :** ».

⚠️ Ce mode de repli n'existe QUE là où un accès disque réel au vault est
possible. Dans claude.ai, un échec MCP doit être signalé à l'utilisateur et
la tâche interrompue — jamais improvisé, jamais présenté comme réussi.

## Étape 0 — Contexte (une fois par session, si pas déjà fait)

Charger, s'ils ne sont pas déjà dans le contexte de la conversation en
cours : `00_Systeme/Conventions.md`, `00_Systeme/Index.md`, et
`00_Systeme/Regles_IA_Lore.md` (`obsidian_get_note`, **si MCP indisponible :**
`Read`). Ce dernier fichier définit le protocole d'écriture directe dont ce
skill dépend entièrement — contrairement aux autres skills du vault, qui
n'écrivent jamais hors de `05_IA_Inbox`. En cas de divergence entre ce
skill et `Regles_IA_Lore.md`, le fichier du vault prime — signaler la
divergence à l'utilisateur pour mise à jour du skill.

Si le chantier touche une chronologie ou des dates : charger
`01_Lore/Timeline Master.md` EN ENTIER avant de discuter — jamais de mémoire.
**Si MCP indisponible :** `Read` ce même fichier en entier.

## Étape 1 — Identifier le ou les chantiers à traiter

- Si l'utilisateur nomme un chantier précis (mot-clé qui matche une ligne de
  "Ouverts"), aller directement dessus.
- Sinon, lire `Index.md` section `Chantiers en cours::Ouverts`
  (`obsidian_get_note`, `format: "section"`, `section: {type: "heading",
  target: "Chantiers en cours::Ouverts"}`). **Si MCP indisponible :** `Read`
  `00_Systeme/Index.md` et repérer la même section. Lister les items ouverts,
  demander lequel traiter en premier.
- Un seul chantier traité à la fois par défaut. N'enchaîner sur un autre que
  si l'utilisateur le demande explicitement en cours de session.
- Si le chantier couvre un grand nombre de fiches (ex. "recalibrer le rang
  des ~20 divinités"), signaler l'ampleur et proposer un découpage (par lot)
  avant de tout traiter d'un coup sans confirmation — même logique que
  audit-coherence sur "tout le vault".

## Étape 2 — Rassembler le contexte du chantier choisi

1. Identifier la ou les fiches concernées (wikilinks présents dans la ligne
   du chantier, ou déduites du sujet). Si le chantier référence une fiche
   brainstorm ou un journal d'audit ("voir [[...]]"), la lire EN ENTIER — 
   c'est la matière de départ de la décision.
2. Résoudre chaque wikilink en chemin réel AVANT toute lecture ou
   écriture : un `[[Nom]]` ne porte pas de chemin, et les tools exigent un
   chemin exact. Passer par `obsidian_search_notes` (mode `text` sur le
   nom) ou `obsidian_list_notes` — jamais par un chemin construit de
   mémoire ou depuis la doc : des divergences d'accents existent entre
   Conventions et les dossiers réels (ex. `01_Lore/Évenements/`, deuxième
   e sans accent), et un chemin faux échoue silencieusement.
   **Si MCP indisponible :** `Glob` sur le nom de fichier.
3. Lire les fiches concernées EN ENTIER (`obsidian_get_note`, format
   `content` ou `full`). **Si MCP indisponible :** `Read`. Ne jamais trancher
   à partir d'un extrait ou d'un souvenir.
4. Si utile, chercher le canon existant lié au sujet
   (`obsidian_search_notes`, `pathPrefix: "01_Lore"`). Attention :
   `pathPrefix` est un POST-filtre appliqué après la recherche, pas un
   scope — une page de résultats peut revenir vide alors que des hits
   existent aux pages suivantes ; en cas de vide suspect, paginer via
   `nextCursor` avant de conclure à l'absence.
   **Si MCP indisponible :** `Grep`/`Glob` sur `01_Lore/`.

## Étape 3 — Trancher ensemble (jamais de yes-man)

Même discipline que le Mode A de `brainstorm-lore` : présenter les pistes
concurrentes s'il y en a, tester chacune contre l'exploitabilité et les
contradictions déjà connues, donner au moins un contre-argument même pour
une piste qui semble bonne. **"Retenu" = validé explicitement par
l'utilisateur dans l'échange** — jamais tranché seul par Claude, jamais par
défaut ni par enthousiasme.

Si le chantier n'est qu'une confirmation simple déjà bien cadrée, aller plus
vite — mais ne jamais sauter la validation explicite avant d'écrire quoi que
ce soit.

À l'inverse, si le chantier s'avère être une question encore largement
ouverte (plusieurs pistes lourdes, beaucoup de non-tranché après discussion),
proposer de basculer vers une vraie session `brainstorm-lore` — fiche
déposée en Inbox, chantier laissé ouvert — plutôt que de forcer une décision
pour pouvoir cocher la case. Un chantier qui reste ouvert honnêtement vaut
mieux qu'une décision arrachée.

## Étape 4 — Écrire la décision (protocole d'écriture directe)

**Cas d'une fiche à CRÉER** (ex. chantier « Créer une fiche evenement dédiée
aux Xeroniens ») : une fiche nouvelle n'est jamais créée directement dans
`01_Lore` par ce skill, même si son contenu a été décidé ensemble. Elle est
déposée en `05_IA_Inbox` comme proposition
(`AAAA-MM-JJ — Proposition — Titre.md`, `statut: brouillon` + `source: ia`,
frontmatter et structure conformes aux Conventions §3-§4) — cohérent avec la
décision actée de `migrer-fiche` : le déplacement vers `01_Lore` reste le
geste de l'utilisateur, jamais celui de l'IA. L'écriture directe ci-dessous
ne concerne que les fiches DÉJÀ existantes de `01_Lore`.

Pour chaque fiche concernée, **hors Timeline Master et hors 00_Systeme**
(jamais touchés à cette étape — voir Étape 4bis et Garde-fous) :

1. Vérifier le `statut` actuel (`obsidian_manage_frontmatter`, `get`). S'il
   est `canon` ou `canon-verrouillé`, le signaler explicitement avant
   d'écrire (Conventions §1 : modifiable, mais vérifier les notes liées
   avant) — ne jamais s'arrêter d'écrire pour autant si l'utilisateur a
   validé la décision, juste le rendre visible.
2. Vérifier si un marqueur `revision:` existe déjà. S'il porte une valeur
   différente de `ia-a-valider` (ou si sa présence suggère une révision
   antérieure pas encore validée), le signaler à l'utilisateur avant
   d'écraser plutôt que de l'effacer silencieusement.
3. Poser le double marqueur :
   - Frontmatter : `obsidian_manage_frontmatter` (`operation: "set"`, `key:
     "revision"`, `value: "ia-a-valider"`).
   - Callout au point modifié, dans le MÊME appel que le contenu ajouté :
     un seul `obsidian_patch_note` (section concernée, `operation:
     "append"`) — ou `obsidian_append_to_note` si aucune section précise
     ne convient — dont le contenu est le callout `> [!ia-a-valider]
     AAAA-MM-JJ — Objet : [décision consignée]. Modifié : [quoi].`
     immédiatement suivi du texte ajouté. Jamais deux appels séparés pour
     le callout et le contenu : ils pourraient se retrouver disjoints dans
     la fiche.
   - Cibler la section par sa syntaxe exacte : `obsidian_get_note` en
     `format: "document-map"` donne le catalogue des headings et la forme
     `Parent::Child` à utiliser — ne pas deviner le nom d'une section.
   - Retries : `patch_note` rejette par défaut un contenu déjà présent
     dans la cible (`applyIfContentPreexists: false`). Un échec de ce type
     après une coupure signifie que l'écriture a probablement déjà réussi
     — relire la fiche avant de forcer.
4. Écriture **additive par défaut** : ajouter sans réécrire ni supprimer la
   prose existante, sauf demande explicite de l'utilisateur dans la
   conversation en cours. Ne jamais utiliser `obsidian_write_note` en pleine
   page (`overwrite: true`) sur une fiche existante à cette étape.
5. Ne jamais poser `statut: canon` ou `canon-verrouillé` — geste exclusif de
   l'utilisateur, quelle que soit la décision prise ensemble.

**Si MCP indisponible :** éditer les mêmes cibles avec `Read`/`Edit` (ajout du
frontmatter `revision` + callout, additif). Puis, seulement si le vault est
un dépôt git (`git rev-parse --is-inside-work-tree`) :
```bash
git add "<fiche 1>" "<fiche 2>"
git commit -m "[ia-a-valider] Chantier — <Sujet>" -- "<fiche 1>" "<fiche 2>"
```
Ne JAMAIS `git add -A`/`git add .`/`git commit -a` : uniquement les fichiers
réellement modifiés à cette étape.

## Étape 4bis — Cas particulier : Timeline Master

Décision actée : Timeline Master n'est **jamais modifié directement**, même
si la décision est validée, même s'il vit dans `01_Lore`.

1. Chercher `05_IA_Inbox/Update - Timeline Master.md`.
2. **S'il n'existe pas** : le créer comme copie conforme intégrale de
   `Timeline Master` (lire l'original en entier, puis
   `obsidian_write_note` avec ce contenu sur le nouveau fichier,
   `overwrite: false`).
3. **S'il existe déjà** (chantier précédent pas encore reporté) : lire la
   copie EN ENTIER, relire l'original EN ENTIER, et comparer AVANT
   d'écrire. Si l'original a évolué depuis la création de la copie
   (entrées nouvelles ou modifiées absentes de la copie, hors marqueurs
   `ia-a-valider`), le signaler explicitement : la copie est périmée et le
   report final serait un merge à trois sources. Proposer à l'utilisateur
   de réintégrer d'abord ces évolutions dans la copie (sans toucher aux
   propositions en attente), ou de reporter/valider les propositions avant
   de continuer. Ensuite seulement, intégrer les nouvelles modifications
   par-dessus la copie — ne jamais repartir de l'original, pour ne pas
   perdre les propositions antérieures encore en attente.
4. Appliquer les modifications décidées sur cette copie, avec le même double
   marqueur (`revision: ia-a-valider` + callout) que pour les autres fiches.
5. Confirmer explicitement à l'utilisateur que l'original n'a pas bougé — la
   version modifiée vit uniquement dans
   `05_IA_Inbox/Update - Timeline Master.md`, à comparer et reporter lui-même.

**Si MCP indisponible :** même logique avec `Read`/`Write` sur
`05_IA_Inbox/Update - Timeline Master.md` ; commit git de ce seul fichier si
le vault est un dépôt git, jamais de l'original.

## Étape 5 — Journal de session (proposition, optionnelle)

Déposer un court récapitulatif `AAAA-MM-JJ — Chantier — <Sujet-en-un-mot>.md`
dans `05_IA_Inbox/Chantiers/` (l'écriture MCP crée le dossier au premier
dépôt s'il manque — vérifié le 2026-07-19 ; si elle échoue malgré tout,
déposer à la racine de `05_IA_Inbox` et le signaler) : fiches touchées
(wikilinks) et rappel
qu'elles portent `revision: ia-a-valider`, mention du fichier Update -
Timeline Master le cas échéant, et le texte exact à reporter dans Index
(voir Étape 6). Sans ce journal, les marqueurs posés en session ne sont
retrouvables qu'en rouvrant chaque fiche une à une — à garder ou à laisser
tomber selon préférence.

## Étape 6 — Confirmer et rendre la main sur Index

Présenter à l'utilisateur, sans rien écrire dans Index (00_Systeme reste
fermé en écriture à l'IA) :

- Chaque fiche modifiée (chemin + wikilink), avec le double marqueur posé.
- Le commit git s'il a eu lieu (Mode Fichiers/Git).
- Pour Timeline Master : rappel explicite que l'original n'a pas bougé.
- Le texte exact à coller soi-même dans Index :
  - la ligne "Ouverts" concernée, à cocher ;
  - la ligne à ajouter sous "Tranchés" :
    `- [x] <résumé de la décision> (<fiche(s) concernée(s)>, <date>)` — ce
    format exact fait foi ; les entrées historiques de "Tranchés" sont
    hétérogènes, ne pas les imiter.
- Rappel explicite : rien n'est validé tant que `ia-a-valider` reste posé —
  la validation de l'utilisateur = suppression du marqueur + commit
  (`Regles_IA_Lore`).

## Garde-fous

- Jamais de yes-man : chaque décision "Retenu" validée explicitement par
  l'utilisateur dans l'échange, jamais par défaut ni par enthousiasme.
- Jamais écrire dans `00_Systeme` — donc jamais dans `Index` lui-même :
  toujours donner le texte à coller, jamais le coller soi-même.
- Jamais poser `statut: canon` ou `canon-verrouillé`.
- Jamais créer une fiche NOUVELLE dans `01_Lore` — toute création passe par
  une proposition en `05_IA_Inbox` ; l'écriture directe est réservée aux
  fiches existantes.
- Jamais forcer une décision pour pouvoir clore un chantier — si la question
  reste réellement ouverte, proposer de basculer en `brainstorm-lore` et
  laisser le chantier ouvert.
- Jamais toucher `Timeline Master` directement — toujours via
  `05_IA_Inbox/Update - Timeline Master.md` ; et jamais écrire dans cette
  copie sans avoir d'abord comparé copie et original (dérive à signaler
  avant, pas après).
- Jamais construire un chemin de fiche de mémoire ou depuis la doc —
  toujours résoudre le chemin réel (`search`/`list`) avant lecture ou
  écriture.
- Jamais réécrire ou supprimer de la prose existante sans demande explicite
  — additif par défaut.
- Jamais écraser silencieusement un marqueur `revision:` préexistant portant
  une autre valeur — le signaler avant.
- Sur un chantier à grande échelle, prévenir du volume et proposer un
  découpage avant de tout traiter d'un coup.
- En Mode Fichiers/Git : ne jamais `git add`/`git commit` autre chose que
  les fichiers réellement modifiés à cette session — jamais l'arbre de
  travail entier.
- Si un tool MCP échoue en cours de session alors qu'il semblait disponible,
  basculer en Mode Fichiers/Git UNIQUEMENT si un accès disque réel existe ;
  sinon, arrêter et signaler l'échec — jamais fabriquer un succès.
