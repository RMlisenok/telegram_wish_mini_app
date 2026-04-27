import { APIRequestContext, expect, request } from '@playwright/test';

export type AuthConfig = {
  baseUrl: string;
  authPath: string;
  token?: string;
  telegramUserId?: string;
  telegramFirstName?: string;
  telegramInitData?: string;
};

export async function getApiContext(baseUrl: string): Promise<APIRequestContext> {
  return await request.newContext({
    baseURL: baseUrl,
    ignoreHTTPSErrors: true,
    extraHTTPHeaders: {
      'Content-Type': 'application/json',
    },
  });
}

export async function ensureRealToken(config: AuthConfig): Promise<string> {
  if (config.token) return config.token;

  if (!config.telegramUserId) {
    throw new Error(
      'Provide PW_TEST_TOKEN or PW_TELEGRAM_USER_ID for real Playwright E2E tests.'
    );
  }

  const api = await getApiContext(config.baseUrl);
  const response = await api.post(config.authPath, {
    data: {
      initData: config.telegramInitData || 'playwright-init-data',
      user: {
        id: Number(config.telegramUserId),
        first_name: config.telegramFirstName || 'Playwright',
      },
    },
  });

  expect([200, 201]).toContain(response.status());

  const data = await response.json().catch(() => ({}));
  const token =
    data?.token ||
    data?.access_token ||
    data?.jwt ||
    data?.data?.token ||
    data?.data?.access_token;

  if (!token) {
    throw new Error('Authentication response did not include a token.');
  }

  await api.dispose();
  return token;
}

export function realEnv() {
  const baseUrl = process.env.PW_BASE_URL || '';
  const uiUrl = process.env.PW_UI_URL || baseUrl;
  const authPath = process.env.PW_AUTH_PATH || '/auth/telegram';

  return {
    baseUrl,
    uiUrl,
    authPath,
    token: process.env.PW_TEST_TOKEN,
    telegramUserId: process.env.PW_TELEGRAM_USER_ID,
    telegramFirstName: process.env.PW_TELEGRAM_FIRST_NAME,
    telegramInitData: process.env.PW_TELEGRAM_INIT_DATA,
  };
}

export function shouldRunRealE2E() {
  const env = realEnv();
  return Boolean(env.baseUrl) && (Boolean(env.token) || Boolean(env.telegramUserId));
}
