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

});
