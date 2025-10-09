"""seed_verbs_data

Revision ID: fdcfdd58fb59
Revises: b97ea2610d64
Create Date: 2025-10-09 20:32:09.410780

"""
from typing import Sequence, Union
from pathlib import Path

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'fdcfdd58fb59'
down_revision: Union[str, None] = 'b97ea2610d64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Загружает seed данные глаголов, если таблица пустая"""
    conn = op.get_bind()
    
    # Проверяем количество записей в таблице verbs
    try:
        result = conn.execute(text("SELECT COUNT(*) FROM verbs"))
        count = result.scalar()
        
        # Если данные уже есть - пропускаем
        if count > 0:
            print(f"Таблица verbs уже содержит {count} записей. Пропускаем импорт.")
            return
    except Exception as e:
        # Таблица не существует или пустая - продолжаем загрузку
        print(f"Таблица verbs пустая или только создана. Загружаем данные...")
    
    # Читаем SQL файл и выполняем
    sql_file = Path(__file__).parent.parent.parent / "data" / "verbs_seed.sql"
    
    if not sql_file.exists():
        print(f"Файл {sql_file} не найден. Пропускаем импорт.")
        return
    
    print(f"Загружаем данные из {sql_file.name}...")
    
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    # Выполняем SQL
    conn.execute(text(sql_content))
    
    print("Данные глаголов успешно загружены!")


def downgrade() -> None:
    """Удаляет все данные из таблиц verb_forms и verbs"""
    conn = op.get_bind()
    # Сначала удаляем формы (foreign key), потом глаголы
    conn.execute(text("TRUNCATE TABLE verb_forms CASCADE"))
    conn.execute(text("TRUNCATE TABLE verbs CASCADE"))
