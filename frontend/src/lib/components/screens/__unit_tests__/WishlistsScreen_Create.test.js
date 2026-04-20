import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, waitFor } from '@testing-library/svelte';

import WishlistsScreenCreate from '../WishlistsScreen_Create.svelte';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data
});

describe('WishlistsScreen_Create', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });
});
