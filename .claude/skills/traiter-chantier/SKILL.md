---
name: traiter-chantier
description: "Reprend et exécute avec l'utilisateur une tâche déjà listée dans la sous-section « Ouverts » des « Chantiers en cours » de Index (souvent issue d'un brainstorm ou d'un audit) — décision tranchée ensemble, puis écrite directement sur les fiches concernées (double marqueur ia-a-valider en frontmatter revision + callout, additif) via le MCP obsidian-lamia, ou en Mode Local (CLI Obsidian / Fichiers-Git) en repli. Déclenche dès que l'utilisateur veut avancer, traiter, trancher ou clore un chantier ouvert, demande ce qu'il reste à trancher ou d'ouvert, ou cite le libellé d'une ligne de chantier — « on traite le chantier sur X », « attaquons les chantiers », « reprenons la tâche sur Y », « il reste quoi à trancher » — même sans dire « chantier ». Si le sujet correspond à une ligne déjà ouverte des Chantiers, ce skill prime sur brainstorm-lore (réflexion neuve, brouillon en Inbox) ; distinct d'audit-coherence (constate sans modifier) — seul ce skill écrit dans des fiches existantes de 01_Lore."
compatibility: "Mode par défaut : MCP obsidian-lamia (obsidian_get_note, obsidian_search_notes, obsidian_list_notes, obsidian_manage_frontmatter, obsidian_patch_note, obsidian_append_to_note, obsidian_replace_in_note, obsidian_write_note). En Claude Code sans MCP : CLI Obsidian (`obsidian`, app ouverte) si disponible, sinon accès disque direct (Read/Edit/Glob/Grep/Bash) + git — voir « Voies d'accès au vault »."
---

# Traiter un chantier — Lamia

Ce skill reprend une tâche déjà actée comme "en attente" dans Index (section
"Chantiers en cours > Ouverts"), la tranche en collaboration avec
l'utilisateur, puis inscrit la décision directement sur la ou les fiches
concernées — c'est le seul skill du vault à exercer le protocole d'écriture
directe de `Regles_IA_Lore.md` plutôt que de déposer un brouillon dans
`05_IA_Inbox`.

## Syntaxe Obsidian — sources d'autorité

Tout ce qui est écrit dans le vault doit être de l'Obsidian Flavored Markdown
valide. Les skills officiels Obsidian installés font foi pour la syntaxe — ne
pas improviser de mémoire :

- `/mnt/skills/user/obsidian-markdown/SKILL.md` — wikilinks, embeds,
  callouts, propriétés, block IDs. Références détaillées dans
  `references/` (CALLOUTS.md, PROPERTIES.md, EMBEDS.md).
- `/mnt/skills/user/obsidian-bases/SKILL.md` — syntaxe `.base` (filtres,
  vues). À lire AVANT de toucher un fichier `.base` : la syntaxe des
  filtres et formules ne se devine pas.

Les formes protocolaires critiques (marqueur de révision, block ID) sont
inlinées plus bas ; pour tout le reste (embed d'une fiche brainstorm, tableau,
lien vers un heading `[[Fiche#Section]]`…), consulter ces références plutôt
que de deviner. Rappels utiles : wikilinks pour tout lien interne (Obsidian
suit les renommages), liens Markdown réservés aux URLs externes ; une
propriété de type lien s'écrit entre guillemets (`related: "[[Fiche]]"`) ;
les dates en frontmatter au format `AAAA-MM-JJ` pour être reconnues comme
type Date.

## Voies d'accès au vault

1. **Mode MCP (par défaut, partout)** : les tools `obsidian_*` listés en
   compatibility sont disponibles → comportement décrit plus bas.
