---
name: traiter-chantier
description: "Écrit directement sur une fiche déjà existante de 01_Lore : soit un chantier listé dans \"Chantiers en cours > Ouverts\" de Index, soit une édition ponctuelle demandée dans l'échange sans passer par Index (\"corrige X sur Y\", \"ajoute ce paragraphe à Y\"). Même protocole dans les deux cas : double marqueur ia-a-valider + cérémonie complète (backlinks, Timeline Master, Base, Journal) via MCP obsidian ou Mode Local en repli. Déclenche dès que l'utilisateur veut avancer, traiter, trancher ou clore un chantier, demande ce qui reste ouvert, cite une ligne de Chantiers, OU demande explicitement de corriger, compléter ou modifier une fiche existante précise, même sans lien avec Index. Ne déclenche PAS sur une simple discussion ou lecture sans demande d'écriture. Prime sur brainstorm-lore si le sujet est déjà un chantier ouvert ; distinct de creer-fiche (fiche neuve) et d'audit-coherence (constate sans modifier) : seul skill à écrire dans des fiches existantes de 01_Lore."
compatibility: "Mode par défaut : MCP obsidian (vault_read, vault_write, vault_patch, vault_append, vault_list, vault_get_document_map, search_simple, search_query, tag_list, active_file_get_path). En Claude Code sans MCP : CLI Obsidian (`obsidian`, app ouverte) si disponible, sinon accès disque direct (Read/Edit/Glob/Grep/Bash) + git — voir « Voies d'accès au vault »."
---

# Traiter un chantier — Lamia

Ce skill écrit directement sur une ou des fiches déjà EXISTANTES de
`01_Lore` — c'est le seul skill du vault à exercer le protocole d'écriture
directe de `Regles_IA_Lore.md` plutôt que de déposer un brouillon dans
`05_IA_Inbox`. Deux origines possibles, toujours traitées par la MÊME
procédure complète (Étapes 0 à 6, sans raccourci ni palier allégé — la
légèreté apparente d'une demande n'est pas un critère fiable pour sauter une
étape) :

- **Chantier tracké** : une tâche déjà actée comme "en attente" dans Index
  (section "Chantiers en cours > Ouverts"), tranchée en collaboration avec
  l'utilisateur puis inscrite sur la ou les fiches concernées.
- **Édition ad hoc** : une demande de modification d'une fiche précise,
  formulée directement dans l'échange, sans être passée par Index au
  préalable (ex. "corrige la date de naissance sur la fiche Kael", "ajoute
  ce paragraphe à l'Histoire de Naphusis"). Décision actée le 2026-08-07 :
  pas de palier allégé séparé pour ces éditions — même rigueur que pour un
  chantier tracké (backlinks, cas Timeline Master, Base, Journal). Seule
  différence de traitement : voir Étape 1 (identification) et Étape 6
  (absence de ligne "Ouverts" à cocher).

Ce qui ne relève PAS de ce skill : une simple discussion ou lecture d'une
fiche sans demande d'écriture explicite (aucun skill à déclencher, ou
`brainstorm-lore` si l'utilisateur veut explorer) ; la création d'une fiche
qui n'existe pas encore (`creer-fiche`) ; un constat sans modification
(`audit-coherence`).

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

1. **Mode MCP (par défaut, partout)** : les tools `vault_*`/`search_*`
   listés en `compatibility` sont disponibles → comportement décrit plus
   bas.
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
`00_Systeme/Regles_IA_Lore.md` (`vault_read`, **si MCP indisponible :**
`obsidian read file=…` ou `Read`). Ce dernier fichier définit le protocole
d'écriture directe dont ce skill dépend entièrement — contrairement aux
autres skills du vault, qui n'écrivent jamais hors de `05_IA_Inbox`. En cas
de divergence entre ce skill et `Regles_IA_Lore.md`, le fichier du vault
prime — signaler la divergence à l'utilisateur pour mise à jour du skill.

Si le chantier touche une chronologie ou des dates : charger
`01_Lore/Timeline Master.md` EN ENTIER avant de discuter — jamais de mémoire.
**Si MCP indisponible :** lire ce même fichier en entier (CLI ou `Read`).

## Étape 1 — Identifier ce qui doit être traité

D'abord déterminer l'origine, puis suivre la branche correspondante :

**Cas A — Chantier tracké.** L'utilisateur nomme un chantier précis (mot-clé
qui matche une ligne de "Ouverts"), ou demande "qu'est-ce qu'il reste à
trancher" sans préciser une fiche.

