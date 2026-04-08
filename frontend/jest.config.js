/** @type {import('jest').Config} */
export default {
  // Среда выполнения тестов (эмулирует браузер)
  testEnvironment: 'jsdom',

  // Трансформация файлов перед тестами
  transform: {
    '^.+\\.svelte$': ['svelte-jester', { preprocess: true }],
    '^.+\\.ts$': ['ts-jest', { useESM: true }],
    '^.+\\.js$': 'babel-jest'
  },

  // Расширения файлов, которые Jest должен обрабатывать
  moduleFileExtensions: ['js', 'ts', 'svelte'],

  // Глобальные настройки перед каждым тестом
  setupFilesAfterEnv: ['@testing-library/jest-dom'],

  // Указываем, что .ts и .svelte файлы нужно обрабатывать как ESM
  extensionsToTreatAsEsm: ['.ts', '.svelte'],

  // Исправляет проблему импорта .js файлов в ESM-режиме
  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1'
  },

  // Исключаем node_modules из трансформации, кроме Svelte-пакетов
  transformIgnorePatterns: [
    'node_modules/(?!(svelte|@testing-library/svelte|svelte-jester)/)'
  ],

  // === Настройки покрытия кода ===
  collectCoverage: true,
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.{js,ts,svelte}',
    '!src/**/*.d.ts',
    '!src/main.js',
    '!src/app.css',
    '!**/node_modules/**',
    '!**/__tests__/**'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};