2. **Mode Local (Claude Code uniquement)** : si les tools MCP sont absents,
   ou si l'un d'eux échoue en cours de session, ET que Claude a un accès
   disque direct au vault (racine du repo git courant). Dans ce mode :
   - **CLI Obsidian d'abord**, si `obsidian help` répond (nécessite l'app
     Obsidian ouverte) : `obsidian read file="Nom"` (résout comme un
     wikilink — nom seul, sans chemin ni extension), `obsidian search
     query="…"`, `obsidian backlinks file="Nom"`,
     `obsidian property:set name="…" value="…" file="Nom"`. La résolution
     par nom du CLI contourne le problème des divergences d'accents entre
     chemins documentés et chemins réels.
   - **Fichiers/Git en dernier recours** : `Read`/`Edit`/`Glob`/`Grep` +
     commit git ciblé. Les insertions dans une section précise se font
     toujours via `Edit` (le CLI ne cible pas une section), mais la pose
     du marqueur frontmatter passe de préférence par `property:set`
     (atomique, pas de YAML édité à la main).
   Chaque étape MCP a son équivalent, indiqué par « **Si MCP
   indisponible :** ».

⚠️ Le Mode Local n'existe QUE là où un accès disque réel au vault est
possible. Dans claude.ai, un échec MCP doit être signalé à l'utilisateur et
la tâche interrompue — jamais improvisé, jamais présenté comme réussi.

## Étape 0 — Contexte (une fois par session, si pas déjà fait)

Charger, s'ils ne sont pas déjà dans le contexte de la conversation en
cours : `00_Systeme/Conventions.md`, `00_Systeme/Index.md`, et
`00_Systeme/Regles_IA_Lore.md` (`obsidian_get_note`, **si MCP indisponible :**
`obsidian read file=…` ou `Read`). Ce dernier fichier définit le protocole
d'écriture directe dont ce skill dépend entièrement — contrairement aux
autres skills du vault, qui n'écrivent jamais hors de `05_IA_Inbox`. En cas
de divergence entre ce skill et `Regles_IA_Lore.md`, le fichier du vault
prime — signaler la divergence à l'utilisateur pour mise à jour du skill.

Si le chantier touche une chronologie ou des dates : charger
`01_Lore/Timeline Master.md` EN ENTIER avant de discuter — jamais de mémoire.
**Si MCP indisponible :** lire ce même fichier en entier (CLI ou `Read`).

## Étape 1 — Identifier le ou les chantiers à traiter

- Si l'utilisateur nomme un chantier précis (mot-clé qui matche une ligne de
  "Ouverts"), aller directement dessus.
- Sinon, lire `Index.md` section `Chantiers en cours::Ouverts`
  (`obsidian_get_note`, `format: "section"`, `section: {type: "heading",
  target: "Chantiers en cours::Ouverts"}`). **Si MCP indisponible :** lire
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
   écriture : un `[[Nom]]` ne porte pas de chemin, et les tools MCP exigent
   un chemin exact. Passer par `obsidian_search_notes` (mode `text` sur le
   nom) ou `obsidian_list_notes` — jamais par un chemin construit de
   mémoire ou depuis la doc : des divergences d'accents existent entre
   Conventions et les dossiers réels (ex. `01_Lore/Évenements/`, deuxième
   e sans accent), et un chemin faux échoue silencieusement.
   **Si MCP indisponible :** CLI `obsidian read file="Nom"` (résolution
   native façon wikilink) pour lire ; pour un chemin exact (édition disque,
   git), `obsidian search query="Nom"` ou `Glob` sur le nom de fichier.
3. Lire les fiches concernées EN ENTIER (`obsidian_get_note`, format
   `content` ou `full`). **Si MCP indisponible :** CLI `read` ou `Read`.
   Ne jamais trancher à partir d'un extrait ou d'un souvenir.
