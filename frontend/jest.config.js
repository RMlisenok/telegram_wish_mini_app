/** @type {import('jest').Config} */
export default {
  testEnvironment: 'jsdom',
  clearMocks: true,
  restoreMocks: true,
  roots: ['<rootDir>/src'],
  testPathIgnorePatterns: ['/node_modules/', '/coverage/'],
  transform: {
    '^.+\\.svelte\\.(js|ts)$': ['svelte-jester', { preprocess: false, compilerOptions: { css: 'external' } }],
    '^.+\\.svelte$': ['svelte-jester', { preprocess: false, compilerOptions: { css: 'external' } }],
    '^.+\\.ts$': ['ts-jest', { useESM: true }],
    '^.+\\.js$': 'babel-jest'
  },
  moduleFileExtensions: ['js', 'ts', 'svelte'],
  setupFilesAfterEnv: ['@testing-library/jest-dom'],
  extensionsToTreatAsEsm: ['.ts', '.svelte'],
  moduleNameMapper: {
    '^(\\.{1,2}/.*)\\.js$': '$1'
  },
  transformIgnorePatterns: [
    'node_modules/(?!(svelte|@testing-library/svelte|@testing-library/svelte-core|svelte-jester)/)'
  ],
  collectCoverage: false,
  coverageProvider: 'v8',
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.{js,ts,svelte}',
    '!src/**/*.d.ts',
    '!src/main.js',
    '!src/app.css',
    '!src/**/*.test.{js,ts}',
    '!src/**/*.spec.{js,ts}',
    '!**/node_modules/**',
    '!**/__tests__/**',
    '!**/__unit_tests__/**'
  ]
};
