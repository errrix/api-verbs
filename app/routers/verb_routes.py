import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.verb import Verb, VerbForm
from app.schemas.verb import (
    VerbResponse, 
    TenseGroup, 
    VerbFormResponse,
    RandomVerbRequest,
    RandomVerbResponse
)

router = APIRouter(prefix="/verbs", tags=["verbs"])


@router.get("/{infinitive}", response_model=VerbResponse)
async def get_verb_forms(
    infinitive: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все формы глагола по инфинитиву
    """
    # Загружаем глагол вместе со всеми его формами
    stmt = select(Verb).where(Verb.infinitive == infinitive).options(
        selectinload(Verb.forms)
    )
    result = await db.execute(stmt)
    verb = result.scalar_one_or_none()
    
    if not verb:
        raise HTTPException(status_code=404, detail=f"Глагол '{infinitive}' не найден")
    
    # Группируем формы по временам
    tenses_dict: dict[str, list[VerbForm]] = {}
    for form in verb.forms:
        if form.tense not in tenses_dict:
            tenses_dict[form.tense] = []
        tenses_dict[form.tense].append(form)
    
    # Формируем ответ
    tenses = [
        TenseGroup(
            tense=tense,
            forms=[
                VerbFormResponse(
                    person=form.person,
                    auxiliary_verb=form.auxiliary_verb,
                    verb_form=form.verb_form
                )
                for form in forms
            ]
        )
        for tense, forms in tenses_dict.items()
    ]
    
    return VerbResponse(infinitive=verb.infinitive, tenses=tenses)


@router.post("/random", response_model=list[RandomVerbResponse])
async def get_random_verb_forms(
    request: RandomVerbRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить случайные формы глаголов для указанного времени.
    
    Принимает список инфинитивов, время и количество форм.
    Возвращает случайно выбранные формы из всех доступных для указанных глаголов.
    """
    # Запрашиваем все формы для указанных глаголов в указанном времени
    stmt = (
        select(VerbForm, Verb.infinitive)
        .join(Verb, VerbForm.verb_id == Verb.id)
        .where(Verb.infinitive.in_(request.verbs))
        .where(VerbForm.tense == request.tense)
    )
    
    result = await db.execute(stmt)
    forms_with_infinitive = result.all()
    
    if not forms_with_infinitive:
        raise HTTPException(
            status_code=404, 
            detail=f"Формы глаголов для времени '{request.tense}' не найдены"
        )
    
    # Перемешиваем и выбираем нужное количество
    available_count = len(forms_with_infinitive)
    selected_count = min(request.count, available_count)
    selected_forms = random.sample(forms_with_infinitive, selected_count)
    
    # Формируем ответ
    return [
        RandomVerbResponse(
            infinitive=infinitive,
            value=form.verb_form,
            person=form.person
        )
        for form, infinitive in selected_forms
    ]

