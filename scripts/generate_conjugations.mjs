// Генерирует data/conjugations.json — спряжения всех глаголов из data/verbs.json.
// По нему scripts/build_static.py собирает dist/.
// Запуск: npm run generate
import { readFile, writeFile } from 'node:fs/promises';

import { TENSES, conjugate, isPersonal, knownVerbs } from './conjugate.mjs';

const DATA_DIR = new URL('../data/', import.meta.url);

const verbs = JSON.parse(await readFile(new URL('verbs.json', DATA_DIR), 'utf8'));

const known = new Set(knownVerbs());
const unknown = verbs.filter((verb) => !known.has(verb));
if (unknown.length > 0) throw new Error(`Нет в conjugate-esp: ${unknown.join(', ')}`);

const tenses = TENSES.map(({ id, name }) => ({ id, name, personal: isPersonal(id) }));
// Один глагол на строку: файл большой, а так его диффы читаются
const lines = verbs.map((verb) => `    ${JSON.stringify(verb)}: ${JSON.stringify(conjugate(verb))}`);

await writeFile(
  new URL('conjugations.json', DATA_DIR),
  `{\n  "tenses": ${JSON.stringify(tenses)},\n  "verbs": {\n${lines.join(',\n')}\n  }\n}\n`
);
console.log(`Готово: ${verbs.length} глаголов`);
