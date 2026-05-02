import { test, expect, request, type APIRequestContext, type APIResponse } from '@playwright/test';
import { ensureRealToken, realEnv, shouldRunRealE2E } from '../lib/auth';

const env = realEnv();

test.describe('Real UI/API E2E stability tests / Реальные E2E тесты стабильности', () => {
  test.skip(!shouldRunRealE2E(), 'PW_BASE_URL + auth data are required.');
  test.describe.configure({ mode: 'serial' });

  async function createApiContext(): Promise<APIRequestContext> {
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

  async function expectOk(response: APIResponse) {
    expect(response.status()).toBeLessThan(500);
    expect(response.ok()).toBeTruthy();
  }

  async function expectStableGet(api: APIRequestContext, path: string, count = 5) {
    for (let index = 0; index < count; index += 1) {
      const response = await api.get(path);
      await expectOk(response);
      const contentType = response.headers()['content-type'] || '';
      if (contentType.includes('application/json')) {
        const data = await response.json().catch(() => null);
        expect(data).not.toBeNull();
      }
    }
  }

  async function createWish(api: APIRequestContext, suffix = '') {
    const response = await api.post('/api/v1/wishes/', {
      data: {
        name: `PW Stability Wish ${suffix} ${Date.now()}`.slice(0, 100),
        url_gift: 'https://example.com/stability-wish',
        price: 100,
        currency: 'USD',
        description: 'Playwright stability wish',
      },
    });
    expect([200, 201]).toContain(response.status());
    return await response.json();
  }

  async function createWishlist(api: APIRequestContext, suffix = '') {
    const response = await api.post('/api/v1/wishlists/', {
      data: {
        name: `PW Stability Wishlist ${suffix} ${Date.now()}`.slice(0, 50),
        description: 'Playwright stability wishlist',
        typeprivacy: 'public',
      },
    });
    expect([200, 201]).toContain(response.status());
    return await response.json();
  }

  async function connectWishToWishlist(api: APIRequestContext, wishlistId: number | string, wishId: number | string) {
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

  test('01. Stable repeated current user reads / Стабильное повторное чтение текущего пользователя', async () => {
    const api = await createApiContext();
    await expectStableGet(api, '/api/v1/users/me', 5);
    await api.dispose();
  });

  test('02. Stable questionnaire and tags reads / Стабильное чтение анкеты и тегов', async () => {
    const api = await createApiContext();
    await expectStableGet(api, '/api/v1/questionnaire/', 3);
    await expectStableGet(api, '/api/v1/questionnaire/tags/available?is_interest=true', 3);
    await expectStableGet(api, '/api/v1/questionnaire/tags/available?is_interest=false', 3);
    await api.dispose();
  });

  test('03. Stable notification settings read-update-read cycle / Стабильный цикл чтения и обновления уведомлений', async () => {
    const api = await createApiContext();
    for (let index = 0; index < 3; index += 1) {
      const patchResponse = await api.patch('/api/v1/settings/notifications', {
        data: {
          new_followers: index % 2 === 0,
          access_requests: true,
          birt_after: true,
          birt_before: index % 2 !== 0,
        },
      });
      expect([200, 201]).toContain(patchResponse.status());
      await expectStableGet(api, '/api/v1/settings/notifications', 1);
    }
    await api.dispose();
  });

  test('04. Stable wish lifecycle repeated several times / Стабильный повторный жизненный цикл желания', async () => {
    const api = await createApiContext();
    for (let index = 0; index < 3; index += 1) {
      const wish = await createWish(api, String(index));
      await expectStableGet(api, `/api/v1/wishes/${wish.id}`, 1);

      const updateResponse = await api.put(`/api/v1/wishes/${wish.id}`, {
        data: {
          name: `Updated ${wish.name}`.slice(0, 100),
          url_gift: 'https://example.com/stability-wish-updated',
          price: 120,
          currency: 'USD',
          description: 'Updated during stability test',
          is_booked: false,
          status_is_finished: false,
        },
      });
      expect([200, 201]).toContain(updateResponse.status());

      const deleteResponse = await api.delete(`/api/v1/wishes/${wish.id}`);
      expect([200, 204]).toContain(deleteResponse.status());
    }
    await api.dispose();
  });

  test('05. Stable wishlist lifecycle repeated several times / Стабильный повторный жизненный цикл вишлиста', async () => {
    const api = await createApiContext();
    for (let index = 0; index < 3; index += 1) {
      const wishlist = await createWishlist(api, String(index));
      await expectStableGet(api, `/api/v1/wishlists/${wishlist.id}`, 1);

      const updateResponse = await api.put(`/api/v1/wishlists/${wishlist.id}`, {
        data: {
          name: `Updated ${wishlist.name}`.slice(0, 50),
          description: 'Updated during stability test',
          photo: null,
          typeprivacy: 'public',
        },
      });
      expect([200, 201]).toContain(updateResponse.status());

      const deleteResponse = await api.delete(`/api/v1/wishlists/${wishlist.id}`);
      expect([200, 204]).toContain(deleteResponse.status());
    }
    await api.dispose();
  });

  test('06. Stable wish-wishlist connection workflow / Стабильный сценарий связи желания и вишлиста', async () => {
    const api = await createApiContext();
    const wish = await createWish(api, 'connection');
    const wishlist = await createWishlist(api, 'connection');
    const connection = await connectWishToWishlist(api, wishlist.id, wish.id);

    await expectStableGet(api, `/api/v1/wishlists/${wishlist.id}/wishes?limit=50`, 3);

    const updateConnectionResponse = await api.put(`/api/v1/wishlists/connections/${connection.id}`, {
      data: {
        is_pinned: true,
        order_position: 2,
      },
    });
    expect([200, 201]).toContain(updateConnectionResponse.status());

    const deleteConnectionResponse = await api.delete(`/api/v1/wishlists/${wishlist.id}/wishes/${wish.id}`);
    expect([200, 204]).toContain(deleteConnectionResponse.status());

    await api.delete(`/api/v1/wishes/${wish.id}`);
    await api.delete(`/api/v1/wishlists/${wishlist.id}`);
    await api.dispose();
  });

  test('07. Stable subscriptions and subscribers reads / Стабильное чтение подписок и подписчиков', async () => {
    const api = await createApiContext();
    await expectStableGet(api, '/api/v1/subscriptions/my?limit=20', 3);
    await expectStableGet(api, '/api/v1/subscriptions/my/users?limit=20', 3);
    await expectStableGet(api, '/api/v1/subscriptions/my/wishlists?limit=20', 3);
    await expectStableGet(api, '/api/v1/subscriptions/my/subscribers?limit=20&is_desc=true', 3);
    await api.dispose();
  });

  test('08. Stable public documentation endpoints / Стабильность публичных endpoint документации', async () => {
    const api = await request.newContext({ baseURL: env.baseUrl, ignoreHTTPSErrors: true });
    await expectStableGet(api, '/api/docs', 3);
    await expectStableGet(api, '/openapi.json', 3);
    await api.dispose();
  });

  test('09. Stable UI reloads without losing the application shell / Стабильная перезагрузка UI без потери оболочки', async ({ page }) => {
    test.skip(!env.uiUrl, 'PW_UI_URL or PW_BASE_URL is required.');
    const pageErrors: Error[] = [];
    page.on('pageerror', error => pageErrors.push(error));

    await page.goto(env.uiUrl, { waitUntil: 'domcontentloaded' });
    await expect(page.locator('body')).toBeVisible();

    for (let index = 0; index < 3; index += 1) {
      await page.reload({ waitUntil: 'domcontentloaded' });
      await expect(page.locator('body')).toBeVisible();
    }

    expect(pageErrors.length).toBe(0);
  });

  test('10. Stable mixed user flow under sequential long session / Стабильный смешанный поток в длинной сессии', async () => {
    const api = await createApiContext();
    for (let index = 0; index < 3; index += 1) {
      await expectStableGet(api, '/api/v1/users/me', 1);
      await expectStableGet(api, '/api/v1/wishes/?limit=10&is_desc=true', 1);
      await expectStableGet(api, '/api/v1/wishlists/?limit=10', 1);
      await expectStableGet(api, '/api/v1/questionnaire/', 1);
      await expectStableGet(api, '/api/v1/settings/notifications', 1);
    }
    await api.dispose();
  });
});
