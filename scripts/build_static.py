"""
Сборка статических JSON-файлов с глаголами из SQL-дампа и файлов переводов.

Результат (по умолчанию в dist/):
    index.json               — список глаголов, времён, лиц и языков перевода
    verbs/{infinitive}.json  — все формы и переводы одного глагола
    tenses/{id}.json         — одно время для всех глаголов
    translations/{lang}.json — переводы всех глаголов на один язык

Запуск: python scripts/build_static.py [папка_результата]
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).parent.parent
SEED_FILE = ROOT / "data" / "verbs_seed.sql"
TRANSLATION_FILES = {"ru": ROOT / "data" / "translations_ru.json"}
MAX_TRANSLATIONS = 3

VERB_RE = re.compile(r"INSERT INTO public\.verbs \(id, infinitive, created_at\) VALUES \((\d+), '([^']*)',")
FORM_RE = re.compile(
    r"INSERT INTO public\.verb_forms \(id, verb_id, tense, person, auxiliary_verb, verb_form, created_at\) "
    r"VALUES \(\d+, (\d+), '([^']*)', '([^']*)', (NULL|'[^']*'), '([^']*)',"
)

PERSONS = ["1s", "2s", "3s", "1p", "2p", "3p"]

# В дампе лица проставлены по порядку форм, а не по смыслу, поэтому для
# неполных наборов восстанавливаем настоящие лица по количеству форм
IMPERATIVE = "Imperativo"
IMPERATIVE_PERSONS = ["2s", "3s", "1p", "2p", "3p"]
DEFECTIVE_PERSONS = {1: ["3s"], 2: ["3s", "3p"], 6: PERSONS}
NON_PERSONAL = {"Gerundio", "Gerundio compuesto", "Infinitivo", "Infinitivo compuesto", "Participio Pasado"}


def slugify(name: str) -> str:
    """'Subjuntivo Pretérito imperfecto (2)' -> 'subjuntivo-preterito-imperfecto-2'"""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


def parse_seed(path: Path) -> tuple[dict[int, str], dict[int, dict[str, list[tuple[str, str]]]]]:
    """
    Читает дамп и возвращает инфинитивы по id и формы в виде
    {verb_id: {название времени: [(лицо, форма), ...]}}
    """
    verbs: dict[int, str] = {}
    forms: dict[int, dict[str, list[tuple[str, str]]]] = {}

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if match := VERB_RE.match(line):
                verbs[int(match[1])] = unicodedata.normalize("NFC", match[2])
            elif match := FORM_RE.match(line):
                verb_id, tense, person, aux, verb_form = match.groups()
                if aux != "NULL":
                    verb_form = f"{aux[1:-1]} {verb_form}"
                forms.setdefault(int(verb_id), {}).setdefault(tense, []).append((person, verb_form))

    return verbs, forms


def build_tense(infinitive: str, tense: str, forms: list[tuple[str, str]]) -> str | dict[str, str]:
    """Собирает одно время глагола: строку для неличных форм, {лицо: форма} для остальных"""
    values = [form for _, form in sorted(forms, key=lambda item: PERSONS.index(item[0]))]

    if tense in NON_PERSONAL:
        if len(values) != 1:
            raise ValueError(f"{infinitive} / {tense}: ожидалась одна форма, найдено {len(values)}")
        return values[0]

    persons = IMPERATIVE_PERSONS if tense == IMPERATIVE else DEFECTIVE_PERSONS.get(len(values))
    if persons is None or len(persons) != len(values):
        raise ValueError(f"{infinitive} / {tense}: неожиданное количество форм ({len(values)})")
    return dict(zip(persons, values))


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


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def build(out_dir: Path) -> None:
    verbs, forms = parse_seed(SEED_FILE)
    if not verbs or not forms:
        raise ValueError(f"В {SEED_FILE.name} не найдено данных")

    tense_ids: dict[str, str] = {}
    by_verb: dict[str, dict[str, str | dict[str, str]]] = {}
    by_tense: dict[str, dict[str, str | dict[str, str]]] = {}

    for verb_id, infinitive in sorted(verbs.items(), key=lambda item: item[1]):
        by_verb[infinitive] = {}
        for tense, tense_forms in forms.get(verb_id, {}).items():
            tense_id = tense_ids.setdefault(tense, slugify(tense))
            built = build_tense(infinitive, tense, tense_forms)
            by_verb[infinitive][tense_id] = built
            by_tense.setdefault(tense_id, {})[infinitive] = built

    if len(set(tense_ids.values())) != len(tense_ids):
        raise ValueError("Разные времена дали одинаковый id")

    translations = {lang: load_translations(path, list(by_verb)) for lang, path in TRANSLATION_FILES.items()}

    if out_dir.exists():
        shutil.rmtree(out_dir)

    tenses = [
        {"id": tense_id, "name": name, "personal": name not in NON_PERSONAL}
        for name, tense_id in tense_ids.items()
    ]
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
