# Échantillonnage de style — protocole et grille

À lire avant de produire une fiche de style. Objectif : transformer un
échantillon de texte en un référentiel **réutilisable**, assez précis pour
guider une réécriture et assez court pour être relu d'un coup d'œil.

## Sommaire

1. [Ce qu'est une bonne fiche de style](#1-ce-quest-une-bonne-fiche-de-style)
2. [Protocole d'échantillonnage](#2-protocole-déchantillonnage)
3. [Mesurer avant d'interpréter](#3-mesurer-avant-dinterpréter)
4. [La grille en 9 dimensions](#4-la-grille-en-9-dimensions)
5. [Les contre-exemples](#5-les-contre-exemples)
6. [Pièges](#6-pièges)
7. [Utiliser la fiche pour réécrire](#7-utiliser-la-fiche-pour-réécrire)

---

## 1. Ce qu'est une bonne fiche de style

Une fiche de style utile est **opérationnelle** : chaque ligne doit permettre de
décider quelque chose au moment d'écrire une phrase. Comparer :

- Inutile : « style immersif et poétique, riche en images ».
- Utile : « phrases de 8 à 45 mots, médiane 19, forte variance ; les passages
  d'action descendent sous 10. Une image pour environ 120 mots, domaines
  sources presque toujours minéraux ou organiques, jamais mécaniques. Pas de
  point-virgule. Incises réduites à *dit-il* dans 90 % des cas. »

Le test : si un autre rédacteur pouvait produire un pastiche crédible en lisant
seulement la fiche, elle est bonne.

---

## 2. Protocole d'échantillonnage

**Volume.** 1 500 à 3 000 mots minimum. En dessous, les indicateurs
quantitatifs sont du bruit — la longueur moyenne de phrase sur 300 mots ne
prédit rien.

**Variété.** C'est le critère le plus important, et le plus souvent négligé. Il
faut du **dialogue**, de la **description**, de l'**action** et de
l'**intériorité**. Raison : presque toutes les mesures de style dépendent du
type de passage. Un profil construit sur une seule scène descriptive produira
des dialogues sur-décrits et des scènes d'action alourdies. Si l'échantillon
est homogène, dis-le et demande un complément plutôt que de produire un profil
faussement solide.

**Provenance.** Trois cas, à traiter différemment :

| Source | Ce qu'on cherche | Précaution |
|---|---|---|
| Textes de l'auteur (vault) | figer sa patte pour ne pas la lisser | prendre des passages qu'il considère réussis, pas le premier chapitre venu — lui demander lesquels |
| Texte collé en conversation | un style visé ponctuel | vérifier volume et variété avant d'analyser |
| Auteur publié | procédés à emprunter | citations courtes uniquement (≈25 mots max), créditées auteur + œuvre ; la fiche décrit des procédés, elle ne stocke pas de corpus |

**Segmentation.** Si l'échantillon mélange des registres très différents (un
prologue lyrique et une scène de bataille), analyser séparément et noter la
variation dans la fiche : le style d'un auteur n'est pas un point, c'est une
amplitude.

---

## 3. Mesurer avant d'interpréter

Écrire l'échantillon dans un fichier et lancer :

```bash
python3 scripts/analyse_style.py echantillon.md
```

Le script rend : longueurs de phrase (moyenne, médiane, écart-type, extrêmes,
proportion de phrases très courtes / très longues), longueurs de paragraphe,
ponctuation pour 1 000 mots, ratio de dialogue, richesse lexicale et hapax,
densité d'adverbes en *-ment*, indices de temps verbaux (imparfait vs passé
simple vs présent), densité d'incises, mots pleins les plus fréquents.

Deux usages :

- **Calibrer la description.** Empêche d'écrire « phrases courtes et nerveuses »
  quand la médiane est à 24 mots. La perception d'un style est très peu fiable ;
  les chiffres tranchent les cas où l'intuition dérape.
- **Contrôler une réécriture.** `--compare` met les deux profils côte à côte et
  signale les écarts marqués :

```bash
python3 scripts/analyse_style.py variante.md --compare reference.md
```

Ce sont des **indicateurs, pas un verdict**. Un texte peut coller sur tous les
chiffres et sonner faux ; les chiffres ne mesurent ni le sous-texte, ni le
choix des détails, ni ce que l'auteur décide de taire. Ils servent à éliminer
les erreurs grossières, pas à valider une prose. Ne jamais présenter la sortie
brute du script à l'auteur comme si c'était l'analyse : elle est l'entrée du
travail, pas la sortie.

---

## 4. La grille en 9 dimensions

Renseigner chaque dimension avec des observables, et un exemple tiré de
l'échantillon quand c'est éclairant.

**1. Phrase.** Longueur (moyenne, médiane, amplitude) et surtout **variance**.
Parataxe (juxtaposition, coordination) contre hypotaxe (subordination
enchâssée). Position du verbe, fréquence des inversions. Phrases nominales,
fragments. Où les phrases longues apparaissent-elles — description, ou
intériorité ?

**2. Paragraphe et blanc.** Longueur des paragraphes, présence de paragraphes
d'une seule ligne (effet de coup), usage des sauts de section, tirets de
séparation. Le blanc typographique est un élément de style à part entière.

**3. Ponctuation.** Point-virgule, deux-points, tiret cadratin, parenthèses,
points de suspension, exclamations. Un auteur qui n'utilise jamais le
point-virgule et un auteur qui en met trois par page n'écrivent pas la même
prose, indépendamment du lexique.

**4. Voix narrative.** Personne (1ʳᵉ / 3ᵉ), temps dominant (passé simple,
imparfait, présent de narration), focalisation (voir `critique.md` §5),
**distance psychique** habituelle et son amplitude. Présence ou non d'un
narrateur qui commente.

**5. Lexique.** Registre (soutenu, courant, familier, mélange), densité
d'adjectifs et d'adverbes, mots rares, archaïsmes, néologismes et termes de
lore, champs lexicaux récurrents. Noter aussi le niveau de technicité : un
auteur qui nomme précisément les pièces d'armure ne fait pas le même effet que
celui qui écrit « son armure ».

**6. Dialogue.** Ratio dialogue/narration, longueur moyenne des répliques,
traitement des incises (neutres ou colorées, avant/après/en milieu), présence
de gestes intercalés (« didascalies »), oralité (élisions, répétitions,
interruptions), typographie employée (tiret cadratin, guillemets français).

**7. Description et sensorialité.** Densité descriptive, mode d'entrée dans une
scène (par le lieu ? par un geste ? par une réplique ?), canaux sensoriels
dominants — beaucoup d'auteurs sont massivement visuels ; ceux qui ne le sont
pas se reconnaissent à ça. Ordre de la description : ensemble → détail, ou
détail → ensemble.

**8. Images.** Fréquence des métaphores et comparaisons (une pour combien de
mots), domaines sources récurrents, longueur des images (comparaison brève vs
métaphore filée), degré d'originalité vs images conventionnelles assumées.

**9. Signature.** Les tics et les partis pris : anaphores, formules de
transition, façon d'ouvrir et de fermer un chapitre, refus systématiques (« ne
met jamais d'adverbe dans une incise », « ne décrit jamais un visage »). C'est
la dimension la plus utile en réécriture et la moins mesurable — elle vient de
la lecture, pas du script.

---

## 5. Les contre-exemples

Section obligatoire de la fiche, et la plus efficace en pratique. Écrire 3 à 5
phrases **hors-style** avec leur version dans le style, et dire pourquoi.

Exemple de forme attendue :

```
Hors-style : « Il ressentit une profonde tristesse en contemplant les ruines
majestueuses de la cité autrefois florissante. »
Pourquoi : abstraction affective nommée, deux adjectifs évaluatifs, aucun
détail concret.
Dans le style : « Les pierres tenaient encore. C'était le pire. »
```

Une contrainte négative (« ce que ce style ne fait jamais ») cadre une
réécriture bien plus efficacement qu'une description positive, parce qu'elle
bloque directement les réflexes par défaut d'un modèle de langage.

---

## 6. Pièges

- **Confondre style et sujet.** Un extrait de bataille et un extrait de deuil
  diffèrent par le contenu, pas forcément par le style. Isoler ce qui reste
  constant.
- **Confondre style et faiblesse.** Dans un texte de l'auteur, certaines
  régularités sont des tics involontaires, pas des choix. Ne pas les figer dans
  une fiche sans lui demander — sinon on canonise un défaut.
- **Sur-généraliser depuis un échantillon court.** Voir §2.
- **Fiche trop longue.** Au-delà de deux pages, elle ne sera plus relue à chaque
  réécriture, donc elle ne servira plus. Couper.
- **Décrire au lieu d'instruire.** « Style fluide » n'instruit rien. Toute ligne
  doit se traduire en une décision d'écriture.
- **Croire que la fiche remplace le jugement.** Elle cadre, elle ne décide pas.

---

## 7. Utiliser la fiche pour réécrire

1. Relire la fiche **avant** d'écrire la première variante, pas après.
2. Écrire les variantes en visant explicitement 2 ou 3 dimensions de la grille
   (par exemple : longueur de phrase + traitement des incises), pas les neuf à
   la fois — une variante qui essaie de tout satisfaire devient un pastiche
   raide.
3. Passer chaque variante au script en `--compare` avec l'échantillon de
   référence, et regarder les écarts marqués.
4. Dire à l'auteur ce que la variante respecte de la fiche et ce qu'elle en
   écarte volontairement. Un écart assumé et nommé est un choix ; un écart non
   vu est une dérive.
5. Si l'auteur corrige la variante, **c'est de l'information sur son style** :
   proposer d'enrichir la fiche avec ce qu'il vient de changer, notamment dans
   la section contre-exemples. C'est là que la fiche devient réellement
   réutilisable.
