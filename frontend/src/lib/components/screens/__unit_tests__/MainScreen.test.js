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

  test('renders totals and empty states when stores are empty', () => {
    totalWishesStore.set(9);
    totalWishlistsStore.set(3);
    totalSubscriptionsStore.set(4);
    totalSubscribersStore.set(5);

    const { container } = renderMainScreen();

    expect(container.querySelector('.ghost-link')?.textContent).toContain('(9)');

    const sectionTitles = Array.from(container.querySelectorAll('.h2')).map((node) =>
      node.textContent?.trim() || ''
    );

    expect(sectionTitles[0]).toContain('(3)');
    expect(sectionTitles[1]).toContain('(4)');
    expect(sectionTitles[2]).toContain('(5)');

    expect(container.querySelectorAll('.empty-note')).toHaveLength(3);
  });
});
