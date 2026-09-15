# TP2 (version longue) — API CRUD avancée « Gestion des employés » -- CONSIGNES

## Objectif général
Construire une API de gestion d'employés complète et réaliste : schémas de données bien
séparés, recherche et filtrage, tri et pagination, mise à jour partielle, et persistance
des données sur disque (pour ne pas tout perdre à chaque redémarrage du serveur).

## Durée totale
Environ 3h, en 7 étapes progressives.

## Prérequis
- Avoir fait (ou au moins tenté) le TP2 version courte, ou connaître les bases de FastAPI
  (routes, Pydantic, HTTPException) vues au TP1.

## Déroulé indicatif

| Étape | Contenu | Durée |
|---|---|---|
| 0 | Mise en place | 10 min |
| Exercice 1 | Modélisation avancée avec Pydantic | 25 min |
| Exercice 2 | CRUD complet | 30 min |
| Exercice 3 | Recherche et filtrage | 25 min |
| Exercice 4 | Tri et pagination | 20 min |
| — | Pause | 10 min |
| Exercice 5 | Mise à jour partielle (PATCH) | 20 min |
| Exercice 6 | Persistance des données (fichier JSON) | 30 min |
| Exercice 7 (bonus) | Tests automatisés | 20 min |
| — | Synthèse | 10 min |

Comme toujours : aucune indication de résolution n'est donnée au départ. Cherchez d'abord,
demandez de l'aide si vous êtes bloqués plus de quelques minutes.

---

## Étape 0 — Mise en place (10 min)

1. Créez et activez un environnement virtuel dans ce dossier.
2. Installez les dépendances de `requirements.txt`.
3. Repérez les deux fichiers à compléter : `schema.py` et `main.py`, chacun balisé par des
   `# ===== EXERCICE N =====` et des `# TODO`.

---

## Exercice 1 — Modélisation avancée avec Pydantic (25 min)

**Objectif :** comprendre pourquoi on utilise en général **plusieurs** schémas Pydantic
pour une même ressource, plutôt qu'un seul modèle unique.

**Contexte :** jusqu'ici, un employé était décrit par un seul modèle. Le problème : le
client qui crée un employé ne connaît pas encore son `id` (c'est le serveur qui l'attribue),
et lors d'une mise à jour partielle, on veut pouvoir ne modifier qu'un seul champ à la fois.

**Consignes (dans `schema.py`) :**
1. Définissez `EmployeeBase`, avec les champs communs : `nom`, `prenom`, `poste`, `salaire`.
   Ajoutez une contrainte de validation sur `salaire` : il doit être strictement positif
   (indice : la fonction `Field` de Pydantic permet d'exprimer des contraintes comme
   `Field(gt=0)`).
2. Définissez `EmployeeCreate`, qui hérite de `EmployeeBase` (c'est le schéma attendu en
   entrée d'un `POST /employees` : le client ne fournit jamais l'`id`).
3. Définissez `Employee`, qui hérite de `EmployeeBase` et ajoute un champ `id` (entier).
   C'est le schéma que l'API renverra dans ses réponses.
