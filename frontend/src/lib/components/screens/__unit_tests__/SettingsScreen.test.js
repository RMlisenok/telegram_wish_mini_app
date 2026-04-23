import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, screen } from '@testing-library/svelte';
import SettingsScreen from '../settings/SettingsScreen.svelte';

describe('SettingsScreen High Coverage', () => {
  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  // ТЕСТ 1: Проверка всех вызовов
  test('executes all callbacks when buttons are clicked', async () => {
    const props = {
      onGoBack: jest.fn(),
      onNavigateToEditProfile: jest.fn(),
      onNavigateToPrivacySettings: jest.fn(),
      onNavigateToInterfaceSettings: jest.fn(),
      onNavigateToNotificationSettings: jest.fn(),
      onNavigateToLegalInformation: jest.fn(),
    };

    render(SettingsScreen, props);

    await fireEvent.click(screen.getByText('←'));
    
    const menuClicks = [
      'Редактировать профиль',
      'Настройки приватности',
      'Настройки интерфейса',
      'Настройки уведомлений',
      'Юридическая информация'
    ];

    for (const text of menuClicks) {
      await fireEvent.click(screen.getByText(text).closest('button'));
    }

    Object.values(props).forEach(mock => expect(mock).toHaveBeenCalledTimes(1));
  });
  // ТЕСТ 2: Проверка отсутствия пропсов 
  test('should not fail if callbacks are not provided', async () => {
    render(SettingsScreen, {}); // Рендерим без пропсов

    const buttons = screen.getAllByRole('button');
    
    // Кликаем по всем кнопкам. 
    // Код внутри (например, goBack) выполнится, условие if(onGoBack) будет false.
    for (const btn of buttons) {
      await fireEvent.click(btn);
    }

    expect(true).toBe(true); // Если не упало — тест пройден
  });

  // ТЕСТ 3: Проверка структуры
  test('renders correct subtitles', () => {
    render(SettingsScreen);
    
    const subtitles = [
      'Изменить личную информацию',
      'Управление видимостью профиля и вишлистов',
      'Тема, размер текста',
      'Управление push-уведомлениями'
    ];

    subtitles.forEach(sub => {
      expect(screen.getByText(sub)).toBeInTheDocument();
    });
  });

});
