import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, waitFor } from '@testing-library/svelte';

import WishesScreenEdit from '../WishesScreen_Edit.svelte';
import { wishlistsStore } from '../../../../types/wishlists.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

describe('WishesScreen_Edit', () => {
  beforeEach(() => {
    wishlistsStore.set([]);
    global.fetch = jest.fn();
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  test('shows validation error and does not save when title is empty', async () => {
    const onGoBack = jest.fn();

    const { container } = render(WishesScreenEdit, {
      token: '',
      wishId: '42',
      onGoBack
    });

    const saveButton = container.querySelectorAll('.form-actions .ui-button')[1];
    await fireEvent.click(saveButton);

    expect(container.querySelector('.field-error')).toBeTruthy();
    expect(global.fetch).not.toHaveBeenCalled();
    expect(onGoBack).not.toHaveBeenCalled();
  });
});
