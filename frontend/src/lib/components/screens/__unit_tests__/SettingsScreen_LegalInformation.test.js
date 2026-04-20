import { jest } from '@jest/globals';
import { cleanup, fireEvent, render, screen } from '@testing-library/svelte';
import LegalInformation from '../settings/SettingsScreen_LegalInformation.svelte';

describe('SettingsScreen_LegalInformation', () => {
  afterEach(() => {
    cleanup();
    jest.restoreAllMocks();
  });

  // Тест №1 Отображение заголовка и юидических ссылок корректно
  test('renders header title and legal links correctly', () => {
    render(LegalInformation);

    // Проверка заголовков
    expect(screen.getByText('Настройки приватности')).toBeInTheDocument();
    expect(screen.getByText('Юридическая информация')).toBeInTheDocument();

    // Проверка ссылок и их атрибутов
    const privacyLink = screen.getByText(/Политика конфиденциальности/i);
    const tosLink = screen.getByText(/Условия использования/i);

    expect(privacyLink.closest('a')).toHaveAttribute('href', 'https://telegram.org/privacy');
    expect(tosLink.closest('a')).toHaveAttribute('href', 'https://telegram.org/tos');
    expect(privacyLink.closest('a')).toHaveAttribute('target', '_blank');
  });

  //Тест №2 проверка кнопки назад и вызов onGoBack
  test('calls onGoBack when back button is clicked', async () => {
    const onGoBack = jest.fn();
    render(LegalInformation, { onGoBack });

    const backBtn = screen.getByRole('button', { name: '←' });
    await fireEvent.click(backBtn);

    expect(onGoBack).toHaveBeenCalledTimes(1);
  });

});