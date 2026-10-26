// Спряжение одного глагола во всех 24 временах API по данным conjugate-esp (MIT,
// https://github.com/jirimracek/conjugate-esp).
//
// Формат как в dist/: личные времена — {лицо: форма}, неличные формы — строка.
// Если допустимых вариантов несколько, они идут через слэш, первым — основной:
// «freído/frito», «guiais/guiáis». В составных формах слэш относится только
// к последнему слову: «he freído/frito».
import { Conjugator } from '@jirimracek/conjugate-esp';

export const PERSONS = ['1s', '2s', '3s', '1p', '2p', '3p'];

// id и названия времён — те же, что раньше были в базе; source — где время лежит в conjugate-esp
export const TENSES = [
  { id: 'indicativo-presente', name: 'Indicativo Presente', source: ['Indicativo', 'Presente'] },
  { id: 'indicativo-futuro', name: 'Indicativo Futuro', source: ['Indicativo', 'FuturoImperfecto'] },
  { id: 'indicativo-preterito-imperfecto', name: 'Indicativo Pretérito imperfecto', source: ['Indicativo', 'PreteritoImperfecto'] },
  { id: 'indicativo-preterito-perfecto-compuesto', name: 'Indicativo Pretérito perfecto compuesto', source: ['Indicativo', 'PreteritoPerfecto'] },
  { id: 'indicativo-preterito-pluscuamperfecto', name: 'Indicativo Pretérito pluscuamperfecto', source: ['Indicativo', 'PreteritoPluscuamperfecto'] },
  { id: 'indicativo-preterito-anterior', name: 'Indicativo Pretérito anterior', source: ['Indicativo', 'PreteritoAnterior'] },
  { id: 'indicativo-futuro-perfecto', name: 'Indicativo Futuro perfecto', source: ['Indicativo', 'FuturoPerfecto'] },
  { id: 'indicativo-condicional-perfecto', name: 'Indicativo Condicional perfecto', source: ['Indicativo', 'CondicionalCompuesto'] },
  { id: 'indicativo-condicional', name: 'Indicativo Condicional', source: ['Indicativo', 'CondicionalSimple'] },
  { id: 'indicativo-preterito-perfecto-simple', name: 'Indicativo Pretérito perfecto simple', source: ['Indicativo', 'PreteritoIndefinido'] },
  { id: 'imperativo', name: 'Imperativo', source: ['Imperativo', 'Afirmativo'] },
  { id: 'subjuntivo-presente', name: 'Subjuntivo Presente', source: ['Subjuntivo', 'Presente'] },
  { id: 'subjuntivo-futuro', name: 'Subjuntivo Futuro', source: ['Subjuntivo', 'FuturoImperfecto'] },
  { id: 'subjuntivo-preterito-imperfecto', name: 'Subjuntivo Pretérito imperfecto', source: ['Subjuntivo', 'PreteritoImperfectoRa'] },
  { id: 'subjuntivo-preterito-pluscuamperfecto', name: 'Subjuntivo Pretérito pluscuamperfecto', source: ['Subjuntivo', 'PreteritoPluscuamperfectoRa'] },
  { id: 'subjuntivo-futuro-perfecto', name: 'Subjuntivo Futuro perfecto', source: ['Subjuntivo', 'FuturoPerfecto'] },
  { id: 'subjuntivo-preterito-imperfecto-2', name: 'Subjuntivo Pretérito imperfecto (2)', source: ['Subjuntivo', 'PreteritoImperfectoSe'] },
  { id: 'subjuntivo-preterito-pluscuamperfecto-2', name: 'Subjuntivo Pretérito pluscuamperfecto (2)', source: ['Subjuntivo', 'PreteritoPluscuamperfectoSe'] },
  { id: 'subjuntivo-preterito-perfecto', name: 'Subjuntivo Pretérito perfecto', source: ['Subjuntivo', 'PreteritoPerfecto'] },
  { id: 'gerundio', name: 'Gerundio', source: ['Impersonal', 'Gerundio'] },
  { id: 'gerundio-compuesto', name: 'Gerundio compuesto', auxiliary: 'habiendo' },
  { id: 'infinitivo', name: 'Infinitivo', source: ['Impersonal', 'Infinitivo'] },
  { id: 'infinitivo-compuesto', name: 'Infinitivo compuesto', auxiliary: 'haber' },
  { id: 'participio-pasado', name: 'Participio Pasado', source: ['Impersonal', 'Participio'] },
];

const NON_PERSONAL = new Set(['gerundio', 'gerundio-compuesto', 'infinitivo', 'infinitivo-compuesto', 'participio-pasado']);
export const isPersonal = (tenseId) => !NON_PERSONAL.has(tenseId);

// Императив в conjugate-esp — шесть позиций [-, tú, -, nosotros, vosotros, -],
// а формы usted/ustedes есть только в региональном режиме formal на местах tú и vosotros
const IMPERATIVE = {
  '2s': ['castellano', 1],
  '3s': ['formal', 1],
  '1p': ['castellano', 3],
  '2p': ['castellano', 4],
  '3p': ['formal', 4],
};

// Ручные поправки поверх conjugate-esp:
// «¡Vamos!» — самая частая форма императива ir для nosotros, RAE её допускает, а conjugate-esp даёт только vayamos;
// hay — безличная форма haber в настоящем времени, её тоже надо принимать
const OVERRIDES = {
  ir: { imperativo: { '1p': ['vamos', 'vayamos'] } },
  haber: { 'indicativo-presente': { '3s': ['ha', 'hay'] } },
};

