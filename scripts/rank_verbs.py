"""
Пишет data/frequency.json — все глаголы из data/verbs.json от частых к редким.

Частота — как при отборе глаголов в select_verbs.py: инфинитив вместе с возвратной
формой (quedar + quedarse) по данным wordfreq (https://github.com/rspeer/wordfreq,
данные CC BY-SA 4.0). Приложение по этому порядку чаще показывает частые глаголы
в быстрой тренировке.

Запуск (нужен pip install wordfreq): python scripts/rank_verbs.py
"""
from __future__ import annotations

import json
from pathlib import Path

from wordfreq import word_frequency

ROOT = Path(__file__).parent.parent
VERBS_FILE = ROOT / "data" / "verbs.json"
FREQUENCY_FILE = ROOT / "data" / "frequency.json"


def main() -> None:
    verbs = json.loads(VERBS_FILE.read_text(encoding="utf-8"))
    # При равной частоте — по алфавиту, чтобы файл не менялся от запуска к запуску
    ranked = sorted(verbs, key=lambda verb: (-(word_frequency(verb, "es") + word_frequency(verb + "se", "es")), verb))
    FREQUENCY_FILE.write_text("[\n" + ",\n".join(f'  "{verb}"' for verb in ranked) + "\n]\n", encoding="utf-8")
    print(f"Готово: {len(ranked)} глаголов, первые: {', '.join(ranked[:10])}")


if __name__ == "__main__":
    main()
