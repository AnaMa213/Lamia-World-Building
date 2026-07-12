---
type: systeme
date: 2026-07-11
version: "1.2"
---
# Conventions du vault

> Source de vérité sur le fonctionnement du vault. En cas de doute, ce fichier prime.
> Objectif : bibliothèque universelle de l'univers de Lamia, interrogeable par moi
> et par l'IA, sans perte ni incohérence.

## 1. Statuts (`statut:` obligatoire dans chaque note de lore)

| Statut | Définition | Règle de modification |
|---|---|---|
| canon-verrouillé | Vrai ET utilisé dans une œuvre finalisée/publiée. | Quasi intouchable. Audit d'impact obligatoire. |
| canon | Vrai dans l'univers. Validé par moi explicitement. | Modifiable, mais vérifier les notes liées avant. |
| semi-canon | Probablement vrai, pas encore verrouillé. | Librement modifiable. |
| brouillon | Idée en cours. N'engage rien. | Librement modifiable. |
| rumeur | Ce que les habitants croient. Peut être faux. | Librement modifiable. |
| secret | Canoniquement vrai, mais non révélé (lecteurs/joueurs). | Comme canon. |
| obsolète | Abandonné. Ne fait plus foi. | Indiquer pourquoi et par quoi c'est remplacé. |

- Note sans `statut:` = traitée comme **brouillon**, et à corriger.
- Seul moi attribue `canon` et `canon-verrouillé`. Jamais l'IA.
- Passage en `canon-verrouillé` : uniquement quand un roman/scénario finalisé s'appuie dessus.

## 2. Types d'entités (`type:`, liste fermée)

`divinite` · `personnage` · `peuple` · `faction` · `lieu` · `creature`
· `magie` · `objet` · `ere` · `evenement` · `legende` · `concept` · `oeuvre` · `systeme`

- **evenement** = fait daté de l'histoire de l'univers. Modèle hybride :
  [[Timeline Master]] est le registre maître de TOUS les événements ; seuls
  les événements MAJEURS reçoivent en plus leur propre note `evenement`.
  Toute note evenement DOIT figurer dans Timeline Master.
- **legende** = un récit qui circule DANS l'univers. La fiche peut être
  `statut: canon` (la légende existe) tout en racontant des choses fausses.
  Indiquer : part vraie / part fausse / origine du récit.
- **concept** = élément culturel ou systémique : calendrier, monnaie, langue,
  coutume, rite.
- **ere** = période historique. Détail dans sa fiche, ordre et dates dans
  [[Timeline Master]].
- Ajouter un nouveau type = modifier CE fichier d'abord.

## 3. Frontmatter type

```yaml
---
statut: brouillon
type: divinite
tags: []
date: 2026-07-11
portee:            # vide = canon-univers ; sinon nom de l'œuvre
aliases: []        # autres noms/titres, pour la recherche et les liens
ere:               # primordial | serenale | exodiale | voile — si la note est datée
annee:             # nombre seul, dans le compte de l'ère
---
```

Champs additionnels par type (optionnels sauf mention) :
- **divinite** : `rang` (primordiale | majeure | mineure | demi-dieu | esprit — OBLIGATOIRE),
  `etat` (active | voilée | bannie | morte | inconnue), `titres`,
  `suivants` (fidèles les plus courants : peuples, ordres — en wikilinks),
  `alignement` (optionnel, usage JDR)
- **personnage** : `naissance` / `mort` (format court "AAAA È.V." ; inconnu
  explicite si besoin), `etat` (vivant | mort | disparu | inconnu),
  `pov` (liste des œuvres où le personnage est point de vue)
- **lieu** : `continent`, `region` (lien vers le lieu parent)
- **ere** : `annee_debut`, `annee_fin` (ou `inconnu` — jamais vide)
- **evenement** : `importance` (majeur | mineur — OBLIGATOIRE), `ere`,
  `annee` ou `annee_debut`/`annee_fin`
