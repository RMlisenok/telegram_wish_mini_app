/** @type {import('jest').Config} */
export default {
  testEnvironment: 'node',
  testMatch: ['<rootDir>/selenium/**/*.test.js'],
  testTimeout: 60000,
  clearMocks: true,
  restoreMocks: true,
  transform: {},
};
