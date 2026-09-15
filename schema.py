"""
TP2 (version longue) - Gestion des employés
Fichier schema.py

Consignes :
Vous allez définir PLUSIEURS modèles Pydantic, pas un seul, pour bien séparer :
- les données que le client envoie à la création (sans id : le serveur le génère)
- les données renvoyées par l'API (avec id)
- les données autorisées lors d'une mise à jour partielle (tous les champs optionnels)

Contrainte de validation à respecter :
- salaire : doit être strictement positif
(Indice : la fonction Field() de pydantic permet d'exprimer ce type de contrainte,
par exemple Field(gt=0).)
"""

# TODO 1 : importer BaseModel et Field depuis pydantic
# TODO 2 : importer Optional depuis typing (utile pour EmployeeUpdate)
from pydantic import BaseModel, Field
from typing import Optional

# ===== EXERCICE 1 : Modélisation avancée =====

# TODO 3 : définir EmployeeBase(BaseModel) avec les champs communs :
#          nom (str), prenom (str), poste (str), salaire (float, contrainte > 0)
class EmployeeBase(BaseModel):
    nom: str
    prenom: str
    poste: str
    salaire: float = Field(gt=0)

# TODO 4 : définir EmployeeCreate(EmployeeBase)
#          -> hérite de tous les champs de EmployeeBase, sans rien ajouter pour l'instant
#          (schéma attendu en entrée de POST /employees)
class EmployeeCreate(EmployeeBase):
    pass

# TODO 5 : définir Employee(EmployeeBase)
#          -> comme EmployeeBase, plus un champ id (int)
#          (schéma renvoyé par l'API dans ses réponses)
class Employee(EmployeeBase):
    id: int

# TODO 6 : définir EmployeeUpdate(BaseModel)
#          -> les mêmes champs que EmployeeBase, mais TOUS optionnels
#          (schéma attendu en entrée de PATCH /employees/{id})
class EmployeeUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    poste: Optional[str] = None
    salaire: Optional[float] = None