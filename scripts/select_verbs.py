"""
Дополняет data/verbs.json самыми частыми глаголами до нужного количества.

Глаголы, которые уже есть в списке, остаются всегда: по ним у пользователей может
быть прогресс. Новые берутся из conjugate-esp по убыванию частоты инфинитива
(вместе с возвратной формой: quedar + quedarse) по данным wordfreq
(https://github.com/rspeer/wordfreq, данные CC BY-SA 4.0).

Отсекаются:
  - омонимы, которые почти не встречаются в глагольных формах (militar, popular, nuclear);
  - только возвратные глаголы (arrepentirse): карточки не спрашивают формы с местоимением;
  - грубые слова и то, что исключено вручную, — списки EXCLUDED ниже.

Запуск (нужны node и wordfreq: pip install wordfreq):
    python scripts/select_verbs.py [количество]
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from wordfreq import word_frequency

ROOT = Path(__file__).parent.parent
VERBS_FILE = ROOT / "data" / "verbs.json"
DEFAULT_TARGET = 2500

# Доля частоты глагольных форм от частоты инфинитива, ниже которой слово считаем омонимом.
# У глаголов из первой тысячи она почти всегда больше 0,05, у militar или nuclear — около нуля
MIN_VERBAL_RATIO = 0.02

# Грубые и откровенно сексуальные слова: из-за них у приложения поднялся бы возрастной рейтинг
EXCLUDED_VULGAR = {
    "boludear", "cagar", "chingar", "copular", "culear", "eyacular", "follar", "fornicar", "joder",
    "mamar", "masturbar", "mear", "pajear", "prostituir", "putear",
}

# Исключены при ручной проверке списка: архаизмы, узкие регионализмы, слова, которые
# почти всегда встречаются в другом значении
EXCLUDED_MANUAL = {"aviar", "chamuyar", "morfar", "petar", "transar", "vivar"}


def frequency(word: str) -> float:
    return word_frequency(word, "es")


def load_verbal_forms() -> dict[str, list[str]]:
    result = subprocess.run(
        ["node", str(ROOT / "scripts" / "dump_verb_forms.mjs")], check=True, capture_output=True, text=True
    )
    return json.loads(result.stdout)


def rank(verbal_forms: dict[str, list[str]]) -> list[str]:
    """Глаголы без возвратных дублей, от частых к редким"""
    known = set(verbal_forms)
    bases = [verb for verb in known if not (verb.endswith("se") and verb[:-2] in known)]
    return sorted(bases, key=lambda verb: frequency(verb) + frequency(verb + "se"), reverse=True)


def verbal_ratio(verb: str, verbal_forms: dict[str, list[str]], owners: Counter[str]) -> float:
    """Сколько частоты приходится на однозначно глагольные формы относительно инфинитива"""
    infinitive = frequency(verb) + frequency(verb + "se")
    if infinitive == 0:
        return 0
    forms = set(verbal_forms.get(verb, [])) | set(verbal_forms.get(verb + "se", []))
    # Форма, общая для нескольких глаголов (fue: ir и ser), ни про один из них ничего не говорит
    return sum(frequency(form) for form in forms if owners[form] == 1) / infinitive


def select(current: list[str], target: int) -> list[str]:
    verbal_forms = load_verbal_forms()
    owners = Counter(form for forms in verbal_forms.values() for form in set(forms))
    selected = set(current)
    added: list[str] = []

    for verb in rank(verbal_forms):
        if len(selected) >= target:
            break
        if verb in selected or verb in EXCLUDED_VULGAR or verb in EXCLUDED_MANUAL:
            continue
        if verb.endswith("se") or verbal_ratio(verb, verbal_forms, owners) < MIN_VERBAL_RATIO:
            continue
        selected.add(verb)
        added.append(verb)

    print(f"Было {len(current)}, добавлено {len(added)}, стало {len(selected)}")
    print("Добавлены (от частых к редким):", " ".join(added))
    return sorted(selected)


def main() -> None:
    target = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TARGET
    current = json.loads(VERBS_FILE.read_text(encoding="utf-8"))
    verbs = select(current, target)
    VERBS_FILE.write_text("[\n" + ",\n".join(f'  "{verb}"' for verb in verbs) + "\n]\n", encoding="utf-8")


if __name__ == "__main__":
    main()
