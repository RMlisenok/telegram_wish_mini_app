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

  test('shows only first three wishlists', () => {
    mainWishlistsStore.set([
      {
        id: 'wl-1',
        name: 'Wishlist 1',
        description: 'First',
        photo: '',
        typeprivacy: 'public',
        created_at: '2026-01-01T00:00:00.000Z',
        updated_at: '2026-01-01T00:00:00.000Z',
        count: 2
      },
      {
        id: 'wl-2',
        name: 'Wishlist 2',
        description: 'Second',
        photo: '',
        typeprivacy: 'restricted',
        created_at: '2026-01-02T00:00:00.000Z',
        updated_at: '2026-01-02T00:00:00.000Z',
        count: 5
      },
      {
        id: 'wl-3',
        name: 'Wishlist 3',
        description: 'Third',
        photo: '',
        typeprivacy: 'private',
        created_at: '2026-01-03T00:00:00.000Z',
        updated_at: '2026-01-03T00:00:00.000Z',
        count: 7
      },
      {
        id: 'wl-4',
        name: 'Wishlist 4',
        description: 'Fourth',
        photo: '',
        typeprivacy: 'public',
        created_at: '2026-01-04T00:00:00.000Z',
        updated_at: '2026-01-04T00:00:00.000Z',
        count: 1
      }
    ]);

    const { container } = renderMainScreen();

    expect(container.querySelectorAll('.wishlist-row')).toHaveLength(3);
    expect(screen.getByText('Wishlist 1')).toBeInTheDocument();
    expect(screen.getByText('Wishlist 2')).toBeInTheDocument();
    expect(screen.getByText('Wishlist 3')).toBeInTheDocument();
    expect(screen.queryByText('Wishlist 4')).not.toBeInTheDocument();
  });

  test('shows only first two subscriptions', () => {
    mainSubscriptionsStore.set([
      {
        type_sub: true,
        user: {
          name: 'Alice',
          photo: '',
          user_id: 10,
          birth_date: '03.03.1993'
        }
      },
      {
        type_sub: false,
        wishlist: {
          name: 'Travel Wishlist',
          photo: '',
          description: 'Trips',
          typeprivacy: 'public',
          owner_name: 'Max',
          id: 99,
          count: 6
        }
      },
      {
        type_sub: true,
        user: {
          name: 'Bob',
          photo: '',
          user_id: 11,
          birth_date: '04.04.1994'
        }
      }
    ]);

    renderMainScreen();

    expect(screen.getByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Travel Wishlist')).toBeInTheDocument();
    expect(screen.queryByText('Bob')).not.toBeInTheDocument();
  });
});
