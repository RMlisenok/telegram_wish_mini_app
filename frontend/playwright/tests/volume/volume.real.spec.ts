import { test, expect, request } from '@playwright/test';
import { ensureRealToken, realEnv, shouldRunRealE2E } from '../lib/auth';
import { clickByPossibleSelectors, fillByPossibleSelectors } from '../lib/ui';

const env = realEnv();

test.describe('Real UI/API E2E volume tests / Реальные объёмные E2E тесты', () => {
  test.skip(!shouldRunRealE2E(), 'PW_BASE_URL + auth data are required.');

  async function createApiContext() {
    const token = await ensureRealToken(env);
    return await request.newContext({
      baseURL: env.baseUrl,
      extraHTTPHeaders: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      ignoreHTTPSErrors: true,
    });
  }

  async function createWish(api, suffix = '') {
    const response = await api.post('/api/v1/wishes/', {
      data: {
        name: `PW Volume Wish ${suffix}${Date.now()}`.slice(0, 100),
        url_gift: 'https://example.com/volume-wish',
        price: 999999.99,
        currency: 'USD',
        description: 'B'.repeat(200),
      },
    });
    expect([200, 201]).toContain(response.status());
    return await response.json();
  }

  async function createWishlist(api, suffix = '') {
    const response = await api.post('/api/v1/wishlists/', {
      data: {
        name: `PW Volume Wishlist ${suffix}${Date.now()}`.slice(0, 50),
        description: 'C'.repeat(100),
        typeprivacy: 'public',
      },
    });
    expect([200, 201]).toContain(response.status());
    return await response.json();
  }

  async function connectWishToWishlist(api, wishlistId, wishId) {
    const response = await api.post(`/api/v1/wishlists/${wishlistId}/wishes`, {
      data: {
        is_pinned: false,
        order_position: 1,
        wish_id: wishId,
        wishlist_id: wishlistId,
      },
    });
    expect([200, 201]).toContain(response.status());
    return await response.json();
  }

  test('01. Large profile update payload / Большой payload обновления профиля', async () => {
    const api = await createApiContext();
    const response = await api.put('/api/v1/users/me', {
      data: {
        name: `PW-${Date.now()}`.slice(0, 40),
        birth_date: '1999-01-01',
        photo: 'https://example.com/playwright-profile-photo.png',
      },
    });
    expect([200, 201]).toContain(response.status());
    await api.dispose();
  });

  test('02. Read current user after update / Чтение текущего пользователя после обновления', async () => {
    const api = await createApiContext();
    const response = await api.get('/api/v1/users/me');
    expect(response.ok()).toBeTruthy();
    const data = await response.json().catch(() => null);
    expect(data).not.toBeNull();
    await api.dispose();
  });

  test('03. Large questionnaire payload / Большой payload анкеты', async () => {
    const api = await createApiContext();
    const response = await api.post('/api/v1/questionnaire/', {
      data: {
        interests: [
          { tag: 'books', details: 'fantasy' },
          { tag: 'movies', details: 'science fiction' },
          { tag: 'games', details: 'rpg' },
        ],
        avoid_gifts: [
          { tag: 'flowers', details: 'not preferred' },
        ],
      },
    });
    expect([200, 201]).toContain(response.status());
    await api.dispose();
  });

  test('04. Read questionnaire after save / Чтение анкеты после сохранения', async () => {
    const api = await createApiContext();
    const response = await api.get('/api/v1/questionnaire/');
    expect(response.ok()).toBeTruthy();
    await api.dispose();
  });

  test('05. Available tags response under volume scenario / Ответ доступных тегов в объёмном сценарии', async () => {
    const api = await createApiContext();
    const response = await api.get('/api/v1/questionnaire/tags/available?is_interest=true');
    expect(response.ok()).toBeTruthy();
    await api.dispose();
  });

  test('06. Large wish creation payload / Большой payload создания желания', async () => {
    const api = await createApiContext();
    await createWish(api, 'A');
    await api.dispose();
  });

  test('07. Read created wish / Чтение созданного желания', async () => {
    const api = await createApiContext();
    const wish = await createWish(api, 'B');
    const response = await api.get(`/api/v1/wishes/${wish.id}`);
    expect(response.ok()).toBeTruthy();
    await api.dispose();
  });

  test('08. Update created wish payload / Обновление payload созданного желания', async () => {
    const api = await createApiContext();
    const wish = await createWish(api, 'C');
    const response = await api.put(`/api/v1/wishes/${wish.id}`, {
      data: {
        name: `Updated ${wish.name}`.slice(0, 100),
        url_gift: 'https://example.com/updated-wish',
        price: 123456.78,
        currency: 'USD',
        description: 'Updated wish description',
        is_booked: false,
        status_is_finished: false,
      },
    });
    expect([200, 201]).toContain(response.status());
    await api.dispose();
  });

  test('09. Large wishlist creation payload / Большой payload создания вишлиста', async () => {
    const api = await createApiContext();
    await createWishlist(api, 'A');
    await api.dispose();
  });

  test('10. Read created wishlist / Чтение созданного вишлиста', async () => {
    const api = await createApiContext();
    const wishlist = await createWishlist(api, 'B');
    const response = await api.get(`/api/v1/wishlists/${wishlist.id}`);
    expect(response.ok()).toBeTruthy();
    await api.dispose();
  });

  test('11. Update created wishlist payload / Обновление payload созданного вишлиста', async () => {
    const api = await createApiContext();
    const wishlist = await createWishlist(api, 'C');
    const response = await api.put(`/api/v1/wishlists/${wishlist.id}`, {
      data: {
        name: `Updated ${wishlist.name}`.slice(0, 50),
        description: 'Updated wishlist description',
        photo: null,
        typeprivacy: 'public',
      },
    });
    expect([200, 201]).toContain(response.status());
    await api.dispose();
  });

  test('12. Add wish to wishlist / Добавление желания в вишлист', async () => {
    const api = await createApiContext();
    const wish = await createWish(api, 'D');
    const wishlist = await createWishlist(api, 'D');
    await connectWishToWishlist(api, wishlist.id, wish.id);
    await api.dispose();
  });

  test('13. Read wishes from wishlist / Чтение желаний из вишлиста', async () => {
    const api = await createApiContext();
    const wish = await createWish(api, 'E');
    const wishlist = await createWishlist(api, 'E');
    await connectWishToWishlist(api, wishlist.id, wish.id);
    const response = await api.get(`/api/v1/wishlists/${wishlist.id}/wishes?limit=50`);
    expect(response.ok()).toBeTruthy();
    await api.dispose();
  });

  test('14. Update wish-wishlist connection / Обновление связи wish-wishlist', async () => {
    const api = await createApiContext();
    const wish = await createWish(api, 'F');
    const wishlist = await createWishlist(api, 'F');
    const connection = await connectWishToWishlist(api, wishlist.id, wish.id);
    const response = await api.put(`/api/v1/wishlists/connections/${connection.id}`, {
      data: {
        is_pinned: true,
        order_position: 2,
      },
    });
    expect([200, 201]).toContain(response.status());
    await api.dispose();
  });

  test('15. Delete wish from wishlist connection / Удаление желания из вишлиста', async () => {
    const api = await createApiContext();
    const wish = await createWish(api, 'G');
    const wishlist = await createWishlist(api, 'G');
    await connectWishToWishlist(api, wishlist.id, wish.id);
    const response = await api.delete(`/api/v1/wishlists/${wishlist.id}/wishes/${wish.id}`);
    expect([200, 204]).toContain(response.status());
    await api.dispose();
  });

  test('16. Delete created wish / Удаление созданного желания', async () => {
    const api = await createApiContext();
    const wish = await createWish(api, 'H');
    const response = await api.delete(`/api/v1/wishes/${wish.id}`);
    expect([200, 204]).toContain(response.status());
    await api.dispose();
  });

  test('17. Delete created wishlist / Удаление созданного вишлиста', async () => {
    const api = await createApiContext();
    const wishlist = await createWishlist(api, 'H');
    const response = await api.delete(`/api/v1/wishlists/${wishlist.id}`);
    expect([200, 204]).toContain(response.status());
    await api.dispose();
  });

  test('18. Patch notification settings / Обновление настроек уведомлений', async () => {
    const api = await createApiContext();
    const response = await api.patch('/api/v1/settings/notifications', {
      data: {
        new_followers: true,
        access_requests: true,
        birt_after: true,
        birt_before: true,
      },
    });
    expect([200, 201]).toContain(response.status());
    await api.dispose();
  });

  test('19. Read notification settings after patch / Чтение настроек уведомлений после обновления', async () => {
    const api = await createApiContext();
    const response = await api.get('/api/v1/settings/notifications');
    expect(response.ok()).toBeTruthy();
    await api.dispose();
  });

  test('20. Browser app shell opens and accepts visible input interaction / Оболочка приложения открывается и принимает ввод', async ({ page }) => {
    test.skip(!env.uiUrl, 'PW_UI_URL or PW_BASE_URL is required.');
    await page.goto(env.uiUrl, { waitUntil: 'domcontentloaded' });
    await expect(page.locator('body')).toBeVisible();

    await fillByPossibleSelectors(page, [
      'input[type="text"]',
      'input[placeholder*="Search"]',
      'input[placeholder*="Поиск"]',
      'input[placeholder*="search"]',
    ], 'playwright');

    await clickByPossibleSelectors(page, [
      'button:has-text("Wishlists")',
      'button:has-text("Вишлисты")',
      'a:has-text("Wishlists")',
      'a:has-text("Вишлисты")',
    ]);

    await expect(page.locator('body')).toBeVisible();
  });
});
