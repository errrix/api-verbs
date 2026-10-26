// Печатает в stdout JSON {глагол: [формы]} для всех глаголов conjugate-esp: только формы,
// которые бывают лишь у глагола (герундий, претерит, имперфект и будущее 3-го лица).
// Нужен scripts/select_verbs.py, чтобы отличить глагол от омонима-прилагательного (militar)
import { conjugate, knownVerbs } from './conjugate.mjs';

const VERBAL = {
  'indicativo-preterito-perfecto-simple': ['3s', '3p'],
  'indicativo-preterito-imperfecto': ['3s', '3p'],
  'indicativo-futuro': ['3s', '3p'],
};

const result = {};
for (const verb of knownVerbs()) {
  let tenses;
  try {
    tenses = conjugate(verb);
  } catch (error) {
    console.error(`Пропускаю: ${error.message}`);
    continue;
  }
  const values = [tenses.gerundio, ...Object.entries(VERBAL).flatMap(([id, persons]) => persons.map((p) => tenses[id]?.[p]))];
  // Только простые формы: у возвратных глаголов формы с местоимением («se lavó») пропускаем
  result[verb] = [...new Set(values.filter(Boolean).flatMap((value) => value.split('/')).filter((form) => !form.includes(' ')))];
}
process.stdout.write(JSON.stringify(result));
