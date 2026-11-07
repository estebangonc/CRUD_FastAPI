from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..views.persona import PersonaCreate, PersonaUpdate, PersonaRead, PoblarRequest, EstadisticasEdadResponse
from ..services import persona_service

router = APIRouter(prefix="/personas", tags=["personas"])



@router.post("/poblar", status_code=status.HTTP_201_CREATED)
def poblar_endpoint(payload: PoblarRequest, db: Session = Depends(get_db)):
    """Endpoint 1: Crea `cantidad` personas con datos generados por Faker (entre 1 y 1000)."""
    if payload.cantidad <= 0 or payload.cantidad > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad debe ser un entero entre 1 y 1000.",
        )
    creados = persona_service.poblar_personas(db, payload.cantidad)
    return {"message": f"{creados} usuarios creados exitosamente", "status": 201}

@router.delete("/reset")
def reset_endpoint(db: Session = Depends(get_db)):
    """Endpoint 2: Elimina todos los registros. Va antes de DELETE /{persona_id}."""
    eliminados = persona_service.reset_personas(db)
    return {
        "message": "Base de datos limpiada. Se eliminaron todos los registros.",
        "deleted_count": eliminados,
    }

@router.get("/estadisticas/dominios")
def estadisticas_dominios_endpoint(db: Session = Depends(get_db)):
    """Endpoint 3: Cantidad de personas por proveedor de correo (GROUP BY)."""
    return persona_service.estadisticas_dominios(db)


@router.post("", response_model=PersonaRead, status_code=status.HTTP_201_CREATED)
def create_persona(persona_in: PersonaCreate, db: Session = Depends(get_db)):
    """Create a new Persona delegating to service layer."""
    # Let domain errors bubble up to global handlers
    return persona_service.create_persona(db, persona_in)


@router.get("", response_model=List[PersonaRead])
def list_personas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List Personas with pagination via service layer."""
    return persona_service.list_personas(db, skip=skip, limit=limit)

@router.get("/estadisticas/edad", response_model=EstadisticasEdadResponse)
def estadisticas_edad_endpoint(db: Session = Depends(get_db)):
    """Endpoint 4: Retorna edad promedio (1 decimal), minima y maxima calculadas con TIMESTAMPDIFF en SQL."""
    return persona_service.obtener_estadisticas_edad(db)


@router.get("/{persona_id}", response_model=PersonaRead)
def get_persona(persona_id: int, db: Session = Depends(get_db)):
    """Retrieve a Persona by ID via service layer."""
    return persona_service.get_persona(db, persona_id)


@router.put("/{persona_id}", response_model=PersonaRead)
def update_persona(persona_id: int, persona_in: PersonaUpdate, db: Session = Depends(get_db)):
    """Update an existing Persona (partial) via service layer."""
    return persona_service.update_persona(db, persona_id, persona_in)


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(persona_id: int, db: Session = Depends(get_db)):
    """Delete a Persona by ID via service layer."""
    persona_service.delete_persona(db, persona_id)
    return None