from pydantic import BaseModel, Field


class VerbFormBase(BaseModel):
    """Базовая схема формы глагола"""
    person: str
    auxiliary_verb: str | None = None
    verb_form: str


class VerbFormResponse(VerbFormBase):
    """Схема ответа для формы глагола"""
    model_config = {"from_attributes": True}


class TenseGroup(BaseModel):
    """Группировка форм по времени"""
    tense: str
    forms: list[VerbFormResponse]


class VerbResponse(BaseModel):
    """Схема ответа для глагола со всеми формами"""
    infinitive: str
    tenses: list[TenseGroup]

    model_config = {"from_attributes": True}


class RandomVerbRequest(BaseModel):
    """Схема запроса для получения случайных форм глаголов"""
    verbs: list[str] = Field(..., description="Список инфинитивов глаголов")
    tense: str = Field(..., description="Время глагола (например, 'Indicativo Presente')")
    count: int = Field(..., ge=1, description="Количество случайных форм для возврата")


class RandomVerbResponse(BaseModel):
    """Схема ответа для случайной формы глагола"""
    infinitive: str
    value: str
    person: str

