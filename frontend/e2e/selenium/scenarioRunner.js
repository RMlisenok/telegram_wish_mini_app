import { afterAll, beforeAll, describe, test } from '@jest/globals';
import { spawn } from 'node:child_process';
import { createServer } from 'node:net';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const env = process.env;
const require = createRequire(import.meta.url);
const selenium = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const chromedriver = require('chromedriver');
const { Builder, By, until, Browser } = selenium;
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(process.cwd(), '..');
const fixtureRoot = path.resolve(__dirname, '..', 'fixtures');
const fixtureAvatarPath = path.join(fixtureRoot, 'avatar.png');
const chromeDriverLogPath = path.resolve(__dirname, '..', 'chromedriver.log');

let viteProcess;
let appOrigin;
let serverOutput = '';
let backendStarted = false;
let backendOrigin = env.E2E_API_BASE_URL || 'http://127.0.0.1:8000';

const e2eEnv = {
  ...env,
  E2E_TELEGRAM_FIRST_NAME: env.E2E_TELEGRAM_FIRST_NAME || 'Test',
  E2E_UPLOAD_IMAGE_PATH: env.E2E_UPLOAD_IMAGE_PATH || fixtureAvatarPath,
};

function scenarioTitle(scenario) {
  return `${scenario.number}. ${scenario.title} [${scenario.requirements.join(', ')}]`;
}

async function getFreePort() {
  const server = createServer();
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const { port } = server.address();
  await new Promise((resolve) => server.close(resolve));
  return port;
}

async function waitForApp(url) {
  const deadline = Date.now() + 30000;
  let lastError;

  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) return;
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }

  throw lastError || new Error(`Timed out waiting for ${url}\n${serverOutput}`);
}

async function runCommand(command, args, options = {}) {
  const child = spawn(command, args, {
    cwd: options.cwd || repoRoot,
    stdio: ['ignore', 'pipe', 'pipe'],
    env: { ...process.env, ...(options.env || {}) },
  });

  let output = '';
  child.stdout.on('data', (chunk) => {
    output += chunk.toString();
    if (env.E2E_DEBUG_SERVER === '1') process.stdout.write(chunk);
  });
  child.stderr.on('data', (chunk) => {
    output += chunk.toString();
    if (env.E2E_DEBUG_SERVER === '1') process.stderr.write(chunk);
  });

  const code = await new Promise((resolve) => child.once('exit', resolve));
  if (code !== 0) {
    if (command === 'docker' && output.includes('docker daemon is not running')) {
      throw new Error(
        `Docker daemon is not running, so the real backend cannot be started for E2E tests.\n` +
        `Start Docker Desktop and rerun npm run test:e2e, or start the backend yourself and set E2E_API_BASE_URL.\n\n` +
        output
      );
    }
    throw new Error(`${command} ${args.join(' ')} failed with code ${code}\n${output}`);
  }
  return output;
}

async function startBackendServer() {
  if (!backendStarted && env.E2E_SKIP_BACKEND_START !== '1' && !env.E2E_API_BASE_URL) {
    await runCommand('docker', [
      'compose',
      '-f',
      path.join(repoRoot, 'docker-compose.e2e.yaml'),
      'up',
      '-d',
      '--build',
      'database',
      'backend',
    ]);
    backendStarted = true;
  }

  await waitForApp(`${backendOrigin}/`);
}

async function resetBackendData() {
  const response = await fetch(`${backendOrigin}/v1/e2e/reset`, {
    method: 'POST',
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`E2E backend reset failed: ${response.status}\n${body}`);
  }
}

async function startAppServer() {
  await startBackendServer();

  if (env.E2E_BASE_URL) {
    appOrigin = env.E2E_BASE_URL;
    return;
  }

  const port = await getFreePort();
  appOrigin = `http://127.0.0.1:${port}`;
  serverOutput = '';
  const viteBin = path.join(process.cwd(), 'node_modules', 'vite', 'bin', 'vite.js');
  viteProcess = spawn(
    process.execPath,
    [viteBin, '--host', '127.0.0.1', '--port', String(port), '--strictPort'],
    {
      cwd: process.cwd(),
      stdio: ['ignore', 'pipe', 'pipe'],
      env: { ...process.env, E2E_API_BASE_URL: backendOrigin },
    }
  );

  viteProcess.stdout.on('data', (chunk) => {
    serverOutput += chunk.toString();
    if (env.E2E_DEBUG_SERVER === '1') process.stdout.write(chunk);
  });
  viteProcess.stderr.on('data', (chunk) => {
    serverOutput += chunk.toString();
    if (env.E2E_DEBUG_SERVER === '1') process.stderr.write(chunk);
  });

  await waitForApp(`${appOrigin}/?e2e=1`);
  e2eEnv.E2E_PUBLIC_PROFILE_URL = env.E2E_PUBLIC_PROFILE_URL || `${appOrigin}/?e2e=1&e2eScreen=publicProfile`;
}

async function stopAppServer() {
  if (!viteProcess) return;
  viteProcess.kill('SIGTERM');
  await new Promise((resolve) => viteProcess.once('exit', resolve));
  viteProcess = undefined;
  appOrigin = undefined;
}

function scenarioBaseUrl(scenario) {
  const e2eParams = `?e2e=1${scenario.number === 5 ? '&e2eNoBirth=1' : ''}`;
  if (env.E2E_BASE_URL) {
    return `${env.E2E_BASE_URL}${e2eParams}${scenario.requires?.includes('telegram') ? '' : '&e2eScreen=main'}`;
  }

  return `${appOrigin}/${e2eParams}${scenario.requires?.includes('telegram') ? '' : '&e2eScreen=main'}`;
}

function buildDriver() {
  const options = new chrome.Options()
    .addArguments('--disable-gpu')
    .addArguments('--disable-extensions')
    .addArguments('--no-sandbox')
    .addArguments('--window-size=1280,900');

  if (!['0', 'false', 'no'].includes(String(env.E2E_HEADLESS || '1').toLowerCase())) {
    options.addArguments('--headless=chrome');
  }

  const service = new chrome.ServiceBuilder(chromedriver.path)
    .loggingTo(chromeDriverLogPath);

  return new Builder()
    .forBrowser(Browser.CHROME)
    .setChromeOptions(options)
    .setChromeService(service)
    .build();
}

export function defineScenarioSuite(moduleName, moduleScenarios) {
  describe(moduleName, () => {
    beforeAll(async () => {
      await startAppServer();
    });

    afterAll(async () => {
      await stopAppServer();
    });

    for (const scenario of moduleScenarios) {
      test(scenarioTitle(scenario), async () => {
        await resetBackendData();
        const driver = await buildDriver();

        try {
          await scenario.run({
            driver,
            By,
            until,
            baseUrl: scenarioBaseUrl(scenario),
            env: e2eEnv,
          });
        } finally {
          const pauseMs = Number(env.E2E_PAUSE_MS || 0);
          if (pauseMs > 0) {
            await driver.sleep(pauseMs);
          }
          await driver.quit().catch(() => {});
        }
      });
    }
  });
}
