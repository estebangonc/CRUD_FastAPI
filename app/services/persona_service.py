import random

import re
import unicodedata
from faker import Faker

from typing import Sequence
from sqlalchemy import or_, text
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models.persona import Persona
from ..views.persona import PersonaCreate, PersonaUpdate
from .errors import PersonaNotFoundError, EmailAlreadyExistsError


def create_persona(db: Session, payload: PersonaCreate) -> Persona:
    """Create a Persona ensuring unique email."""
    # Optimistic check; DB unique constraint is the final guard
    if db.query(Persona).filter(Persona.email == payload.email).first():
        raise EmailAlreadyExistsError()
    obj = Persona(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        birth_date=payload.birth_date,
        is_active=payload.is_active,
        notes=payload.notes,
    )
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Catch race conditions on unique email
        raise EmailAlreadyExistsError() from e
    db.refresh(obj)
    return obj

DOMINIOS_REALES = ["gmail.com", "outlook.com", "yahoo.es", "hotmail.com"]

def _slug(texto: str) -> str:
    """Pasa a minusculas ASCII, sin tildes ni espacios (para armar emails)."""
    ascii_txt = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]", "", ascii_txt.lower())

def poblar_personas(db: Session, cantidad: int) -> int:
    """Crea 'cantidad' personas con datos falsos (Faker) y emails unicos con dominios reales."""
    fake = Faker("es_CO")
    usados = {email for (email,) in db.query(Persona.email).all()}
    nuevas: list[Persona] = []
    
    for _ in range(cantidad):
        nombre = fake.first_name()
        apellido = fake.last_name()
        base = f"{_slug(nombre) or 'usuario'}.{_slug(apellido) or 'persona'}"
        dominio = random.choice(DOMINIOS_REALES)
        email = f"{base}@{dominio}"
        n = 1
        while email in usados: # nombre y apellido repetidos: agrega un numero
            n += 1
            email = f"{base}{n}@{dominio}"
            
        usados.add(email)
        nuevas.append(
            Persona(
                first_name=nombre,
                last_name=apellido,
                email=email,
                phone=f"+57 3{random.randint(0, 2)}{random.randint(0, 9)} "
                      f"{random.randint(100, 999)} {random.randint(1000, 9999)}",
                birth_date=fake.date_of_birth(minimum_age=18, maximum_age=85),
                is_active=fake.boolean(),
                notes=fake.sentence(nb_words=6) if random.random() < 0.5 else None,
            )
        )
        
    db.add_all(nuevas)
    db.commit()
    return len(nuevas)

def reset_personas(db: Session) -> int:
    """Elimina todos los registros de personas y devuelve cuantos se borraron."""
    eliminados = db.query(Persona).delete()
    db.commit()
    return eliminados

def estadisticas_dominios(db: Session) -> dict:
    """Cuenta personas por dominio de correo (lo que hay despues del @)."""
    sql = text(f"""
        SELECT SUBSTRING_INDEX(email, '@', -1) AS dominio, COUNT(*) AS total
        FROM {Persona.__tablename__}
        GROUP BY dominio
        ORDER BY total DESC
    """)
    return {fila.dominio: int(fila.total) for fila in db.execute(sql).fetchall()}


def list_personas(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Persona]:
    """Return paginated list of Personas."""
    return db.query(Persona).offset(skip).limit(limit).all()


def get_persona(db: Session, persona_id: int) -> Persona:
    """Return Persona by ID or raise if not found."""
    obj = db.query(Persona).filter(Persona.id == persona_id).first()
    if not obj:
        raise PersonaNotFoundError()
    return obj


def update_persona(db: Session, persona_id: int, payload: PersonaUpdate) -> Persona:
    """Update Persona partially, enforcing unique email."""
    obj = db.query(Persona).filter(Persona.id == persona_id).first()
    if not obj:
        raise PersonaNotFoundError()

    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"] != obj.email:
        if db.query(Persona).filter(Persona.email == data["email"], Persona.id != persona_id).first():
            raise EmailAlreadyExistsError()

    for field, value in data.items():
        setattr(obj, field, value)

    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise EmailAlreadyExistsError() from e
    db.refresh(obj)
    return obj


def delete_persona(db: Session, persona_id: int) -> None:
    """Delete Persona by ID or raise if not found."""
    obj = db.query(Persona).filter(Persona.id == persona_id).first()
    if not obj:
        raise PersonaNotFoundError()
    db.delete(obj)
    db.commit()

def obtener_estadisticas_edad(db: Session) -> dict:
    sql = text(f"""
        SELECT
            ROUND(AVG(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())), 1) AS promedio,
            MIN(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())) AS minima,
            MAX(TIMESTAMPDIFF(YEAR, birth_date, CURDATE())) AS maxima
        FROM {Persona.__tablename__}
    """)
    fila = db.execute(sql).fetchone()

    # Tabla vacía (o sin fechas): AVG/MIN/MAX devuelven NULL
    if fila is None or fila.promedio is None:
        return {"edad_promedio": 0.0, "edad_minima": 0, "edad_maxima": 0}

    return {
        "edad_promedio": float(fila.promedio),
        "edad_minima": int(fila.minima),
        "edad_maxima": int(fila.maxima),
    }

def buscar_personas_por_termino(db: Session, termino: str):
    patron = f"%{termino}%"
    return db.query(Persona).filter(
        or_(
            Persona.first_name.ilike(patron),
            Persona.last_name.ilike(patron),
            Persona.email.ilike(patron),
        )
    ).all()