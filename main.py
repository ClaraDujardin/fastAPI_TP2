"""
TP2 (version longue) - Gestion des employés
Fichier main.py

Complétez chaque section au fur et à mesure des exercices. Relancez le serveur
(uvicorn main:app --reload) et testez sur http://127.0.0.1:8000/docs après chaque étape.
"""

# TODO (Exercice 2) : imports (FastAPI, HTTPException, vos modèles depuis schema.py, etc.)
from fastapi import FastAPI, HTTPException
from schema import Employee, EmployeeCreate, EmployeeUpdate
import json
import os

EMPLOYEES_FILE = os.path.join(os.path.dirname(__file__), "employees.json")

# TODO (Exercice 2) : instance de l'application (variable "app")
app = FastAPI()

# ===== EXERCICE 2 : CRUD complet =====

# TODO : structure de données en mémoire pour stocker les employés (liste)
#        (elle sera remplacée par un chargement depuis un fichier à l'exercice 6)
employees = []


def load_employees():
    global employees
    if os.path.exists(EMPLOYEES_FILE):
        with open(EMPLOYEES_FILE, "r", encoding="utf-8") as f:
            employees_data = json.load(f)
            employees = [Employee(**data) for data in employees_data]
    else:
        employees = []


def save_employees():
    employees_data = [employee.dict() for employee in employees]
    with open(EMPLOYEES_FILE, "w", encoding="utf-8") as f:
        json.dump(employees_data, f, ensure_ascii=False, indent=2)


load_employees()

# TODO : route GET /employees -> liste tous les employés
#        (cette route sera enrichie aux exercices 3 et 4 : filtres, tri, pagination)
# @app.get("/employees")
# def get_employees():
#     return employees

# TODO : route GET /employees/{employee_id} -> un employé précis, 404 si absent
@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    for employee in employees:
        if employee.id == employee_id:
            return employee
    raise HTTPException(status_code=404, detail="Employee not found")

# TODO : route POST /employees -> reçoit un EmployeeCreate, génère un id, renvoie un
#        Employee (statut 201)
@app.post("/employees", status_code=201)
def create_employee(employee: EmployeeCreate):
    new_employee = Employee(
        id=len(employees) + 1,
        **employee.dict()
    )
    employees.append(new_employee)
    save_employees()
    return new_employee

# TODO : route PUT /employees/{employee_id} -> remplace entièrement un employé existant,
#        404 si absent
@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, updated_employee: EmployeeCreate):
    for index, employee in enumerate(employees):
        if employee.id == employee_id:
            employees[index] = Employee(id=employee_id, **updated_employee.dict())
            save_employees()
            return employees[index]
    raise HTTPException(status_code=404, detail="Employee not found")

# TODO : route DELETE /employees/{employee_id} -> supprime un employé (statut 204),
#        404 si absent

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    for index, employee in enumerate(employees):
        if employee.id == employee_id:
            employees.pop(index)
            save_employees()
            return {"message": "Employee deleted"}
    raise HTTPException(status_code=404, detail="Employee not found")




# ===== EXERCICE 3 : Recherche et filtrage =====
# Revenez sur la route GET /employees ci-dessus et ajoutez-lui des paramètres de requête
# optionnels : poste, salaire_min, salaire_max. Combinez-les avec un filtrage progressif
# de la liste avant de la renvoyer.
# @app.get("/employees")
# def get_employees(poste: str = None, salaire_employee: float = None):
#     filtered_employees = employees
#     if poste:
#         filtered_employees = [e for e in filtered_employees if e.poste == poste]
#     if salaire_employee is not None:
#         filtered_employees = [e for e in filtered_employees if e.salaire >= salaire_employee]
#     return filtered_employees

# ===== EXERCICE 4 : Tri et pagination =====
# Toujours sur GET /employees : ajoutez sort_by ("nom" ou "salaire", défaut "nom"),
# order ("asc" ou "desc", défaut "asc"), puis skip (défaut 0) et limit (défaut 10).
# Ordre des opérations : filtrer -> trier -> paginer.
@app.get("/employees")
def get_employees(poste: str = None, salaire_employee: float = None,
                  sort_by: str = "nom", order: str = "asc",
                  skip: int = 0, limit: int = 10):
    filtered_employees = employees
    if poste:
        filtered_employees = [e for e in filtered_employees if e.poste == poste]
    if salaire_employee is not None:
        filtered_employees = [e for e in filtered_employees if e.salaire >= salaire_employee]

    # Tri
    reverse_order = (order == "desc")
    if sort_by == "nom":
        filtered_employees.sort(key=lambda e: e.nom, reverse=reverse_order)
    elif sort_by == "salaire":
        filtered_employees.sort(key=lambda e: e.salaire, reverse=reverse_order)

    # Pagination
    return filtered_employees[skip:skip + limit]

# ===== EXERCICE 5 : Mise à jour partielle (PATCH) =====

# TODO : route PATCH /employees/{employee_id}
#        -> reçoit un EmployeeUpdate, ne modifie que les champs réellement fournis,
#           404 si l'employé n'existe pas
#        (Indice : une méthode de Pydantic permet d'exporter uniquement les champs
#        explicitement fournis par le client, en excluant les valeurs par défaut.)
@app.patch("/employees/{employee_id}")
def patch_employee(employee_id: int, employee_update: EmployeeUpdate):
    for index, employee in enumerate(employees):
        if employee.id == employee_id:
            update_data = employee_update.dict(exclude_unset=True)
            updated_employee = employees[index].copy(update=update_data)
            employees[index] = updated_employee
            save_employees()
            return updated_employee
    raise HTTPException(status_code=404, detail="Employee not found")

# ===== EXERCICE 6 : Persistance des données =====
# 1. Au démarrage de l'application, chargez employees.json s'il existe (sinon liste vide).
# 2. Après chaque opération qui modifie les données (POST, PUT, PATCH, DELETE), réécrivez
#    employees.json avec l'état à jour.
# TODO : import de json et os (ou pathlib) en haut du fichier
# TODO : fonction charger_employees() appelée au démarrage
# TODO : fonction sauvegarder_employees() appelée après chaque modification

# DONE
