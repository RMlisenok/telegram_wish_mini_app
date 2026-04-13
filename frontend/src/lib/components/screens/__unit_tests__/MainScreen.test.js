import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, screen } from '@testing-library/svelte';

import MainScreen from '../MainScreen.svelte';
import MainScreenEventHarness from './MainScreenEventHarness.svelte';
import {
  mainSubscribersStore,
  mainSubscriptionsStore,
  mainWishlistsStore,
  totalSubscribersStore,
  totalSubscriptionsStore,
  totalWishesStore,
  totalWishlistsStore
} from '../../../../types/mainScreenData.ts';

const baseUser = {
  fullName: 'John Doe',
  birthDate: '01.01.1990',
  avatarUrl: ''
};

function resetMainScreenStores() {
  mainWishlistsStore.set([]);
  mainSubscriptionsStore.set([]);
  mainSubscribersStore.set([]);

  totalWishesStore.set(0);
  totalWishlistsStore.set(0);
  totalSubscriptionsStore.set(0);
  totalSubscribersStore.set(0);
}

function renderMainScreen(props = {}) {
  return render(MainScreen, {
    token: '',
    user: baseUser,
    ...props
  });
}

describe('MainScreen', () => {
  beforeEach(() => {
    resetMainScreenStores();
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  test('renders user information and avatar initials fallback', () => {
    renderMainScreen();

    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('01.01.1990')).toBeInTheDocument();
    expect(screen.getByText('JD')).toBeInTheDocument();
  });
});