4. **Obligatoire — pas seulement "si utile"** : avant de réécrire
   l'Histoire, le Résumé ou les Relations d'une fiche existante, vérifier
   ses `backlinks` (déjà renvoyés par `obsidian_get_note` à l'Étape 2.3) ET
   lancer une recherche texte sur son nom (`obsidian_search_notes`, mode
   `text`) pour repérer les mentions non liées. Lire EN ENTIER toute fiche
   de type `evenement` ou `objet` qui en ressort et qui n'a pas encore été
   lue cette session, même si elle ne semble pas centrale au premier coup
   d'œil. Les Relations déjà présentes sur la fiche ne suffisent pas :
   elles reflètent ce qui était su au moment de leur rédaction, pas le
   canon qui a pu s'y ajouter depuis. Un oubli ici crée une incohérence
   silencieuse, découverte seulement si l'utilisateur la remarque
   lui-même — expérience vécue (fiche Naphusis, 2026-07-28 : deux
   événements canon déjà établis, passés inaperçus jusqu'à ce que
   l'utilisateur signale leur absence de l'Histoire).
   Ne pas se limiter à la première page de résultats : `pathPrefix` est un
   POST-filtre appliqué après la recherche, pas un scope — une page peut
   revenir vide alors que des hits existent aux pages suivantes ; paginer
   via `nextCursor` avant de conclure à l'absence.
   **Si MCP indisponible :** CLI `obsidian backlinks file="Nom"` et
   `obsidian search query="Nom"`, ou `Grep`/`Glob` sur `01_Lore/`.

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

### Forme du marqueur (protocole — inline car critique)

Le double marqueur se pose ainsi, et nulle part ailleurs sous une autre
forme :

- **Frontmatter** : `revision: ia-a-valider` (propriété texte) et
  `revision-date: AAAA-MM-JJ` (propriété date — format strict pour être
  reconnue par Obsidian et filtrable en Base). `revision-date` est une
  convention additive récente : si `Regles_IA_Lore.md` ne la mentionne pas
  encore, la poser quand même mais la signaler à l'utilisateur en fin de
  session pour ratification.
- **Callout**, au point modifié, repliable et référençable :

  ```markdown
  > [!ia-a-valider]- AAAA-MM-JJ — <Objet court>
  > **Décision** : <décision consignée>.
  > **Modifié** : <ce qui a été ajouté ou changé>.
  <texte ajouté, le cas échéant>

  ^rev-AAAAMMJJ-<slug>
  ```

  Le `-` après `[!ia-a-valider]` rend le callout replié par défaut : en
  lecture, seule la ligne de titre (marqueur + date + objet) reste
  visible — une fiche portant plusieurs révisions en attente reste
  lisible. Le block ID `^rev-AAAAMMJJ-<slug>` va sur sa propre ligne,
  APRÈS une ligne vide qui suit le bloc (règle Obsidian pour les
  citations et callouts — un ID collé au bloc ne s'attache pas). Slug en
  ASCII pur : minuscules, chiffres, tirets, pas d'accents — un block ID
  accentué est fragile. Ce block ID permet de lier la révision exacte
  depuis le journal ou depuis Index : `[[Fiche#^rev-AAAAMMJJ-slug]]`.
  `[!ia-a-valider]` est un type de callout custom : sans snippet CSS côté
  vault il s'affiche avec le style `note` par défaut — fonctionnel et
  cherchable, seulement moins visible (voir CALLOUTS.md § Custom Callouts
  si l'utilisateur veut le styler).

### Procédure par fiche

Pour chaque fiche concernée, **hors Timeline Master et hors 00_Systeme**
(jamais touchés à cette étape — voir Étape 4bis et Garde-fous) :

1. Vérifier le `statut` actuel (`obsidian_manage_frontmatter`, `get`). S'il
   est `canon` ou `canon-verrouillé`, le signaler explicitement avant
   d'écrire (Conventions §1 : modifiable, mais vérifier les notes liées
   avant) — et vérifier concrètement les notes liées : **Si MCP
   indisponible :** CLI `obsidian backlinks file="Nom"` donne la liste
   exacte des fiches entrantes ; en Mode MCP, approximer par
   `obsidian_search_notes` (mode `text`) sur le nom de la fiche pour
   repérer qui la cite. Ne jamais s'arrêter d'écrire pour autant si
   l'utilisateur a validé la décision, juste rendre visible ce qui
   dépend de la fiche.
2. Vérifier si un marqueur `revision:` existe déjà. S'il porte une valeur
   différente de `ia-a-valider` (ou si sa présence suggère une révision
   antérieure pas encore validée), le signaler à l'utilisateur avant
   d'écraser plutôt que de l'effacer silencieusement.
3. Poser le double marqueur :
   - Frontmatter : `obsidian_manage_frontmatter` (`operation: "set"`,
     `key: "revision"`, `value: "ia-a-valider"`), puis idem pour
     `revision-date`. **Si MCP indisponible :** CLI
     `obsidian property:set` (deux appels), sinon édition YAML via `Edit`.
   - Callout + contenu + block ID dans le MÊME appel : un seul
     `obsidian_patch_note` (section concernée, `operation: "append"`) —
     ou `obsidian_append_to_note` si aucune section précise ne convient —
     dont le contenu est le bloc complet de la « Forme du marqueur »
     ci-dessus. Jamais d'appels séparés pour le callout, le texte et le
     block ID : disjoints, ils se retrouveraient éparpillés dans la
     fiche. **Si MCP indisponible :** un seul `Edit` insérant le bloc
     complet au bon endroit (le CLI `append` ne cible pas une section —
     ne l'utiliser que si l'ajout va légitimement en fin de fiche).
   - Cibler la section par sa syntaxe exacte : `obsidian_get_note` en
     `format: "document-map"` donne le catalogue des headings et la forme
     `Parent::Child` à utiliser — ne pas deviner le nom d'une section.
   - Retries : `patch_note` rejette par défaut un contenu déjà présent
     dans la cible (`applyIfContentPreexists: false`). Un échec de ce
     type après une coupure signifie que l'écriture a probablement déjà
     réussi — relire la fiche avant de forcer.
4. Écriture **additive par défaut** : ajouter sans réécrire ni supprimer la
   prose existante, sauf demande explicite de l'utilisateur dans la
   conversation en cours. Ne jamais utiliser `obsidian_write_note` en pleine
   page (`overwrite: true`) sur une fiche existante à cette étape.
5. Ne jamais poser `statut: canon` ou `canon-verrouillé` — geste exclusif de
   l'utilisateur, quelle que soit la décision prise ensemble.

**Si MCP indisponible**, après les éditions locales, et seulement si le
vault est un dépôt git (`git rev-parse --is-inside-work-tree`) :
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
4. Appliquer les modifications décidées sur cette copie, avec la même
   « Forme du marqueur » que pour les autres fiches (frontmatter +
   callout replié + block ID).
5. Confirmer explicitement à l'utilisateur que l'original n'a pas bougé — la
   version modifiée vit uniquement dans
   `05_IA_Inbox/Update - Timeline Master.md`, à comparer et reporter
   lui-même.

**Si MCP indisponible :** même logique en local (CLI `read` pour comparer,
`Write`/`Edit` sur `05_IA_Inbox/Update - Timeline Master.md`) ; commit git
de ce seul fichier si le vault est un dépôt git, jamais de l'original.

## Étape 5 — Retrouvabilité : Base et journal de session

Le problème à résoudre : sans dispositif dédié, les marqueurs posés en
session ne sont retrouvables qu'en rouvrant chaque fiche une à une. Deux
outils complémentaires, tous deux optionnels et proposés à l'utilisateur :

**a) Base « Revisions en attente » (recommandé — vue vivante).** Vérifier
si une Base filtrant les révisions existe déjà (`obsidian_search_notes` sur
`revision` dans les `.base`, ou demander à l'utilisateur — c'est plus
fiable). Si non, proposer de déposer dans `05_IA_Inbox` une copie du
fichier fourni avec ce skill, `assets/Revisions en attente.base`
(`obsidian_write_note` avec son contenu, `overwrite: false` ; **si MCP
indisponible :** copie disque). L'utilisateur la déplacera où il veut —
une Base filtre tout le vault quel que soit son emplacement. Elle liste en
continu toutes les fiches portant `revision: ia-a-valider`, triables par
`revision-date` : c'est la vue de contrôle des validations en attente, qui
survit aux sessions. Ne jamais modifier une Base existante sans lire
d'abord `/mnt/skills/user/obsidian-bases/SKILL.md`.

**b) Journal de session (ponctuel).** Déposer un court récapitulatif
`AAAA-MM-JJ — Chantier — <Sujet-en-un-mot>.md` dans `05_IA_Inbox/Chantiers/`
(l'écriture MCP crée le dossier au premier dépôt s'il manque — vérifié le
2026-07-19 ; si elle échoue malgré tout, déposer à la racine de
`05_IA_Inbox` et le signaler) : fiches touchées, en liant chaque révision
par son block ID exact (`[[Fiche#^rev-AAAAMMJJ-slug]]` — lien direct vers
le callout posé, pas seulement vers la fiche), mention du fichier Update -
Timeline Master le cas échéant, et le texte exact à reporter dans Index
(voir Étape 6). Si la Base est en place, le journal devient un simple
compte rendu de séance — à garder ou à laisser tomber selon préférence.

