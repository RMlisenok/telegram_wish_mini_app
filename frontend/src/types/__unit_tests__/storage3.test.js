import { jest } from '@jest/globals';
import { deleteFile, replaceFile, uploadFile } from '../storage3.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data
});

describe('types/storage3', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('uploadFile sends multipart request with authorization header', async () => {
    const file = new File(['hello'], 'avatar.png', { type: 'image/png' });
    global.fetch.mockResolvedValue(
      jsonResponse({
        message: 'uploaded',
        filename: 'avatar.png',
        file_url: 'https://cdn/avatar.png',
        content_type: 'image/png',
        size: 5
      })
    );

    const result = await uploadFile(file, 'token-123');

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/s3/file/',
      expect.objectContaining({ method: 'POST', headers: { Authorization: 'Bearer token-123' } })
    );
    expect(result.file_url).toBe('https://cdn/avatar.png');
  });

  test('replaceFile encodes old file url in query string', async () => {
    const file = new File(['new'], 'new.png', { type: 'image/png' });
    global.fetch.mockResolvedValue(
      jsonResponse({
        message: 'replaced',
        filename: 'new.png',
        file_url: 'https://cdn/new.png',
        content_type: 'image/png',
        size: 3
      })
    );

    await replaceFile('https://cdn/old file.png', file, 'token-123');

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/s3/file/replace?file_url=https%3A%2F%2Fcdn%2Fold%20file.png',
      expect.objectContaining({ method: 'PUT' })
    );
  });

  test('deleteFile throws backend detail on failure', async () => {
    global.fetch.mockResolvedValue({
      ok: false,
      json: async () => ({ detail: 'cannot delete' })
    });

    await expect(deleteFile('https://cdn/file.png', 'token-123')).rejects.toThrow('cannot delete');
  });
});
