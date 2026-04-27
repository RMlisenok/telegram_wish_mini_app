function json(data, init = {}) {
  return new Response(JSON.stringify(data), {
    status: init.status || 200,
    headers: { 'Content-Type': 'application/json' },
  });
}

const E2E_TELEGRAM_BOT_TOKEN = '1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi';
const nativeFetch = window.fetch.bind(window);

function currentTelegramUser() {
  const params = new URLSearchParams(window.location.search);
  const noBirth = params.get('e2eNoBirth') === '1';
  const telegramId = noBirth ? 900005 : 900001;

  return {
    id: telegramId,
    first_name: noBirth ? 'Birth' : 'Test',
    last_name: noBirth ? 'Required' : 'User',
    username: noBirth ? 'e2e_birth_required' : 'e2e_user',
  };
}

function toHex(buffer) {
  return [...new Uint8Array(buffer)]
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
}

async function hmac(key, message) {
  const cryptoKey = await crypto.subtle.importKey(
    'raw',
    typeof key === 'string' ? new TextEncoder().encode(key) : key,
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  return crypto.subtle.sign('HMAC', cryptoKey, new TextEncoder().encode(message));
}

async function createTelegramInitData(user) {
  const data = {
    auth_date: '1770000000',
    query_id: 'e2e-query-id',
    user: JSON.stringify(user),
  };
  const dataCheckString = Object.keys(data)
    .sort()
    .map((key) => `${key}=${data[key]}`)
    .join('\n');
  const secretKey = await hmac('WebAppData', E2E_TELEGRAM_BOT_TOKEN);
  const hash = toHex(await hmac(secretKey, dataCheckString));
  return new URLSearchParams({ ...data, hash }).toString();
}

window.__E2E__ = true;
const telegramUser = currentTelegramUser();
const telegramInitData = await createTelegramInitData(telegramUser);

window.Telegram = {
  WebApp: {
    initData: telegramInitData,
    initDataUnsafe: {
      user: telegramUser,
    },
    themeParams: {
      bg_color: '#ffffff',
      text_color: '#111827',
      hint_color: '#6b7280',
      link_color: '#007aff',
      secondary_bg_color: '#f3f4f6',
    },
    ready() {},
    expand() {},
    enableClosingConfirmation() {},
    setHeaderColor() {},
    setBackgroundColor() {},
    openTelegramLink() {},
    openLink() {},
    shareToStory() {},
  },
};

window.alert = (message) => {
  const node = document.createElement('div');
  node.setAttribute('role', 'alert');
  node.textContent = message;
  document.body.appendChild(node);
};

if (!window.navigator.clipboard) {
  Object.defineProperty(window.navigator, 'clipboard', {
    configurable: true,
    value: {},
  });
}
window.navigator.clipboard.writeText = async () => {};
window.navigator.share = async () => {};

window.fetch = async (input, options = {}) => {
  const url = typeof input === 'string' ? input : input.url;
  const parsed = new URL(url, window.location.origin);
  const pathname = parsed.pathname;

  if (pathname.startsWith('/api/v1/s3/file/')) {
    return json({
      message: 'success',
      filename: 'e2e.png',
      file_url: 'https://example.test/e2e.png',
      content_type: 'image/png',
      size: 10,
    });
  }

  return nativeFetch(input, options);
};