4. Définissez `EmployeeUpdate`, avec les mêmes champs que `EmployeeBase`, mais **tous
   optionnels** (c'est le schéma attendu en entrée d'un `PATCH /employees/{id}` — voir
   exercice 5 — où le client ne renvoie que les champs qu'il veut modifier).

**Vérification :** essayez d'instancier `EmployeeCreate` avec un `salaire` négatif dans une
cellule Python ou un petit script de test, et vérifiez que Pydantic lève bien une erreur.

---

## Exercice 2 — CRUD complet (30 min)

**Objectif :** implémenter les 5 opérations de base, en utilisant les schémas définis à
l'exercice 1.

**Consignes (dans `main.py`) :**
1. Créez une structure de données en mémoire pour stocker les employés (une liste de
   dictionnaires, ou une liste d'objets `Employee` — à vous de choisir).
2. Implémentez :
   - `GET /employees` → liste tous les employés (réponse typée `list[Employee]`)
   - `GET /employees/{id}` → un employé précis (404 si absent)
   - `POST /employees` → reçoit un `EmployeeCreate`, génère un `id`, renvoie un `Employee`
     (statut 201)
   - `PUT /employees/{id}` → remplace entièrement un employé existant (404 si absent)
   - `DELETE /employees/{id}` → supprime un employé (statut 204, 404 si absent)

**Vérification :** testez l'ensemble sur `/docs`, en créant au moins 5 employés avec des
postes et des salaires variés (vous en aurez besoin pour les exercices suivants).

---

## Exercice 3 — Recherche et filtrage (25 min)

**Objectif :** permettre au client de ne récupérer qu'une partie des employés, selon des
critères passés en paramètres de requête.

**Consignes :**
1. Modifiez la route `GET /employees` pour accepter des paramètres de requête **optionnels** :
   - `poste` : ne renvoyer que les employés ayant exactement ce poste
   - `salaire_min` : ne renvoyer que les employés dont le salaire est supérieur ou égal à
     cette valeur
   - `salaire_max` : ne renvoyer que les employés dont le salaire est inférieur ou égal à
     cette valeur
2. Ces trois paramètres doivent pouvoir être combinés (ex : tous les développeurs gagnant
   entre 2500 et 4000).
3. Si aucun paramètre n'est fourni, la route doit continuer à se comporter comme avant
   (tous les employés).

**Vérification :** testez `/employees?poste=Développeur`, puis
`/employees?salaire_min=3000&salaire_max=4000`, et vérifiez les résultats.

---

## Exercice 4 — Tri et pagination (20 min)

**Objectif :** gérer de grandes listes de résultats de façon utilisable côté client.

**Consignes :**
1. Ajoutez un paramètre de requête `sort_by` (valeurs possibles : `"nom"` ou `"salaire"`,
   valeur par défaut `"nom"`) qui trie la liste renvoyée par `GET /employees`.
2. Ajoutez un paramètre `order` (`"asc"` ou `"desc"`, défaut `"asc"`) pour choisir le sens
   du tri.
3. Ajoutez deux paramètres de pagination : `skip` (défaut 0) et `limit` (défaut 10), qui
   déterminent quelle tranche de la liste triée est renvoyée.
4. Ces paramètres doivent fonctionner **en plus** des filtres de l'exercice 3 (filtrer,
   puis trier, puis paginer, dans cet ordre).

**Vérification :** avec au moins 8 employés créés, testez
`/employees?sort_by=salaire&order=desc&skip=0&limit=3` et vérifiez que vous obtenez bien
les 3 employés les mieux payés.

---

## PAUSE (10 min)

---

## Exercice 5 — Mise à jour partielle : PATCH (20 min)

**Objectif :** comprendre la différence entre `PUT` (remplacement complet) et `PATCH`
(modification partielle).

**Consignes :**
1. Ajoutez une route `PATCH /employees/{id}` qui reçoit un `EmployeeUpdate` (voir
   exercice 1) et ne modifie que les champs effectivement fournis par le client, en
   laissant les autres inchangés.
2. Réfléchissez : comment savoir si un champ a été explicitement fourni par le client,
   plutôt que laissé à sa valeur par défaut ? (Indice : Pydantic propose une méthode pour
   n'exporter que les champs réellement fournis.)
3. Renvoyez 404 si l'employé n'existe pas.

**Vérification :** modifiez uniquement le `salaire` d'un employé via `PATCH`, et vérifiez
que son `nom`, `prenom` et `poste` n'ont pas changé.

---

## Exercice 6 — Persistance des données (30 min)

**Objectif :** ne plus perdre toutes les données à chaque redémarrage du serveur.

**Contexte :** jusqu'ici, la liste des employés vit uniquement en mémoire : elle disparaît
dès que le serveur redémarre (avec `--reload` par exemple). On va la sauvegarder dans un
fichier `employees.json`.

**Consignes :**
1. Au démarrage de l'application, si `employees.json` existe, chargez son contenu dans
   votre structure de données en mémoire. S'il n'existe pas, démarrez avec une liste vide.
2. Après **chaque** opération qui modifie les données (création, mise à jour complète ou
   partielle, suppression), réécrivez le fichier `employees.json` avec l'état à jour.
3. Vérifiez que si vous créez des employés, puis que vous arrêtez et relancez le serveur
   (`Ctrl+C` puis `uvicorn main:app --reload`), vos employés sont toujours là.

**Attention :** ajoutez `employees.json` à votre `.gitignore` — ce sont des données de
test, pas du code à versionner.

---

## Exercice 7 (bonus) — Tests automatisés (20 min)

**Objectif :** sécuriser votre API avec une vraie suite de tests.

**Consignes (dans `test_api.py`) :**
Écrivez des tests couvrant au moins :
- la création d'un employé avec un salaire invalide (doit échouer, 422)
- le filtrage par poste
- le tri et la pagination
- une mise à jour partielle qui ne change qu'un seul champ
- la suppression suivie d'une tentative de lecture (404 attendu)

---

## Synthèse (10 min)

À l'oral avec le formateur : pourquoi sépare-t-on `EmployeeCreate`, `Employee` et
`EmployeeUpdate` plutôt que d'utiliser un seul modèle Pydantic partout ? Quel est le risque
si on ne le fait pas ?

## Commandes utiles

```
python -m venv venv
venv\Scripts\activate          (Windows)
source venv/bin/activate       (macOS / Linux)

pip install -r requirements.txt

uvicorn main:app --reload
```






# TP2 (version longue) — API CRUD avancée « Gestion des employés » -- RESOLUTON TP

## Bilan post-TP — ce qu'il faut retenir

Cette partie resume les notions retenues apres la realisation du TP.

### 1. Les schemas Pydantic

On utilise plusieurs modeles car ils n'ont pas le meme role :

- `EmployeeBase` contient les champs communs : `nom`, `prenom`, `poste` et `salaire`.
- `EmployeeCreate` sert a recevoir les donnees envoyees lors d'un `POST`. Le client ne fournit pas l'`id`.
- `Employee` represente un employe renvoye par l'API et contient aussi l'`id`.
- `EmployeeUpdate` sert au `PATCH`. Ses champs sont optionnels pour permettre une modification partielle.

La contrainte `Field(gt=0)` signifie que le salaire doit etre strictement superieur a zero. Une valeur egale a zero ou negative provoque automatiquement une reponse `422`.

### 2. Les methodes HTTP

- `GET` consulte les employes sans modifier les donnees.
- `POST` cree un nouvel employe.
- `PUT` remplace completement un employe et necessite tous les champs.
- `PATCH` modifie uniquement les champs envoyes.
- `DELETE` supprime un employe.

Pour une mise a jour partielle, `exclude_unset=True` permet de recuperer uniquement les champs effectivement fournis par le client.

### 3. Recherche, tri et pagination

La route `GET /employees` peut recevoir des parametres optionnels :

- `poste` filtre sur un poste precis ;
- `salaire_min` conserve les salaires superieurs ou egaux a cette valeur ;
- `salaire_max` conserve les salaires inferieurs ou egaux a cette valeur ;
- `sort_by` choisit le champ de tri, par exemple `nom` ou `salaire` ;
- `order` choisit le sens du tri avec `asc` ou `desc` ;
- `skip` indique combien de resultats sont ignores ;
- `limit` indique combien de resultats sont retournes.

L'ordre de traitement est important :

```text
filtrer -> trier -> paginer
```

Exemple :

```text
GET /employees?poste=Dev&sort_by=salaire&order=desc&skip=0&limit=3
```

Cette requete conserve les employes `Dev`, les trie du salaire le plus eleve au plus faible, puis retourne les trois premiers.

### 4. Persistance des donnees

Sans persistance, la liste `employees` existe uniquement en memoire et est perdue au redemarrage du serveur.

Le fichier `employees.json` permet de conserver les donnees :

- `load_employees()` lit le fichier au demarrage et reconstruit les objets `Employee` ;
- `save_employees()` reecrit le fichier apres chaque `POST`, `PUT`, `PATCH` ou `DELETE` ;
- si le fichier n'existe pas, l'application demarre avec une liste vide.

Le fichier est cree dans le meme dossier que `main.py`. Il s'agit de donnees de test et il ne doit pas etre versionne dans Git.

### 5. Codes de reponse HTTP

- `200` indique qu'une requete a reussi, notamment un `GET` ou un `PATCH` ;
- `201` indique qu'un employe a ete cree avec succes ;
- `404` indique que l'employe demande n'existe pas ;
- `422` indique que les donnees envoyees ne respectent pas le schema attendu, par exemple un salaire invalide.

FastAPI genere automatiquement certaines reponses, comme `422` lors d'une erreur de validation. Les reponses `404` sont levees explicitement avec `HTTPException`.

### 6. Tests automatises

Les tests utilisent `TestClient` pour appeler l'API sans lancer Uvicorn. La commande suivante execute tous les tests :

```powershell
pytest -v test_api.py
```

Les tests verifies couvrent :

- le refus d'un salaire invalide ;
- le filtrage par poste ;
- le tri et la pagination ;
- la modification d'un seul champ avec `PATCH` ;
- la suppression d'un employe suivie d'une reponse `404`.

Un resultat comme `5 passed` signifie que les cinq tests ont reussi.

### 7. Verification manuelle avec Swagger

Le serveur se lance avec :

```powershell
uvicorn main:app --reload
```

La documentation interactive est disponible a l'adresse :

```text
http://127.0.0.1:8000/docs
```

Swagger permet de tester les routes `POST`, `GET`, `PUT`, `PATCH` et `DELETE` directement depuis le navigateur.