- Si un chantier précis est nommé, aller directement dessus.
- Sinon, lire `Index.md` section `Chantiers en cours::Ouverts`
  (`vault_read` avec `targetType: "heading"`, `target: "Chantiers en
  cours::Ouverts"`). **Si MCP indisponible :** lire `00_Systeme/Index.md` et
  repérer la même section. Lister les items ouverts, demander lequel traiter
  en premier.

**Cas B — Édition ad hoc.** L'utilisateur nomme directement une fiche
existante de `01_Lore` et une modification précise, sans référence à une
ligne de "Chantiers en cours" (ex. "corrige X sur la fiche Y", "ajoute ce
paragraphe à Y"). Ne pas chercher de correspondance dans Index — la demande
EST le mandat. Vérifier seulement que la fiche visée existe bien et vit dans
`01_Lore` (sinon : `creer-fiche` si elle n'existe pas encore, ou signaler
l'emplacement réel si elle est ailleurs, ex. `04_Brouillons`). En cas de
doute sur si la demande est vraiment une édition à écrire tout de suite ou
plutôt une question/exploration, demander avant d'engager la Cérémonie —
ne jamais déclencher ce skill sur une simple lecture ou discussion.

Dans les deux cas, la suite (Étapes 2 à 6) est identique — la seule
différence de traitement apparaît à l'Étape 6 (pas de ligne "Ouverts" à
cocher pour le Cas B).

Règles communes aux deux cas :

- Un seul chantier ou une seule édition ad hoc traité(e) à la fois par
  défaut. N'enchaîner sur un(e) autre que si l'utilisateur le demande
  explicitement en cours de session.
- Si le sujet couvre un grand nombre de fiches (ex. "recalibrer le rang des
  ~20 divinités"), signaler l'ampleur et proposer un découpage (par lot)
  avant de tout traiter d'un coup sans confirmation — même logique que
  audit-coherence sur "tout le vault".

## Étape 2 — Rassembler le contexte

1. Identifier la ou les fiches concernées : Cas A → wikilinks présents dans
   la ligne du chantier, ou déduites du sujet ; Cas B → la fiche nommée
   directement par l'utilisateur. Si un chantier référence une fiche
   brainstorm ou un journal d'audit ("voir [[...]]"), la lire EN ENTIER —
   c'est la matière de départ de la décision.
2. Résoudre chaque wikilink en chemin réel AVANT toute lecture ou
   écriture : un `[[Nom]]` ne porte pas de chemin, et les tools MCP exigent
   un chemin exact. Passer par `search_simple` (sur le nom) ou `vault_list`
   sur le dossier probable — jamais par un chemin construit de mémoire ou
   depuis la doc : des divergences d'accents existent entre Conventions et
   les dossiers réels (ex. `01_Lore/Évenements/`, deuxième e sans accent),
   et un chemin faux échoue silencieusement.
   **Si MCP indisponible :** CLI `obsidian read file="Nom"` (résolution
   native façon wikilink) pour lire ; pour un chemin exact (édition disque,
   git), `obsidian search query="Nom"` ou `Glob` sur le nom de fichier.
3. Lire les fiches concernées EN ENTIER (`vault_read`, sans `target` pour
   avoir le contenu complet + `frontmatter` + `links` + `backlinks`).
   **Si MCP indisponible :** CLI `read` ou `Read`. Ne jamais trancher à
   partir d'un extrait ou d'un souvenir.
4. **Obligatoire — pas seulement "si utile"** : avant de réécrire
   l'Histoire, le Résumé ou les Relations d'une fiche existante, vérifier
   ses `backlinks` (déjà renvoyés par `vault_read` à l'Étape 2.3) ET
   lancer une recherche texte sur son nom (`search_simple`) pour repérer
   les mentions non liées ; `search_query` (JsonLogic) est complémentaire
   pour cibler par `type`/`statut` si `search_simple` remonte trop de bruit.
   Lire EN ENTIER toute fiche de type `evenement` ou `objet` qui en ressort
   et qui n'a pas encore été lue cette session, même si elle ne semble pas
   centrale au premier coup d'œil. Les Relations déjà présentes sur la
   fiche ne suffisent pas : elles reflètent ce qui était su au moment de
   leur rédaction, pas le canon qui a pu s'y ajouter depuis. Un oubli ici
   crée une incohérence silencieuse, découverte seulement si l'utilisateur
   la remarque lui-même — expérience vécue (fiche Naphusis, 2026-07-28 :
   deux événements canon déjà établis, passés inaperçus jusqu'à ce que
   l'utilisateur signale leur absence de l'Histoire).
   ⚠️ Le mapping d'outils ci-dessus (`search_simple`/`search_query`) a été
   corrigé le 2026-08-07 contre le serveur MCP réel — l'ancienne version
   référençait `obsidian_search_notes` avec une pagination (`pathPrefix`,
   `nextCursor`) qui n'existe pas dans les outils actuels. Si une session
   future constate que `search_simple` ne remonte pas tous les résultats
   sur un vault volumineux, le signaler : ce point n'a pas été vérifié à
   l'échelle, seul le mapping de noms l'a été.
   **Si MCP indisponible :** CLI `obsidian backlinks file="Nom"` et
   `obsidian search query="Nom"`, ou `Grep`/`Glob` sur `01_Lore/`.

## Étape 3 — Trancher ensemble (jamais de yes-man)

Même discipline que le Mode A de `brainstorm-lore` : présenter les pistes
concurrentes s'il y en a, tester chacune contre l'exploitabilité et les
contradictions déjà connues, donner au moins un contre-argument même pour
une piste qui semble bonne. **"Retenu" = validé explicitement par
l'utilisateur dans l'échange** — jamais tranché seul par Claude, jamais par
défaut ni par enthousiasme.

Si le chantier (ou l'édition ad hoc — ex. une correction ponctuelle déjà
sans ambiguïté) n'est qu'une confirmation simple déjà bien cadrée, aller
plus vite — mais ne jamais sauter la validation explicite avant d'écrire
quoi que ce soit. Aller vite ne veut jamais dire sauter une étape de la
Cérémonie (Étapes 0, 2.4, 4bis, 5) : décision actée le 2026-08-07, voir
intro.

À l'inverse, si le sujet s'avère être une question encore largement ouverte
(plusieurs pistes lourdes, beaucoup de non-tranché après discussion),
proposer de basculer vers une vraie session `brainstorm-lore` — fiche
déposée en Inbox, chantier laissé ouvert (ou, pour une édition ad hoc,
simplement non traitée pour l'instant) — plutôt que de forcer une décision
pour pouvoir cocher la case. Un sujet qui reste ouvert honnêtement vaut
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

1. Vérifier le `statut` actuel — déjà connu depuis la lecture complète de
   l'Étape 2.3 (`vault_read` renvoie `frontmatter.statut` directement, pas
   besoin d'un second appel). S'il est `canon` ou `canon-verrouillé`, le
   signaler explicitement avant d'écrire (Conventions §1 : modifiable, mais
   vérifier les notes liées avant) — notes liées déjà rassemblées à l'Étape
   2, point 4 (`backlinks` + `search_simple`). Ne jamais s'arrêter d'écrire
   pour autant si l'utilisateur a validé la décision, juste rendre visible
   ce qui dépend de la fiche.
2. Vérifier si un marqueur `revision:` existe déjà (`frontmatter.revision`,
   même lecture). S'il porte une valeur différente de `ia-a-valider` (ou si
   sa présence suggère une révision antérieure pas encore validée), le
   signaler à l'utilisateur avant d'écraser plutôt que de l'effacer
   silencieusement.
3. Poser le double marqueur :
   - Frontmatter : `vault_patch` avec `targetType: "frontmatter"`,
     `target: "revision"`, `operation: "replace"`, `content:
     "ia-a-valider"`, `createTargetIfMissing: true` — puis un second appel
     identique pour `target: "revision-date"`, `content: "AAAA-MM-JJ"`
     (date du jour). **Si MCP indisponible :** CLI `obsidian
     property:set` (deux appels), sinon édition YAML via `Edit`.
   - Callout + contenu + block ID dans le MÊME appel : un seul
     `vault_patch` (`targetType: "heading"`, `target:` la section
     concernée en syntaxe `Parent::Child`, `operation: "append"`) — ou
     `vault_append` si aucune section précise ne convient (ajout en fin de
     fichier uniquement) — dont le contenu est le bloc complet de la
     « Forme du marqueur » ci-dessus. Jamais d'appels séparés pour le
     callout, le texte et le block ID : disjoints, ils se retrouveraient
     éparpillés dans la fiche. **Si MCP indisponible :** un seul `Edit`
     insérant le bloc complet au bon endroit (le CLI `append` ne cible pas
     une section — ne l'utiliser que si l'ajout va légitimement en fin de
     fiche).
   - Cibler la section par sa syntaxe exacte : `vault_get_document_map`
     donne le catalogue des headings, block IDs et clés frontmatter réels
     et la forme `Parent::Child` à utiliser — ne pas deviner le nom d'une
     section ; un heading bare sans le chemin imbriqué complet échoue
     silencieusement.
   - Retries — **poser explicitement `rejectIfContentPreexists: true`** sur
     l'appel `vault_patch` du callout : contrairement à ce qu'un ancien
     texte de ce skill supposait, ce paramètre défaut à `false` (donc à
     AUCUNE protection anti-duplication tant qu'il n'est pas posé
     explicitement). Un échec avec `rejectIfContentPreexists: true` après
     une coupure signifie que l'écriture a probablement déjà réussi —
     relire la fiche avant de forcer un nouvel essai, jamais retenter sans
     ce paramètre.
   - Si le callout cible une section contenant des références de block ID
     existantes, ou si la fiche a déjà reçu plusieurs révisions le même
     jour : préférer une reconstruction complète (`vault_write`, contenu
     entier relu puis fusionné) à un `append`/`replace` partiel — un
     `vault_patch` sur une section porteuse de block IDs peut supprimer du
     contenu existant sans le signaler.
   - **Vérification post-écriture, systématique, chaque appel** : `vault_write`
     a déjà été observé retourner un succès sans persister réellement le
     contenu. Après CHAQUE écriture (frontmatter, callout, ou fusion
     complète), relire la fiche (`vault_read`) et confirmer que le
     contenu attendu y figure avant de passer à la fiche suivante ou de
     déclarer l'Étape 4 terminée pour cette fiche — ne jamais présenter une
     écriture comme réussie sur la seule foi du retour de l'appel.
4. Écriture **additive par défaut** : ajouter sans réécrire ni supprimer la
   prose existante, sauf demande explicite de l'utilisateur dans la
   conversation en cours. Ne jamais utiliser `vault_write` en pleine page
   sur une fiche existante à cette étape, sauf dans le cas de
   reconstruction complète prévu au point 3 ci-dessus (et alors seulement
   après avoir relu et fusionné explicitement le contenu existant).
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

1. Chercher `05_IA_Inbox/Update - Timeline Master.md` (`vault_list` sur
   `05_IA_Inbox/` — confirmer l'existence ou l'absence AVANT toute écriture :
   `vault_write` n'a pas de paramètre de protection, il écrase sans
   avertissement que le fichier existe déjà ou non).
2. **S'il n'existe pas** : le créer comme copie conforme intégrale de
   `Timeline Master` (lire l'original en entier, puis `vault_write` avec ce
   contenu sur le nouveau fichier). Relire ensuite (`vault_read`) pour
   confirmer la persistance avant de continuer.
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
si une Base filtrant les révisions existe déjà (`search_simple` sur
`revision`, ou demander à l'utilisateur — c'est plus fiable). Si non,
proposer de déposer dans `05_IA_Inbox` une copie du fichier fourni avec ce
skill, `assets/Revisions en attente.base` — vérifier d'abord via
`vault_list` que rien n'existe déjà à ce chemin (`vault_write` écrase sans
avertissement), puis `vault_write` avec son contenu (**si MCP
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
- Rappel explicite : rien n'est validé tant que `ia-a-valider` reste posé —
  la validation de l'utilisateur = suppression du marqueur (frontmatter
  `revision` ET `revision-date` ET callout) + commit (`Regles_IA_Lore`).
  Si la Base est en place, la fiche disparaît de « Revisions en attente »
  dès que `revision` est retiré — c'est le témoin de validation.

Le texte à coller soi-même dans Index dépend de l'origine (Étape 1) :

**Cas A — Chantier tracké** : donner les deux lignes, comme avant.
- La ligne "Ouverts" concernée, à cocher.
- La ligne à ajouter sous "Tranchés" :
  `- [x] <résumé de la décision> (<fiche(s) concernée(s)>, <date>)` — ce
  format exact fait foi ; les entrées historiques de "Tranchés" sont
  hétérogènes, ne pas les imiter.

**Cas B — Édition ad hoc** : pas de ligne "Ouverts" (il n'y en avait pas).
Pour la ligne "Tranchés", décision actée le 2026-08-07 : la fournir
**seulement si la modification est significative**. Heuristique proposée
(à affiner à l'usage — signaler tout cas limite plutôt que trancher seul) :

- **Significatif** → fournir la ligne Tranchés : la modification change ce
  que le canon affirme — fait nouveau, changement de Relations, arbitrage
  d'une contradiction, tout contenu qui pourrait plus tard être cité comme
  "le canon dit que...".
- **Mineur** → pas de ligne Tranchés : correction cosmétique ou formelle
  qui ne change pas le sens — typo, syntaxe d'un wikilink, reformulation
  sans changement de fond, ajout d'un lien vers une entité déjà établie
  ailleurs sur la fiche.
- **Cas limite** → proposer la ligne quand même et laisser l'utilisateur
  décider de la garder, plutôt que trancher silencieusement dans un sens ou
  l'autre — cohérent avec le "jamais yes-man" du skill : une omission
  injustifiée est aussi une décision prise à la place de l'utilisateur
  qu'un ajout superflu.

Dans les deux cas, le double marqueur (`ia-a-valider` + callout + block ID)
est posé de façon identique — la distinction Cas A/B ne joue que sur le
texte à reporter dans Index, jamais sur la rigueur de l'écriture elle-même.

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
- Jamais déclencher ce skill sur une simple lecture, discussion ou question
  au sujet d'une fiche existante — seulement sur une demande explicite de
  modification (Cas B, Étape 1). Une hésitation sur l'intention se
  clarifie en la demandant, jamais en présumant l'intention d'écrire.
- Jamais sauter une étape de la Cérémonie (backlinks, cas Timeline Master,
  Base, Journal) pour une édition ad hoc au motif qu'elle "semble" mineure
  — décision actée le 2026-08-07 : même rigueur quelle que soit l'origine.
  Seule la ligne "Tranchés" de l'Étape 6 varie selon significativité.
- Jamais présenter une écriture comme réussie sur la seule foi du retour
  d'un appel `vault_write`/`vault_patch` — toujours relire la fiche
  ensuite pour confirmer la persistance réelle (Étape 4, point 3).
- Jamais poser `rejectIfContentPreexists` implicite : ce paramètre défaut
  à `false` (aucune protection) — le poser explicitement à `true` sur tout
  `vault_patch` de callout, ne jamais compter sur un comportement par
  défaut supposé.

---

## Journal des modifications de ce skill

- 2026-08-07 : extension du périmètre — le skill couvre désormais aussi
  l'édition ad hoc d'une fiche existante hors chantier tracké (Cas B,
  Étape 1 et 6), toujours via la Cérémonie complète, sans palier allégé
  (décision explicite : pas de skill séparé pour ce cas). Correction du
  mapping d'outils, obsolète depuis un renommage du serveur MCP non
  répercuté ici : `obsidian_get_note` → `vault_read`, `obsidian_search_notes`
  → `search_simple`/`search_query`, `obsidian_list_notes` → `vault_list`,
  `obsidian_manage_frontmatter` → `vault_patch` (`targetType: frontmatter`),
  `obsidian_patch_note` → `vault_patch`, `obsidian_append_to_note` →
  `vault_append`, `obsidian_write_note` → `vault_write`,
  `obsidian_get_note format: document-map` → `vault_get_document_map`.
  Correction du paramètre anti-duplication supposé par défaut
  (`applyIfContentPreexists`, inexistant) vers le vrai paramètre
  (`rejectIfContentPreexists`, défaut `false` — à poser explicitement).
  Ajout d'une vérification de persistance obligatoire après chaque écriture
  (`vault_write` a déjà été observé retourner un succès sans persister).
  Le mapping a été vérifié contre les tools réellement exposés en session ;
  la mécanique de pagination de recherche décrite dans l'ancienne version
  (`pathPrefix`/`nextCursor`) n'a pas d'équivalent connu dans les tools
  actuels et n'a pas pu être vérifiée à l'échelle — à surveiller.