// У части глаголов в conjugate-esp несколько моделей спряжения. Здесь — какие оставить
// и в каком порядке (первая — основная), по «Diccionario panhispánico de dudas» RAE.
// Одна модель — вторая архаичная, ошибочная или относится к редкому значению
// (apostar «расставлять посты» → aposto); две — RAE допускает обе.
// Глагол с несколькими моделями, которого здесь нет, остановит генерацию
const MODELS = {
  acostar: ['contar'],
  adecuar: ['hablar', 'actuar'],
  apostar: ['contar'],
  arrendar: ['acertar', 'hablar'],
  asestar: ['hablar'],
  atentar: ['hablar'],
  auxiliar: ['hablar', 'vaciar'],
  cimentar: ['hablar', 'acertar'],
  colar: ['contar'],
  derrocar: ['sacar'],
  desmembrar: ['acertar', 'hablar'],
  engrosar: ['hablar', 'contar'],
  errar: ['errar', 'hablar'],
  evacuar: ['hablar', 'actuar'],
  homogeneizar: ['enraizar'],
  licuar: ['hablar', 'actuar'],
  mecer: ['vencer'],
  paliar: ['hablar', 'vaciar'],
  reinar: ['hablar'],
  repatriar: ['vaciar', 'hablar'],
  responder: ['temer'],
  templar: ['hablar', 'acertar'],
};

// Орфография 1999 года: conjugate-esp отдаёт и новые написания 2010 года (guiais),
// и старые (guiáis) — принимаем оба, новые идут первыми
const conjugator = new Conjugator('1999');
conjugator.useHighlight(false);

// conjugate-esp даёт им и полное спряжение, но в живом языке они употребляются только
// в 3-м лице: «yo ataño» на карточке выглядело бы странно
const DEFECTIVE_ONLY = new Set(['atañer']);

// Полные спряжения, а если глагол только недостаточный (soler) — то, что есть
const results = (verb, region) => {
  const all = conjugator.conjugateSync(verb, region);
  if (typeof all === 'string') throw new Error(`${verb}: ${all}`);
  const full = all.filter(({ info }) => !info.defective);
  const defective = all.filter(({ info }) => info.defective);
  const chosen = DEFECTIVE_ONLY.has(verb) ? defective : full.length > 0 ? full : all;

  const models = [...new Set(chosen.map(({ info }) => info.model))];
  if (models.length > 1 && !MODELS[verb]) {
    throw new Error(`${verb}: несколько моделей спряжения (${models.join(', ')}) — выбери нужные в MODELS`);
  }
  const order = MODELS[verb] ?? models;
  return order.flatMap((model) => chosen.filter(({ info }) => info.model === model)).map(({ conjugation }) => conjugation);
};

// conjugate-esp тоже пишет варианты через слэш, и в составных формах слэш относится
// к последнему слову: 'he descrito/descripto' → ['he descrito', 'he descripto']
const splitValue = (value) => {
  const [first, ...rest] = String(value).split(/[/,]/).map((part) => part.trim());
  const prefix = first.split(' ').slice(0, -1).join(' ');
  return [first, ...rest.map((part) => (prefix && !part.includes(' ') ? `${prefix} ${part}` : part))];
};

const cleanVariants = (values) => [
  ...new Set(values.flatMap(splitValue).filter((value) => value && value !== '-' && !value.endsWith(' -'))),
];

// ['he freído', 'he frito'] → 'he freído/frito'
const joinVariants = (verb, tenseId, variants) => {
  if (variants.length === 0) return null;
  const prefixes = new Set(variants.map((variant) => variant.split(' ').slice(0, -1).join(' ')));
  if (prefixes.size > 1) throw new Error(`${verb} / ${tenseId}: варианты расходятся не только в последнем слове: ${variants.join(', ')}`);
  const [prefix] = prefixes;
  const lastWords = variants.map((variant) => variant.split(' ').at(-1));
  return prefix ? `${prefix} ${lastWords.join('/')}` : lastWords.join('/');
};

export const conjugate = (verb) => {
  const regions = { castellano: results(verb, 'castellano'), formal: results(verb, 'formal') };
  const overrides = OVERRIDES[verb] ?? {};
  const tenses = {};

  for (const tense of TENSES) {
    const pick = (person) => {
      if (overrides[tense.id]?.[person]) return overrides[tense.id][person];
      if (tense.auxiliary) return regions.castellano.map((c) => `${tense.auxiliary} ${c.Impersonal.Participio}`);
      if (tense.id === 'imperativo') {
        const [region, index] = IMPERATIVE[person];
        return regions[region].map((c) => c.Imperativo.Afirmativo[index]);
      }
      const [mood, key] = tense.source;
      return regions.castellano.map((c) => (person ? c[mood][key][PERSONS.indexOf(person)] : c[mood][key]));
    };

    if (!isPersonal(tense.id)) {
      const value = joinVariants(verb, tense.id, cleanVariants(pick(null)));
      if (value) tenses[tense.id] = value;
      continue;
    }

    const persons = tense.id === 'imperativo' ? Object.keys(IMPERATIVE) : PERSONS;
    const forms = {};
    for (const person of persons) {
      const value = joinVariants(verb, tense.id, cleanVariants(pick(person)));
      if (value) forms[person] = value;
    }
    if (Object.keys(forms).length > 0) tenses[tense.id] = forms;
  }

  return tenses;
};

export const knownVerbs = () => conjugator.getVerbListSync();
