"""
Скрипт для импорта глаголов из JSON файлов в базу данных
"""
import asyncio
import json
import sys
from pathlib import Path

# Добавляем корневую папку в sys.path для импорта модулей
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.verb import Verb, VerbForm


async def import_verb_from_file(file_path: Path, db: AsyncSession) -> bool:
    """
    Импортирует один глагол из JSON файла
    
    Args:
        file_path: Путь к JSON файлу
        db: Сессия базы данных
        
    Returns:
        True если импорт успешен, False если глагол уже существует
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        infinitive = data["infinitive"]
        
        # Проверяем, существует ли глагол
        stmt = select(Verb).where(Verb.infinitive == infinitive)
        result = await db.execute(stmt)
        existing_verb = result.scalar_one_or_none()
        
        if existing_verb:
            print(f"  ⏭️  Глагол '{infinitive}' уже существует, пропускаем")
            return False
        
        # Создаём новый глагол
        verb = Verb(infinitive=infinitive)
        db.add(verb)
        await db.flush()  # Получаем ID глагола
        
        # Создаём формы глагола
        forms_to_add = []
        for tense_data in data["tenses"]:
            tense_name = tense_data["tense"]
            for form_data in tense_data["forms"]:
                verb_form = VerbForm(
                    verb_id=verb.id,
                    tense=tense_name,
                    person=form_data["person"],
                    auxiliary_verb=form_data.get("aux"),
                    verb_form=form_data["verb"]
                )
                forms_to_add.append(verb_form)
        
        # Bulk insert для форм
        db.add_all(forms_to_add)
        await db.commit()
        
        print(f"  ✅ Импортирован глагол '{infinitive}' ({len(forms_to_add)} форм)")
        return True
        
    except Exception as e:
        await db.rollback()
        print(f"  ❌ Ошибка при импорте {file_path.name}: {e}")
        return False


async def import_all_verbs(verbs_dir: Path):
    """
    Импортирует все глаголы из папки verbs/
    
    Args:
        verbs_dir: Путь к папке с JSON файлами глаголов
    """
    json_files = list(verbs_dir.glob("*.json"))
    total_files = len(json_files)
    
    if total_files == 0:
        print(f"❌ Не найдено JSON файлов в папке {verbs_dir}")
        return
    
    print(f"📂 Найдено {total_files} файлов глаголов")
    print("🚀 Начинаем импорт...\n")
    
    imported_count = 0
    skipped_count = 0
    
    async with AsyncSessionLocal() as db:
        for idx, file_path in enumerate(json_files, 1):
            print(f"[{idx}/{total_files}] Обрабатываем {file_path.name}...")
            
            was_imported = await import_verb_from_file(file_path, db)
            
            if was_imported:
                imported_count += 1
            else:
                skipped_count += 1
    
    print(f"\n✨ Импорт завершён!")
    print(f"   Импортировано: {imported_count}")
    print(f"   Пропущено: {skipped_count}")
    print(f"   Всего: {total_files}")


async def main():
    """Точка входа"""
    # Определяем путь к папке verbs
    project_root = Path(__file__).parent.parent.parent
    verbs_dir = project_root / "verbs"
    
    if not verbs_dir.exists():
        print(f"❌ Папка {verbs_dir} не существует")
        return
    
    await import_all_verbs(verbs_dir)


if __name__ == "__main__":
    asyncio.run(main())

