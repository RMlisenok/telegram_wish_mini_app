import { jest } from '@jest/globals';
import { writable } from 'svelte/store';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/svelte';

const questionnaireStore = writable({ interests: [], avoid_gifts: [] });
const loadAvailableTags = jest.fn();
const loadQuestionnaire = jest.fn();
const saveQuestionnaire = jest.fn();

jest.unstable_mockModule('../../../../types/questionnaire.ts', () => ({
  questionnaireStore,
  loadAvailableTags,
  loadQuestionnaire,
  saveQuestionnaire,
  TagItem: class TagItem {},
  QuestionnaireData: class QuestionnaireData {}
}));

const { default: QuestionnaireScreen } = await import('../QuestionnaireScreen.svelte');

describe('QuestionnaireScreen', () => {
  beforeEach(() => {
    questionnaireStore.set({ interests: [], avoid_gifts: [] });
    loadAvailableTags.mockReset();
    loadQuestionnaire.mockReset();
    saveQuestionnaire.mockReset();
    global.alert = jest.fn();
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
  });

  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  function setupLoadMocks({
    availableInterests = ['кино', '-', 'книги'],
    availableNoGifts = ['сладости', '-', 'цветы'],
    questionnaire = { interests: [], avoid_gifts: [] }
  } = {}) {
    loadAvailableTags.mockImplementation(async (_token, isInterest) =>
      isInterest ? availableInterests : availableNoGifts
    );
    loadQuestionnaire.mockResolvedValue(questionnaire);
    saveQuestionnaire.mockResolvedValue(undefined);
  }

  test('loads tags and questionnaire data on mount', async () => {
    setupLoadMocks({
      availableInterests: ['кино', 'театр'],
      availableNoGifts: ['сладости'],
      questionnaire: {
        interests: [{ tag: 'книги', details: 'Фэнтези' }],
        avoid_gifts: [{ tag: 'цветы', details: 'Только не розы' }]
      }
    });

    render(QuestionnaireScreen, { token: 'token-123' });

    await waitFor(() => {
      expect(loadAvailableTags).toHaveBeenCalledWith('token-123', true);
      expect(loadAvailableTags).toHaveBeenCalledWith('token-123', false);
      expect(loadQuestionnaire).toHaveBeenCalledWith('token-123');
      expect(screen.getByText('кино')).toBeInTheDocument();
      expect(screen.getByText('театр')).toBeInTheDocument();
      expect(screen.getByText('книги')).toBeInTheDocument();
      expect(screen.getByText('цветы')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Фэнтези')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Только не розы')).toBeInTheDocument();
    });
  });

  test('adds selected predefined interest and hides it from available chips', async () => {
    setupLoadMocks();

    render(QuestionnaireScreen, { token: 'token-123' });

    const kinoChip = await screen.findByText('кино');
    await fireEvent.click(kinoChip);

    expect(screen.getByText('кино')).toBeInTheDocument();
    expect(screen.queryAllByText('кино')).toHaveLength(1);
  });

  test('adds custom interest trimmed and clears custom input', async () => {
    setupLoadMocks();

    render(QuestionnaireScreen, { token: 'token-123' });

    const customInterestInput = await screen.findByPlaceholderText('Например, джазовые концерты');
    const addButtons = screen.getAllByText('Добавить свой тег');

    await fireEvent.input(customInterestInput, {
      target: { value: '  джаз  ' }
    });
    await fireEvent.click(addButtons[0]);

    expect(screen.getByText('джаз')).toBeInTheDocument();
    expect(customInterestInput).toHaveValue('');
  });

  test('shows validation error for too long custom interest', async () => {
    setupLoadMocks();

    render(QuestionnaireScreen, { token: 'token-123' });

    const customInterestInput = await screen.findByPlaceholderText('Например, джазовые концерты');
    const addButtons = screen.getAllByText('Добавить свой тег');

    await fireEvent.input(customInterestInput, {
      target: { value: 'x'.repeat(21) }
    });
    await fireEvent.click(addButtons[0]);

    expect(screen.getByText('Максимум 20 символов для кастомного тега.')).toBeInTheDocument();
    expect(screen.queryByText('x'.repeat(21))).not.toBeInTheDocument();
  });

  test('shows minimum validation errors and does not save invalid questionnaire', async () => {
    setupLoadMocks();

    render(QuestionnaireScreen, { token: 'token-123' });

    const saveButton = await screen.findByText('Сохранить анкету');
    await fireEvent.click(saveButton);

    expect(screen.getByText('Для сохранения анкеты необходимо выбрать минимум 3 интереса.')).toBeInTheDocument();
    expect(screen.getByText('Для сохранения анкеты необходимо выбрать минимум 1 тег')).toBeInTheDocument();
    expect(saveQuestionnaire).not.toHaveBeenCalled();
    expect(global.alert).not.toHaveBeenCalled();
  });

  test('saves questionnaire with special dash tag and truncates details to 100 chars', async () => {
    setupLoadMocks();

    render(QuestionnaireScreen, { token: 'token-123' });

    await fireEvent.click(await screen.findByText('-'));
    await fireEvent.click(screen.getByText('сладости'));

    const detailInputs = screen.getAllByPlaceholderText('Уточните...');
    await fireEvent.input(detailInputs[0], { target: { value: 'a'.repeat(120) } });
    await fireEvent.input(detailInputs[1], { target: { value: 'b'.repeat(150) } });

    await fireEvent.click(screen.getByText('Сохранить анкету'));

    await waitFor(() => {
      expect(saveQuestionnaire).toHaveBeenCalledWith('token-123', {
        interests: [{ tag: '-', details: 'a'.repeat(100) }],
        avoid_gifts: [{ tag: 'сладости', details: 'b'.repeat(100) }]
      });
      expect(global.alert).toHaveBeenCalledWith(
        'Анкета успешно сохранена! Теперь друзья смогут видеть ваши интересы.'
      );
    });
  });

  test('removes selected interest by tag remove button', async () => {
    setupLoadMocks({
      questionnaire: {
        interests: [{ tag: 'книги', details: '' }],
        avoid_gifts: []
      }
    });

    render(QuestionnaireScreen, { token: 'token-123' });

    await screen.findByText('книги');
    const removeButtons = screen.getAllByLabelText('Удалить тег');
    await fireEvent.click(removeButtons[0]);

    await waitFor(() => {
      expect(screen.queryByText('Удалить тег')).not.toBeInTheDocument();
      expect(screen.getAllByText('Пока ничего не выбрано.')).toHaveLength(2);
      expect(screen.getAllByText('книги')).toHaveLength(1);
    });
  });

});