## Étape 6 — Confirmer et rendre la main sur Index

Présenter à l'utilisateur, sans rien écrire dans Index (00_Systeme reste
fermé en écriture à l'IA) :

- Chaque fiche modifiée (chemin + wikilink), avec le double marqueur posé
  et le block ID de chaque révision (`[[Fiche#^rev-…]]`).
- Le commit git s'il a eu lieu (Mode Local).
- Pour Timeline Master : rappel explicite que l'original n'a pas bougé.
- Le texte exact à coller soi-même dans Index :
  - la ligne "Ouverts" concernée, à cocher ;
  - la ligne à ajouter sous "Tranchés" :
    `- [x] <résumé de la décision> (<fiche(s) concernée(s)>, <date>)` — ce
    format exact fait foi ; les entrées historiques de "Tranchés" sont
    hétérogènes, ne pas les imiter.
- Rappel explicite : rien n'est validé tant que `ia-a-valider` reste posé —
  la validation de l'utilisateur = suppression du marqueur (frontmatter
  `revision` ET `revision-date` ET callout) + commit (`Regles_IA_Lore`).
  Si la Base est en place, la fiche disparaît de « Revisions en attente »
  dès que `revision` est retiré — c'est le témoin de validation.

## Garde-fous

- Jamais de yes-man : chaque décision "Retenu" validée explicitement par
  l'utilisateur dans l'échange, jamais par défaut ni par enthousiasme.
