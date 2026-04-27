import { clickByAnyText, expectText, fillFirstMatchingInput, openApp } from './helpers.js';
import { defineScenarioSuite } from './scenarioRunner.js';

const maxInterestTags = [
  'кино', 'музыка', 'книги', 'театр', 'аниме', 'спорт', 'сладости',
  'мультфильмы', 'фэнтези', 'фотография', 'научпоп', 'саморазвитие',
  'иностранные языки', 'компьютерные игры', 'настольные игры', 'рукоделие',
  'сад и огород', 'домашний декор', 'танцы', 'робототехника', 'программирование',
];
const maxNoGiftTags = [
  'мягкие игрушки', 'пластиковые сувениры', 'ароматические свечи', 'канцелярия',
  'магниты', 'плакаты', 'брелоки', 'ежедневники', 'статуэтки', 'открытки',
  'календари',
];

async function openQuestionnaire(driver, By, until, baseUrl) {
  await openApp(driver, baseUrl);
  await clickByAnyText(driver, By, until, ['Анкета', 'Посмотреть анкету']);
}

defineScenarioSuite('Questionnaire E2E scenarios', [
  {
    number: 13,
    title: 'Успешное заполнение анкеты',
    requirements: ['FS-5.1', 'FS-5.2', 'FS-5.6'],
    requires: ['authenticated'],
    run: async ({ driver, By, until, baseUrl }) => {
      await openQuestionnaire(driver, By, until, baseUrl);
      await clickByAnyText(driver, By, until, ['кино']);
      await clickByAnyText(driver, By, until, ['музыка']);
      await clickByAnyText(driver, By, until, ['книги']);
      await clickByAnyText(driver, By, until, ['мягкие игрушки']);
      await clickByAnyText(driver, By, until, ['Сохранить анкету']);
      await expectText(driver, By, until, 'Анкета успешно сохранена');
    },
  },
]);
