---
type: systeme
date: 2026-07-10
---
# Tableau de bord

> Détecteur de dérive. Nécessite le plugin **Dataview**.
> Idéal : toutes les sections vides. Ce qui s'affiche ici demande une action.
> Revue : une fois par mois ou après toute grosse session.

## 🚨 Notes de lore sans statut

```dataview
TABLE type, file.folder AS "Dossier"
FROM "01_Lore"
WHERE !statut
```

## 🔗 Notes orphelines (aucun lien entrant)

```dataview
LIST
FROM "01_Lore"
WHERE length(file.inlinks) = 0
```

## 🕰️ Brouillons de plus de 30 jours

```dataview
TABLE type, date, file.folder AS "Dossier"
FROM "01_Lore" OR "04_Brouillons"
WHERE statut = "brouillon" AND date AND (date(today) - date) >= dur(30 days)
SORT date ASC
```

## ⚖️ Divinités sans rang

```dataview
LIST
FROM "01_Lore/Divinités"
WHERE !rang
```

## 📅 Notes datées incomplètes (année sans ère, ou l'inverse)

```dataview
LIST
FROM "01_Lore"
WHERE (annee AND !ere) OR (ere AND !annee)
```

## 🏗️ Chantiers en cours (depuis l'Index)

```dataview
TASK
FROM "00_Systeme"
WHERE !completed
```

## 📝 Dernières notes modifiées

```dataview
TABLE file.mtime AS "Modifié", statut
FROM "01_Lore"
SORT file.mtime DESC
LIMIT 10
```
