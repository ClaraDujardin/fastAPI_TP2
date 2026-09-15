"""
TP2 (version longue) - Exercice 7 (bonus) : tests automatisés

Consigne :
Écrivez des tests avec le TestClient de FastAPI couvrant au moins :
- la création d'un employé avec un salaire invalide (doit échouer, 422)
- le filtrage par poste
- le tri et la pagination
- une mise à jour partielle (PATCH) qui ne change qu'un seul champ
- la suppression suivie d'une tentative de lecture (404 attendu)
"""

# TODO : from fastapi.testclient import TestClient
from fastapi.testclient import TestClient

# TODO : from main import app
from main import app

# TODO : client = TestClient(app)
client = TestClient(app)

# TODO : def test_salaire_invalide(): ...
def test_salaire_invalide():
    response = client.post("/employees", json={
        "nom": "Dujardin",
        "prenom": "Clara",
        "poste": "Data Engineer",
        "salaire": -1000  # salaire invalide
    })
    assert response.status_code == 422

# TODO : def test_filtrage_par_poste(): ...
def test_filtrage_par_poste():
    # Créer des employés pour le test
    client.post("/employees", json={
        "nom": "Dupont",
        "prenom": "Jean",
        "poste": "Data Engineer",
        "salaire": 5000
    })
    client.post("/employees", json={
        "nom": "Durand",
        "prenom": "Marie",
        "poste": "Data Scientist",
        "salaire": 6000
    })

    response = client.get("/employees", params={"poste": "Data Engineer"})
    assert response.status_code == 200
    employees = response.json()
    assert all(emp["poste"] == "Data Engineer" for emp in employees)

# TODO : def test_tri_et_pagination(): ...
def test_tri_et_pagination():
    # Créer des employés pour le test
    client.post("/employees", json={
        "nom": "Martin",
        "prenom": "Paul",
        "poste": "Data Analyst",
        "salaire": 4000
    })
    client.post("/employees", json={
        "nom": "Bernard",
        "prenom": "Lucie",
        "poste": "Data Analyst",
        "salaire": 4500
    })

    response = client.get("/employees", params={"sort_by": "salaire", "order": "desc", "skip": 0, "limit": 2})
    assert response.status_code == 200
    employees = response.json()
    assert employees[0]["salaire"] >= employees[1]["salaire"]

# TODO : def test_patch_un_seul_champ(): ...
def test_patch_un_seul_champ():
    # Créer un employé pour le test
    response = client.post("/employees", json={
        "nom": "Lemoine",
        "prenom": "Sophie",
        "poste": "Data Engineer",
        "salaire": 5500
    })
    employee_id = response.json()["id"]

    # Mettre à jour uniquement le salaire
    response = client.patch(f"/employees/{employee_id}", json={"salaire": 6000})
    assert response.status_code == 200
    updated_employee = response.json()
    assert updated_employee["salaire"] == 6000
    assert updated_employee["nom"] == "Lemoine"  # les autres champs restent inchangés

# TODO : def test_suppression_puis_404(): ...
def test_suppression_puis_404():
    # Créer un employé pour le test
    response = client.post("/employees", json={
        "nom": "Moreau",
        "prenom": "Alice",
        "poste": "Data Scientist",
        "salaire": 7000
    })
    employee_id = response.json()["id"]

    # Supprimer l'employé
    response = client.delete(f"/employees/{employee_id}")
    assert response.status_code == 200

    # Tenter de récupérer l'employé supprimé
    response = client.get(f"/employees/{employee_id}")
    assert response.status_code == 404
