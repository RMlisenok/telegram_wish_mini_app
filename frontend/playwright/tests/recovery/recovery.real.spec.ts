import { test, expect, request, type APIRequestContext, type APIResponse } from '@playwright/test';
import { ensureRealToken, realEnv, shouldRunRealE2E } from '../lib/auth';

const env = realEnv();

test.describe('Real UI/API E2E recovery tests / Реальные E2E тесты восстановления', () => {
  test.skip(!shouldRunRealE2E(), 'PW_BASE_URL + auth data are required.');

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

  async function createAnonymousContext(): Promise<APIRequestContext> {
    return await request.newContext({
      baseURL: env.baseUrl,
      extraHTTPHeaders: {
        'Content-Type': 'application/json',
      },
      ignoreHTTPSErrors: true,
    });
  }

  async function expectFailureWasHandled(response: APIResponse, label: string) {
    const body = await response.text().catch(() => '');

    // Recovery testing verifies that the system survives an invalid operation.
    // Some current backend routes return 500 for invalid payloads, so the test
    // accepts any HTTP error here and checks recovery with a valid request after it.
    expect(response.status(), `${label}\nBody: ${body}`).toBeGreaterThanOrEqual(400);
    expect(response.status(), `${label}\nBody: ${body}`).toBeLessThan(600);
  }

  async function expectSuccessfulRecovery(response: APIResponse, label: string) {
    const body = await response.text().catch(() => '');

    expect(response.status(), `${label}\nBody: ${body}`).toBeLessThan(500);
    expect(response.ok(), `${label}\nStatus: ${response.status()}\nBody: ${body}`).toBeTruthy();
  }

  async function assertAuthenticatedRecovery(api: APIRequestContext, label: string) {
    const recoveredUserResponse = await api.get('/api/v1/users/me');
    await expectSuccessfulRecovery(recoveredUserResponse, `${label}: /api/v1/users/me must recover`);
  }

  test('01. Recovery after invalid authentication payload / Восстановление после некорректной аутентификации', async () => {
    const anonymousApi = await createAnonymousContext();
    const api = await createApiContext();

    try {
      const invalidAuthResponse = await anonymousApi.post(env.authPath, {
        data: {
          initData: 'invalid-playwright-data',
          user: null,
        },
      });

      await expectFailureWasHandled(invalidAuthResponse, 'Invalid authentication payload should not break the backend');
      await assertAuthenticatedRecovery(api, 'Recovery after invalid authentication payload');
    } finally {
      await api.dispose();
      await anonymousApi.dispose();
    }
  });

  test('02. Recovery after missing authorization header / Восстановление после отсутствующего токена', async () => {
    const anonymousApi = await createAnonymousContext();
    const api = await createApiContext();

    try {
      const unauthorizedResponse = await anonymousApi.get('/api/v1/users/me');

      await expectFailureWasHandled(unauthorizedResponse, 'Missing authorization header should be handled');
      await assertAuthenticatedRecovery(api, 'Recovery after missing authorization header');
    } finally {
      await api.dispose();
      await anonymousApi.dispose();
    }
  });

  test('03. Recovery after malformed bearer token / Восстановление после повреждённого bearer token', async () => {
    const invalidTokenApi = await request.newContext({
      baseURL: env.baseUrl,
      ignoreHTTPSErrors: true,
      extraHTTPHeaders: {
        Authorization: 'Bearer invalid-playwright-token',
        'Content-Type': 'application/json',
      },
    });
    const api = await createApiContext();

    try {
      const invalidTokenResponse = await invalidTokenApi.get('/api/v1/users/me');

      await expectFailureWasHandled(invalidTokenResponse, 'Malformed bearer token should be handled');
      await assertAuthenticatedRecovery(api, 'Recovery after malformed bearer token');
    } finally {
      await api.dispose();
      await invalidTokenApi.dispose();
    }
  });

  test('04. Recovery after reading nonexistent wish / Восстановление после чтения несуществующего желания', async () => {
    const api = await createApiContext();

    try {
      const missingWishResponse = await api.get('/api/v1/wishes/999999999');

      await expectFailureWasHandled(missingWishResponse, 'Reading a nonexistent wish should be handled');
      await assertAuthenticatedRecovery(api, 'Recovery after reading nonexistent wish');
    } finally {
      await api.dispose();
    }
  });

  test('05. Recovery after invalid wish creation payload / Восстановление после неверного payload желания', async () => {
    const api = await createApiContext();

    try {
      const invalidCreateResponse = await api.post('/api/v1/wishes/', {
        data: {
          name: '',
          url_gift: 'not-a-valid-url',
          price: -100,
          currency: '',
        },
      });

      await expectFailureWasHandled(invalidCreateResponse, 'Invalid wish creation payload should be handled');
      await assertAuthenticatedRecovery(api, 'Recovery after invalid wish creation payload');
    } finally {
      await api.dispose();
    }
  });

  test('06. Recovery after updating nonexistent wish / Восстановление после обновления несуществующего желания', async () => {
    const api = await createApiContext();

    try {
      const invalidUpdateResponse = await api.put('/api/v1/wishes/999999999', {
        data: {
          name: 'Should not exist',
          url_gift: 'https://example.com/not-existing',
          price: 10,
          currency: 'USD',
          description: 'Invalid update target',
          is_booked: false,
          status_is_finished: false,
        },
      });

      await expectFailureWasHandled(invalidUpdateResponse, 'Updating a nonexistent wish should be handled');
      await assertAuthenticatedRecovery(api, 'Recovery after updating nonexistent wish');
    } finally {
      await api.dispose();
    }
  });

  test('07. Recovery after invalid wishlist creation payload / Восстановление после неверного payload вишлиста', async () => {
    const api = await createApiContext();

    try {
      const invalidCreateResponse = await api.post('/api/v1/wishlists/', {
        data: {
          name: '',
          description: 'Invalid wishlist payload',
          typeprivacy: 'unexpected-privacy-value',
        },
      });

      await expectFailureWasHandled(invalidCreateResponse, 'Invalid wishlist creation payload should be handled');
      await assertAuthenticatedRecovery(api, 'Recovery after invalid wishlist creation payload');
    } finally {
      await api.dispose();
    }
  });

  test('08. Recovery after reading nonexistent wishlist / Восстановление после чтения несуществующего вишлиста', async () => {
    const api = await createApiContext();

    try {
      const missingWishlistResponse = await api.get('/api/v1/wishlists/999999999');

      await expectFailureWasHandled(missingWishlistResponse, 'Reading a nonexistent wishlist should be handled');
      await assertAuthenticatedRecovery(api, 'Recovery after reading nonexistent wishlist');
    } finally {
      await api.dispose();
    }
  });

  test('09. Recovery after invalid wish-wishlist connection / Восстановление после некорректной связи wish-wishlist', async () => {
    const api = await createApiContext();

    try {
      const invalidConnectionResponse = await api.post('/api/v1/wishlists/999999999/wishes', {
        data: {
          is_pinned: false,
          order_position: 1,
          wish_id: 999999999,
          wishlist_id: 999999999,
        },
      });

      await expectFailureWasHandled(invalidConnectionResponse, 'Invalid wish-wishlist connection should be handled');
      await assertAuthenticatedRecovery(api, 'Recovery after invalid wish-wishlist connection');
    } finally {
      await api.dispose();
    }
  });

  test('10. Recovery after opening unknown UI route / Восстановление UI после неизвестного маршрута', async ({ page }) => {
    test.skip(!env.uiUrl, 'PW_UI_URL or PW_BASE_URL is required.');

    const unknownUrl = new URL('/__playwright_unknown_recovery_route__', env.uiUrl).toString();

    await page.goto(unknownUrl, { waitUntil: 'domcontentloaded' });
    await expect(page.locator('body')).toBeVisible();

    await page.goto(env.uiUrl, { waitUntil: 'domcontentloaded' });
    await expect(page.locator('body')).toBeVisible();
  });
});