- Jamais écrire dans `00_Systeme` — donc jamais dans `Index` lui-même :
  toujours donner le texte à coller, jamais le coller soi-même. Vaut pour
  toutes les voies d'accès, CLI compris.
- Jamais poser `statut: canon` ou `canon-verrouillé`.
- Jamais créer une fiche NOUVELLE dans `01_Lore` — toute création passe par
  une proposition en `05_IA_Inbox` ; l'écriture directe est réservée aux
  fiches existantes. Vaut aussi pour `obsidian create` côté CLI.
- Jamais forcer une décision pour pouvoir clore un chantier — si la question
  reste réellement ouverte, proposer de basculer en `brainstorm-lore` et
  laisser le chantier ouvert.
- Jamais toucher `Timeline Master` directement — toujours via
  `05_IA_Inbox/Update - Timeline Master.md` ; et jamais écrire dans cette
  copie sans avoir d'abord comparé copie et original (dérive à signaler
  avant, pas après).
- Jamais construire un chemin de fiche de mémoire ou depuis la doc —
  toujours résoudre le chemin réel (`search`/`list` MCP, ou résolution par
  nom du CLI) avant lecture ou écriture.
- Jamais réécrire ou supprimer de la prose existante sans demande explicite
  — additif par défaut.
- Avant de réécrire Histoire/Résumé/Relations d'une fiche existante,
  vérifier systématiquement ses backlinks et lancer une recherche texte
  sur son nom (Étape 2, point 4) — ne jamais se fier aux seules Relations
  déjà présentes sur la fiche pour connaître le canon qui la concerne.
- Jamais écraser silencieusement un marqueur `revision:` préexistant portant
  une autre valeur — le signaler avant.
- Jamais improviser de la syntaxe Obsidian avancée (Base, embed, propriété
  typée…) — la vérifier dans les skills officiels référencés en tête.
- Block IDs toujours en ASCII pur, jamais dupliqués dans une même fiche
  (suffixer `-2`, `-3`… si plusieurs révisions le même jour sur la même
  fiche).
- Sur un chantier à grande échelle, prévenir du volume et proposer un
  découpage avant de tout traiter d'un coup.
- En Mode Local : ne jamais `git add`/`git commit` autre chose que les
  fichiers réellement modifiés à cette session — jamais l'arbre de travail
  entier.
- Si un tool MCP échoue en cours de session alors qu'il semblait disponible,
  basculer en Mode Local UNIQUEMENT si un accès disque réel existe ;
  sinon, arrêter et signaler l'échec — jamais fabriquer un succès.
