---
name: audit-coherence
description: Audite la cohérence d'une fiche, d'un dossier/type ou d'une zone du vault Lamia — contradictions avec le canon, doublons, conflits de timeline, zones floues — et dépose un journal d'audit dans 05_IA_Inbox/Audits/. Utilise ce skill UNIQUEMENT sur demande explicite ("audite X", "vérifie la cohérence de Y", "est-ce que X contredit autre chose dans le vault", "check les doublons sur Z", "y a-t-il des zones floues dans W") — jamais de façon proactive après un simple ajout ou une simple modification. Ne pas confondre avec migrer-fiche (qui fait sa propre mini-vérification, mais uniquement pour une fiche en cours de migration depuis 99_Archive) ni avec brainstorm-lore (exploration créative, pas audit de l'existant).
compatibility: Fonctionne avec le MCP obsidian-mcp-server connecté au vault Lamia (obsidian_search_notes, obsidian_get_note, obsidian_list_notes, obsidian_write_note, obsidian_list_tags). En Claude Code, si ce MCP est absent, bascule sur un accès disque direct (Read/Write/Glob/Grep/Bash) et git — voir "Deux modes d'accès au vault".
---

# Auditer la cohérence — Lamia

Ce skill audite une cible (fiche, dossier, type d'entité) contre le reste du
vault selon 4 axes : contradictions, doublons, conflits de timeline, zones
floues. Il **ne modifie jamais la ou les fiches auditées** — lecture seule
sur les cibles, écriture uniquement dans un nouveau fichier journal déposé
dans `05_IA_Inbox/Audits/`. Il ne tranche jamais une incohérence lui-même :
il la signale, l'utilisateur arbitre.

## Deux modes d'accès au vault

Ce skill dépend normalement du MCP `obsidian-mcp-server`. Deux cas de figure :

- **Mode MCP (par défaut)** : les tools `obsidian_get_note`,
  `obsidian_search_notes`, `obsidian_write_note`, `obsidian_list_notes`,
  `obsidian_list_tags` sont disponibles → comportement décrit plus bas,
  inchangé.
- **Mode Fichiers/Git (Claude Code uniquement)** : si ces tools sont absents,
  ou si l'un d'eux échoue en cours de session, ET que Claude a un accès
  disque direct au vault (racine du repo git courant). Chaque étape MCP a son
  équivalent Fichiers, indiqué par « **Si MCP indisponible :** ». Il n'existe
  pas d'équivalent disque direct à `obsidian_list_tags` : en son absence,
  s'appuyer uniquement sur `Grep`/recherche texte pour le cross-référencement.

⚠️ Ce mode de repli n'existe QUE là où un accès disque réel au vault est
possible. Dans claude.ai, un échec MCP doit être signalé à l'utilisateur et
la tâche interrompue — jamais improvisé.

## Étape 0 — Contexte (une fois par session, si pas déjà fait)

Charger `00_Systeme/Conventions.md` et `00_Systeme/Index.md` s'ils ne sont
pas déjà dans le contexte (`obsidian_get_note`, **si MCP indisponible :**
`Read`). La notation §5 (`⚠️` incohérence en attente d'arbitrage, `≈`
approximatif, `?` inconnu ordonné, `(rumeur)`, `🔒` secret) est le vocabulaire
de sortie de ce skill — l'utiliser tel quel dans le rapport et le journal.

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

Si la cible nommée est ambiguë (plusieurs fiches possibles), lister les
candidats et demander laquelle avant de continuer.

## Étape 2 — Rassembler le contexte

1. Lire la ou les fiches cibles EN ENTIER (`obsidian_get_note`, format
   content). **Si MCP indisponible :** `Read`. Ne jamais auditer à partir
   d'un extrait.
2. Repérer les entités, concepts et dates référencés dans la cible.
3. Chercher les fiches qui mentionnent ces mêmes entités/concepts
   (`obsidian_search_notes`, `pathPrefix: "01_Lore"`), et croiser avec
   `obsidian_list_tags` pour repérer d'autres fiches partageant les mêmes
   tags (angle de recherche complémentaire au texte plein, utile pour les
   doublons de rôle qui n'utilisent pas forcément le même vocabulaire).
   **Si MCP indisponible :** `Grep`/`Glob` sur `01_Lore/`.
4. Si la cible contient des éléments datés : charger
   `01_Lore/Timeline Master.md` EN ENTIER (jamais de mémoire).
   **Si MCP indisponible :** `Read` ce fichier en entier.
5. Lire réellement les fiches candidates trouvées à l'étape 3 — jamais
   travailler sur un titre ou un extrait de recherche seul.

## Étape 3 — Analyser selon les 4 axes

Pour chaque axe, ne signaler QUE ce qui a été réellement vérifié à l'Étape 2
— jamais une supposition présentée comme un constat.

1. **Contradictions avec le canon** : faits incompatibles entre la cible et
   une autre fiche déjà dans `01_Lore` (dates, relations, événements,
   attributs). Citer les deux fiches et les passages précis en tension.
2. **Doublons** : deux entités qui semblent remplir le même rôle narratif,
   ou deux fiches dont le contenu se recoupe fortement au point de
   constituer un doublon plutôt que deux entités distinctes. Distinguer les
   deux cas dans le rapport (doublon de rôle vs doublon de contenu).
3. **Conflits de timeline** : incompatibilité entre la datation de la cible
   (`ere`/`annee` en frontmatter, ou dates dans le corps) et
   [[Timeline Master]] ou une autre fiche datée.
4. **Zones floues** : ambiguïtés, informations manquantes, ou questions non
   tranchées repérées pendant l'analyse — même si elles ne sont ni
   contradiction ni doublon à proprement parler.

Ne jamais arbitrer un constat : le signaler avec la notation `⚠️` (Conventions
§5), jamais le résoudre à la place de l'utilisateur.

## Étape 4 — Présenter le rapport en conversation

Structurer par les 4 axes ci-dessus. Chaque constat cite les fiches
concernées en wikilinks. Si un axe n'a rien à signaler, le dire brièvement
plutôt que de l'omettre silencieusement (pour que l'absence de constat soit
distinguable d'un audit non fait).

## Étape 5 — Déposer le journal

Nom de fichier : `AAAA-MM-JJ — Audit — [Cible].md` (cible = nom de la fiche,
ou nom du dossier/type si périmètre élargi). Contenu formaté en cases à
cocher, prêt à être collé dans la section "Chantiers en cours" de `Index`
(Conventions §8) :

```markdown
---
statut: brouillon
source: ia
tags: [audit-coherence]
cible: "<fiche ou périmètre audité>"
date: <AAAA-MM-JJ>
---
# <nom du fichier sans extension>

**En une phrase :** <résumé du résultat — ex. "2 contradictions, 1 doublon de rôle, 0 conflit de timeline, 3 zones floues sur [[Cible]]">

## Contradictions avec le canon
- [ ] ⚠️ <constat, fiches citées en wikilinks>

## Doublons
- [ ] ⚠️ <constat>

## Conflits de timeline
- [ ] ⚠️ <constat>

## Zones floues
- [ ] ⚠️ <constat>
```

Omettre les sections sans aucun constat plutôt que d'y laisser une case
vide trompeuse. Écrire dans `05_IA_Inbox/Audits/` via `obsidian_write_note`
(`overwrite: false`).

**Si MCP indisponible :** `Write` au même chemin. Puis, seulement si le vault
est un dépôt git (`git rev-parse --is-inside-work-tree`) :
```bash
git add "05_IA_Inbox/Audits/<fichier>.md"
git commit -m "[brouillon IA] Audit — <Cible>" -- "05_IA_Inbox/Audits/<fichier>.md"
```
Ne JAMAIS `git add -A`/`git add .`/`git commit -a` : uniquement ce fichier.

Confirmer à l'utilisateur : chemin du journal (+ commit s'il a eu lieu), et
rappel que rien n'est arbitré — c'est à lui de trancher chaque point, puis
de reporter ce qu'il retient dans les Chantiers de `Index` (verrouillé pour
l'IA) et, le cas échéant, de corriger les fiches concernées lui-même.

## Garde-fous

- Jamais modifier la ou les fiches auditées — ni leur statut, ni leur
  section "Contradictions potentielles" (le §4 des Conventions dit qu'elle
  est vidée "après arbitrage" : l'arbitrage est le geste de l'utilisateur,
  pas de ce skill). Seule écriture autorisée : le nouveau fichier journal.
- Jamais arbitrer un constat — le signaler avec `⚠️`, ne jamais le résoudre.
- Jamais inventer une contradiction ou un doublon non réellement vérifié à
  l'Étape 2 — mieux vaut sous-signaler que fabriquer un constat.
- Sur une demande d'audit très large ("tout le vault") sans précision,
  prévenir du coût et proposer un découpage avant de lancer quoi que ce
  soit d'exhaustif.
- En Mode Fichiers/Git : ne jamais `git add`/`git commit` autre chose que le
  fichier journal créé.
- Si un tool MCP échoue en cours de session, basculer en Mode Fichiers/Git
  UNIQUEMENT si un accès disque réel existe ; sinon, arrêter et signaler
  l'échec — jamais fabriquer un succès.
