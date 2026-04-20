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

  // Тест №3 не падает, если пропс onGoBack не передан
  test('does not crash when onGoBack is not provided', async () => {
    render(LegalInformation, { onGoBack: undefined });
    
    const backBtn = screen.getByRole('button', { name: '←' });
    
    // Клик не должен вызывать ошибок, несмотря на отсутствие пропса
    await fireEvent.click(backBtn);
    
    expect(true).toBe(true); 
  });

  // Тест №4 Применяет правильные стили к заголовку и кнопке назад
  test('applies correct CSS styles to the header and back button', () => {
    const { container } = render(LegalInformation);

    // Проверка стилей заголовка
    const title = screen.getByText('Настройки приватности');
    const titleStyle = window.getComputedStyle(title);
    expect(titleStyle.fontSize).toBe('20px');
    expect(titleStyle.fontWeight).toBe('600');

    // Проверка размеров кнопки "Назад" (зона нажатия 44x44)
    const backBtn = container.querySelector('.back-btn');
    const btnStyle = window.getComputedStyle(backBtn);
    expect(btnStyle.width).toBe('44px');
    expect(btnStyle.height).toBe('44px');
    expect(btnStyle.display).toBe('flex');
  });

  //Тест №5 Проверка разметки для списка ссылок
  test('applies correct layout for links list', () => {
    const { container } = render(LegalInformation);
    const linksList = container.querySelector('.links');
    const style = window.getComputedStyle(linksList);

    expect(style.display).toBe('flex');
    expect(style.flexDirection).toBe('column');
    expect(style.gap).toBe('4px');
  });
});