- **oeuvre** : `type_oeuvre` (roman / scenario-jdr), `etat` (en cours / finalisé)

Propriété héritée supprimée : `statut_lore` → remplacée par `statut`.

## 4. Structure des fiches (corps de note)

Toute note de lore commence par :
**En une phrase :** (résumé d'une ligne — obligatoire).

Fiche divinité et personnage (sections, dans cet ordre) :
Résumé / Histoire / Apparence / Désir conscient / Besoin profond /
Croyance fausse / Faille intime / Relations / Contradictions potentielles

- Les quatre sections psychologiques (Désir → Faille) sont FACULTATIVES pour
  les entités mineures. Une fiche courte finie vaut mieux qu'une fiche
  complète abandonnée.
- Relations : wikilinks avec la nature du lien.
- Contradictions potentielles : rempli à la création, vidé après arbitrage.

**Règle une-entité-une-note :** si une note couvre deux entités ou deux
portées, on scinde.

**Géographie et ères :** la topologie du monde varie selon les ères.
Règle : UNE note par lieu, avec une section "À travers les ères"
(Sérénale / Exodiale / Voile). Pas de note séparée par version d'ère.

## 5. Datation et chronologie

### Périodes et durées (calendrier lamien — création des peuples de Lamia)
| Période | Bornes | Durée |
|---|---|---|
| Temps primordiaux | avant Sérénale 0 — origines cosmiques | non datée en ères lamiennes |
| Ère Sérénale | 0 (premiers peuples lamiens) → ≈ 2950 (démons sur Lamia) | ≈ 2950 ans |
| Ère Exodiale | 0 (= Sérénale ≈ 2950) → ≈ 1600 (fin de la Grande Guerre divine) | ≈ 1600 ans |
| Ère du Voile (È.V.) | 0 (= Exodiale ≈ 1600) → aujourd'hui | **présent : 1448 È.V.** |

- Chaque ère compte en années **croissantes depuis son an 0**. Un changement
  d'ère = rupture historique majeure vécue par les Lamiens.
- Les durées sont approximatives (≈) y compris pour moi, l'auteur ; les
  habitants n'en ont qu'une idée vague.
- `ere: primordial` est une valeur technique de frontmatter : in-universe,
  les Temps primordiaux ne sont PAS une ère lamienne.
- ⚠️ Orthographe provisoire : « Sérénale » (→ chantier ouvert).

### Datation dans les frontmatters (simple, obligatoire pour toute note datée)
`ere:` (primordial | serenale | exodiale | voile) + `annee:` (nombre seul).
- Plage : `annee_debut:` / `annee_fin:`.
- Année inconnue : `annee: inconnu` — jamais vide.

### Notation des incertitudes (Timeline et fiches)
`≈` approximatif · `?` inconnu mais ordonné · `(rumeur)` la date crue par les
habitants diffère de la vraie · `🔒` entrée secrète, ne fuite JAMAIS vers
lecteurs/joueurs · `⚠️` incohérence en attente d'arbitrage (→ Chantiers).
Symboles définis ici et utilisés partout à l'identique.

### Modèle de timelines (hybride, multi-niveaux)
- [[Timeline Master]] = registre maître manuel, échelle de l'ANNÉE, tous les
  événements canoniques de l'univers, y compris secrets (🔒).
- Les événements MAJEURS peuvent en plus avoir leur note `evenement`
  (auto-listées dans Timeline Master via Dataview).
- Chaque œuvre a SA timeline (`portee:` œuvre) : échelle fine, au jour près
  (format complet `JJ Mois AAAA È.V.`), avec ses propres entrées secrètes.
- Timeline Master ne descend jamais au jour près, sauf exception justifiée.

### Format complet (corps des textes et timelines d'œuvres)
`JJ Mois AAAA È.V.` — ex. **20 Thanèse 1448 È.V.**

### Structure de l'année (Calendrier Commun de Lamia)
365 jours = 12 mois de 30 jours + les **Cinq du Voile** (hors-mois, entre
Atarien et Albarée). 1 mois = 5 sixaines de 6 jours.
Détail : [[Calendrier Commun de Lamia]].

### Règles
- Tout événement daté canonique figure dans [[Timeline Master]].
- Toute note datée lie [[Timeline Master]] ou la fiche d'ère concernée.

## 6. Nommage des fichiers

- Espaces et accents autorisés : `Ordre du Cercle Brisé.md`.
- Pas d'article initial — l'article va dans `aliases`.
- Homonymes : suffixe entre parenthèses avec le type :
  `Kael (lieu).md` / `Kael (personnage).md`. Le nom nu devient alias des deux.
  S'applique aussi aux œuvres : `Le Monde de Lamia (roman)`.

## 7. Arborescence

```
00_Systeme/        conventions, index, règles IA, tableau de bord, Templates/
01_Lore/           le canon-univers (+ Timeline Master.md à la racine)
  Divinités/  Personnages/  Peuples/  Factions/  Lieux/
  Créatures/  Magies/  Objets/  Ères/  Événements/  Légendes/  Concepts/
02_Romans/         un sous-dossier par roman (notes à portee:)
03_Scenarios_JDR/  un sous-dossier par scénario/campagne
04_Brouillons/     capture rapide, tout est statut: brouillon
05_IA_Inbox/       inbox des propositions de l'IA à valider par un humain 
99_Archive/        ancien vault en cours de migration (lecture seule)
```

## 8. Liens et navigabilité (règle anti-oubli)

- Toute nouvelle note formatée doit : (1) contenir au moins un wikilink vers
  une entité existante, (2) être ajoutée à la MOC de son type.
- Une note orpheline (hors 04_Brouillons) est un bug, pas une exception.
- Zones floues et décisions en attente : section "Chantiers en cours" de
  [[Index]], sous forme de cases à cocher (interrogeables par Dataview).

## 9. Flux de capture (protéger la créativité)

- Pendant une session d'écriture ou de brainstorm : une idée = une note dans
  `04_Brouillons` avec juste `statut: brouillon` et une ligne de contenu.
- JAMAIS de formatage complet à la capture. Le formatage se fait au tri.
- 04_Brouillons est la seule zone où les règles du §8 ne s'appliquent pas.

## 10. Revue périodique (protéger contre l'oubli)

- [[Tableau de bord]] (Dataview) affiche en continu : notes sans statut,
  notes orphelines, brouillons de plus de 30 jours, divinités sans rang,
  notes datées incomplètes, chantiers ouverts.
- Passage en revue : une fois par mois, ou après toute grosse session.

## 11. Migration de l'ancien vault

- Tout l'existant part dans `99_Archive/` tel quel (rien n'est supprimé).
- Chaque fiche migrée vers `01_Lore/` est reprise au nouveau format et reçoit
  `statut: brouillon` par défaut — je revalide moi-même en semi-canon ou
  canon à la relecture. Aucune promotion automatique.
- Exception : un document rédigé par moi avec des statuts explicites
  (ex. chronologie taguée [CANON]) conserve ses statuts — le tag vaut
  validation.
- Une note archivée déjà migrée reçoit en tête : `> Migré vers [[X]]`.

---

## Journal des versions
- 1.2 (2026-07-11) : réintroduction du type `evenement` (modèle hybride de
  timelines), valeur `ere: primordial` (Temps primordiaux), durées et sens du
  compte des ères, notation ≈ / ? / (rumeur) / 🔒 / ⚠️, timelines par œuvre,
  dossier Événements/, orthographe provisoire « Sérénale », exception de
  migration pour documents auto-tagués.
- 1.1 (2026-07-10) : ajout `rang` + `etat` (divinités), champs de continuité
  personnages, `continent` (lieux), règle "À travers les ères", homonymie
  des œuvres.
- 1.0 (2026-07-10) : version initiale consolidée.
