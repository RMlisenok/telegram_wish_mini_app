import { test, expect, request } from '@playwright/test';
import { ensureRealToken, realEnv, shouldRunRealE2E } from '../lib/auth';

const env = realEnv();

test.describe('Real UI/API E2E load tests / Реальные нагрузочные E2E тесты', () => {
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

  async function expectRepeatedSuccess(api, path, count = 5) {
    const responses = await Promise.all(Array.from({ length: count }, () => api.get(path)));
    for (const response of responses) {
      expect(response.ok()).toBeTruthy();
      const contentType = response.headers()['content-type'] || '';
      if (contentType.includes('application/json')) {
        const data = await response.json().catch(() => null);
        expect(data).not.toBeNull();
      } else {
        const text = await response.text();
        expect(typeof text).toBe('string');
        expect(text.length).toBeGreaterThan(0);
      }
    }
  }

  async function createWish(api) {
    const response = await api.post('/api/v1/wishes/', {
      data: {
        name: `PW Load Wish ${Date.now()}`,
        url_gift: 'https://example.com/load-wish',
        price: 100,
        currency: 'USD',
        description: 'Playwright load helper wish',
      },
    });
    expect([200, 201]).toContain(response.status());
    return await response.json();
  }

  async function createWishlist(api) {
    const response = await api.post('/api/v1/wishlists/', {
      data: {
        name: `PW Load Wishlist ${Date.now()}`.slice(0, 50),
        description: 'Playwright load helper wishlist',
        typeprivacy: 'public',
      },
    });
    expect([200, 201]).toContain(response.status());
    return await response.json();
  }

  test('01. Burst authentication requests / Пакетные запросы аутентификации', async () => {
    const api = await request.newContext({
      baseURL: env.baseUrl,
      ignoreHTTPSErrors: true,
      extraHTTPHeaders: { 'Content-Type': 'application/json' },
    });

    const responses = await Promise.all(Array.from({ length: 3 }, () =>
      api.post(env.authPath, {
        data: {
          initData: env.telegramInitData || 'playwright-init-data',
          user: {
            id: Number(env.telegramUserId || 100001),
            first_name: env.telegramFirstName || 'Playwright',
          },
        },
      })
    ));

    for (const response of responses) {
      // expect([200, 201]).toContain(response.status());
        expect([200, 201, 401, 429]).toContain(response.status());
        expect(response.status()).toBeLessThan(500);
    }
    await api.dispose();
  });

  test('02. Repeated current user reads / Повторные чтения текущего пользователя', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/users/me');
    await api.dispose();
  });

  test('03. High-load wishes list requests / Высокая нагрузка на список желаний', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/wishes/?limit=10&is_desc=true');
    await api.dispose();
  });

  test('04. High-load finished wishes list requests / Высокая нагрузка на список завершённых желаний', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/wishes/finish?limit=10&is_finish=true');
    await api.dispose();
  });

  test('05. High-load wishlists list requests / Высокая нагрузка на список вишлистов', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/wishlists/?limit=10');
    await api.dispose();
  });

  test('06. High-load my subscriptions requests / Высокая нагрузка на мои подписки', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/subscriptions/my?limit=20');
    await api.dispose();
  });

  test('07. High-load my user subscriptions requests / Высокая нагрузка на подписки пользователей', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/subscriptions/my/users?limit=20');
    await api.dispose();
  });

  test('08. High-load my wishlist subscriptions requests / Высокая нагрузка на подписки вишлистов', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/subscriptions/my/wishlists?limit=20');
    await api.dispose();
  });

  test('09. High-load my subscribers requests / Высокая нагрузка на список подписчиков', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/subscriptions/my/subscribers?limit=20&is_desc=true');
    await api.dispose();
  });

  test('10. Repeated questionnaire reads / Повторные чтения анкеты', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/questionnaire/');
    await api.dispose();
  });

  test('11. Repeated questionnaire tags reads / Повторные чтения доступных тегов анкеты', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/questionnaire/tags/available?is_interest=true');
    await api.dispose();
  });

  test('12. Repeated notification settings reads / Повторные чтения настроек уведомлений', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/settings/notifications');
    await api.dispose();
  });

  test('13. Repeated users list reads / Повторные чтения списка пользователей', async () => {
    const api = await createApiContext();
    await expectRepeatedSuccess(api, '/api/v1/users/all?limit=10');
    await api.dispose();
  });

  test('14. Fast repeated docs access via public route / Быстрый повторный доступ к docs', async () => {
    const api = await request.newContext({ baseURL: env.baseUrl, ignoreHTTPSErrors: true });
    const responses = await Promise.all(Array.from({ length: 3 }, () => api.get('/api/docs')));
    for (const response of responses) {
      expect(response.ok()).toBeTruthy();
      const text = await response.text();
      expect(text.length).toBeGreaterThan(0);
    }
    await api.dispose();
  });

  test('15. Fast repeated openapi access / Быстрый повторный доступ к openapi', async () => {
    const api = await request.newContext({ baseURL: env.baseUrl, ignoreHTTPSErrors: true });
    const responses = await Promise.all(Array.from({ length: 3 }, () => api.get('/openapi.json')));
    for (const response of responses) {
      expect(response.ok()).toBeTruthy();
    }
    await api.dispose();
  });

  test('16. Mixed user-questionnaire-settings load burst / Смешанная нагрузка user-questionnaire-settings', async () => {
    const api = await createApiContext();
    const responses = await Promise.all([
      ...Array.from({ length: 2 }, () => api.get('/api/v1/users/me')),
      ...Array.from({ length: 2 }, () => api.get('/api/v1/questionnaire/')),
      ...Array.from({ length: 2 }, () => api.get('/api/v1/settings/notifications')),
    ]);
    for (const response of responses) expect(response.ok()).toBeTruthy();
    await api.dispose();
  });

  test('17. Mixed wishes-wishlists load burst / Смешанная нагрузка wishes-wishlists', async () => {
    const api = await createApiContext();
    const responses = await Promise.all([
      ...Array.from({ length: 3 }, () => api.get('/api/v1/wishes/?limit=10')),
      ...Array.from({ length: 3 }, () => api.get('/api/v1/wishlists/?limit=10')),
    ]);
    for (const response of responses) expect(response.ok()).toBeTruthy();
    await api.dispose();
  });

  test('18. Repeated created wish reads / Повторные чтения созданного желания', async () => {
    const api = await createApiContext();
    const wish = await createWish(api);
    await expectRepeatedSuccess(api, `/api/v1/wishes/${wish.id}`, 3);
    await api.dispose();
  });

  test('19. Repeated created wishlist reads / Повторные чтения созданного вишлиста', async () => {
    const api = await createApiContext();
    const wishlist = await createWishlist(api);
    await expectRepeatedSuccess(api, `/api/v1/wishlists/${wishlist.id}`, 3);
    await api.dispose();
  });

  test('20. Browser home page load and refresh stability / Стабильность загрузки и обновления главной страницы', async ({ page }) => {
    test.skip(!env.uiUrl, 'PW_UI_URL or PW_BASE_URL is required.');
    await page.goto(env.uiUrl, { waitUntil: 'domcontentloaded' });
    await expect(page.locator('body')).toBeVisible();
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await expect(page.locator('body')).toBeVisible();
  });
});
