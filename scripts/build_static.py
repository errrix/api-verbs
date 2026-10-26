"""
Сборка статических JSON-файлов с глаголами из сгенерированных спряжений и файлов переводов.

Спряжения лежат в data/conjugations.json, его делает npm run generate (scripts/generate_conjugations.mjs).

Результат (по умолчанию в dist/):
    index.json               — список глаголов, времён, лиц и языков перевода
    verbs/{infinitive}.json  — все формы и переводы одного глагола
    tenses/{id}.json         — одно время для всех глаголов
    translations/{lang}.json — переводы всех глаголов на один язык
    themes.json              — глаголы по темам: {тема: [глаголы от частых к редким]}
    frequency.json           — все глаголы от частых к редким

Запуск: python scripts/build_static.py [папка_результата]
"""
from __future__ import annotations

import json
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONJUGATIONS_FILE = ROOT / "data" / "conjugations.json"
# Языки переводов: ru — эталон, по его значениям переведены остальные
TRANSLATION_LANGUAGES = ["ru", "en", "pt", "fr", "de", "it"]
TRANSLATION_FILES = {lang: ROOT / "data" / f"translations_{lang}.json" for lang in TRANSLATION_LANGUAGES}
MAX_TRANSLATIONS = 3
THEMES_FILE = ROOT / "data" / "themes.json"
FREQUENCY_FILE = ROOT / "data" / "frequency.json"

PERSONS = ["1s", "2s", "3s", "1p", "2p", "3p"]


def load_translations(path: Path, infinitives: list[str]) -> dict[str, list[str]]:
    """Читает файл переводов {инфинитив: [значения]} и проверяет его по списку глаголов"""
    if not path.exists():
        raise ValueError(f"Не найден файл переводов {path.name}")
    with open(path, "r", encoding="utf-8") as f:
        try:
            raw = json.load(f)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path.name}: некорректный JSON ({error})") from error
    if not isinstance(raw, dict):
        raise ValueError(f"{path.name}: ожидался объект {{инфинитив: [значения]}}")

    translations = {unicodedata.normalize("NFC", key): value for key, value in raw.items()}
    errors: list[str] = []
    if len(translations) != len(raw):
        errors.append("есть повторяющиеся ключи (отличаются только юникод-нормализацией)")
    if missing := sorted(set(infinitives) - set(translations)):
        errors.append(f"нет перевода для {len(missing)} глаголов: {', '.join(missing)}")
    if extra := sorted(set(translations) - set(infinitives)):
        errors.append(f"лишние ключи ({len(extra)}), таких глаголов нет: {', '.join(extra)}")

    for infinitive, values in translations.items():
        if not isinstance(values, list) or not 1 <= len(values) <= MAX_TRANSLATIONS:
            errors.append(f"{infinitive}: ожидался список от 1 до {MAX_TRANSLATIONS} значений, найдено {values!r}")
        elif any(not isinstance(value, str) or not value.strip() for value in values):
            errors.append(f"{infinitive}: значения должны быть непустыми строками, найдено {values!r}")

    if errors:
        raise ValueError(f"Ошибки в {path.name}:\n" + "\n".join(f"  - {error}" for error in errors))
    return {infinitive: translations[infinitive] for infinitive in infinitives}


def load_themes(path: Path, infinitives: list[str]) -> dict[str, list[str]]:
    """Читает темы {тема: [глаголы]} и проверяет, что в них только глаголы из списка и нет пустых тем"""
    with open(path, "r", encoding="utf-8") as f:
        themes = json.load(f)
    known = set(infinitives)
    errors = [
        f"{theme}: нет таких глаголов: {', '.join(sorted(set(verbs) - known))}"
        for theme, verbs in themes.items()
        if set(verbs) - known
    ]
    errors += [f"{theme}: пустая тема" for theme, verbs in themes.items() if not verbs]
    errors += [f"{theme}: повторы" for theme, verbs in themes.items() if len(set(verbs)) != len(verbs)]
    if errors:
        raise ValueError(f"Ошибки в {path.name}:\n" + "\n".join(f"  - {error}" for error in errors))
    return themes


def load_frequency(path: Path, infinitives: list[str]) -> list[str]:
    """Читает порядок глаголов по частоте и проверяет, что в нём ровно глаголы из списка"""
    with open(path, "r", encoding="utf-8") as f:
        ranked = json.load(f)
    if len(ranked) != len(set(ranked)) or set(ranked) != set(infinitives):
        missing = sorted(set(infinitives) - set(ranked))
        extra = sorted(set(ranked) - set(infinitives))
        raise ValueError(
            f"{path.name} не совпадает со списком глаголов (python scripts/rank_verbs.py): "
            f"нет {', '.join(missing) or '—'}; лишние {', '.join(extra) or '—'}; повторы: {len(ranked) - len(set(ranked))}"
        )
    return ranked


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def build(out_dir: Path) -> None:
    with open(CONJUGATIONS_FILE, "r", encoding="utf-8") as f:
        conjugations = json.load(f)
    tenses = conjugations["tenses"]
    by_verb = dict(sorted(conjugations["verbs"].items()))
    if not tenses or not by_verb:
        raise ValueError(f"В {CONJUGATIONS_FILE.name} не найдено данных")

    by_tense: dict[str, dict[str, str | dict[str, str]]] = {tense["id"]: {} for tense in tenses}
    for infinitive, verb_tenses in by_verb.items():
        for tense_id, built in verb_tenses.items():
            by_tense[tense_id][infinitive] = built

    translations = {lang: load_translations(path, list(by_verb)) for lang, path in TRANSLATION_FILES.items()}
    themes = load_themes(THEMES_FILE, list(by_verb))
    frequency = load_frequency(FREQUENCY_FILE, list(by_verb))

    if out_dir.exists():
        shutil.rmtree(out_dir)

    write_json(
        out_dir / "index.json",
        {"verbs": list(by_verb), "tenses": tenses, "persons": PERSONS, "translations": list(translations)},
    )

    for infinitive, verb_tenses in by_verb.items():
        verb_translations = {lang: values[infinitive] for lang, values in translations.items()}
        write_json(
            out_dir / "verbs" / f"{infinitive}.json",
            {"infinitive": infinitive, "translations": verb_translations, "tenses": verb_tenses},
        )

    write_json(out_dir / "themes.json", themes)
    write_json(out_dir / "frequency.json", frequency)

    for lang, values in translations.items():
        write_json(out_dir / "translations" / f"{lang}.json", values)

    for tense in tenses:
        write_json(out_dir / "tenses" / f"{tense['id']}.json", {**tense, "verbs": by_tense[tense["id"]]})

    print(f"Готово: {len(by_verb)} глаголов, {len(tenses)} времён -> {out_dir}")


if __name__ == "__main__":
    try:
        build(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist")
    except ValueError as error:
        sys.exit(f"Сборка не удалась: {error}")
