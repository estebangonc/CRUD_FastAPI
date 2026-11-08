from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr


class PersonaBase(BaseModel):
    """Shared attributes for Persona inputs."""
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    birth_date: date | None = None
    is_active: bool = True
    notes: str | None = None


class PersonaCreate(PersonaBase):
    """Schema used for creating a new Persona."""
    pass

class PoblarRequest(BaseModel):
   """Cuerpo del POST /personas/poblar: solo la cantidad de registros a
   crear."""
   cantidad: int

class PersonaUpdate(BaseModel):
    """Schema used for partial update of Persona."""
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    birth_date: date | None = None
    is_active: bool | None = None
    notes: str | None = None


class BulkDesactivarRequest(BaseModel):
    """Cuerpo del PATCH /personas/bulk/desactivar."""
    ids: list[int]


class BulkDesactivarResponse(BaseModel):
    """Respuesta de la desactivacion masiva."""
    message: str
    desactivados: list[int]
    no_encontrados: list[int]
    total_desactivados: int


class PersonaRead(BaseModel):
    """Schema used to return Persona data to clients."""
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None
    birth_date: date | None
    is_active: bool
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

class EstadisticasEdadResponse(BaseModel):
    edad_promedio: float
    edad_minima: int
    edad_maxima: int

class PersonaActivaResponse(BaseModel):
    id: int
    email: str
    phone: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}