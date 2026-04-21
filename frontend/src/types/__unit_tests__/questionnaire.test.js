import { jest } from '@jest/globals';
import {
  loadAvailableTags,
  loadQuestionnaire,
  loadUserQuestionnaire,
  saveQuestionnaire
} from '../questionnaire.ts';

const jsonResponse = (data, ok = true, status = 200) => ({
  ok,
  status,
  json: async () => data,
  text: async () => JSON.stringify(data)
});

describe('types/questionnaire', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('loadQuestionnaire normalizes missing details to empty strings', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse({
        interests: [{ tag: 'книги' }],
        avoid_gifts: [{ tag: 'цветы', details: null }]
      })
    );

    const result = await loadQuestionnaire('token-123');

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/questionnaire/',
      expect.objectContaining({ method: 'GET' })
    );
    expect(result).toEqual({
      interests: [{ tag: 'книги', details: '' }],
      avoid_gifts: [{ tag: 'цветы', details: '' }]
    });
  });

  test('loadQuestionnaire returns empty structure on 404', async () => {
    global.fetch.mockResolvedValue(jsonResponse({}, false, 404));

    await expect(loadQuestionnaire('token-123')).resolves.toEqual({
      interests: [],
      avoid_gifts: []
    });
  });

  test('saveQuestionnaire posts payload and throws on backend error', async () => {
    global.fetch.mockResolvedValueOnce(jsonResponse({ success: true }));

    await saveQuestionnaire('token-123', {
      interests: [{ tag: 'кино', details: 'драма' }],
      avoid_gifts: [{ tag: 'алкоголь', details: '' }]
    });

    const call = global.fetch.mock.calls[0];
    expect(call[0]).toBe('/api/v1/questionnaire/');
    expect(call[1]).toMatchObject({ method: 'POST' });
    expect(JSON.parse(call[1].body)).toEqual({
      interests: [{ tag: 'кино', details: 'драма' }],
      avoid_gifts: [{ tag: 'алкоголь', details: '' }]
    });

    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      text: async () => 'server error'
    });

    await expect(
      saveQuestionnaire('token-123', { interests: [], avoid_gifts: [] })
    ).rejects.toThrow('Ошибка сохранения анкеты: 500 - server error');
  });

  test('loadAvailableTags maps tag values from backend', async () => {
    global.fetch.mockResolvedValue(
      jsonResponse({ tags: [{ tag_value: 'кино' }, { tag_value: 'театр' }] })
    );

    await expect(loadAvailableTags('token-123', true)).resolves.toEqual(['кино', 'театр']);
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/v1/questionnaire/tags/available?is_interest=true',
      expect.objectContaining({ method: 'GET' })
    );
  });

  test('loadUserQuestionnaire returns empty structure on 404', async () => {
    global.fetch.mockResolvedValue(jsonResponse({}, false, 404));

    await expect(loadUserQuestionnaire('token-123', 55)).resolves.toEqual({
      interests: [],
      avoid_gifts: []
    });
  });
});
