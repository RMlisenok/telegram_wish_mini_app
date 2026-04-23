import { jest } from '@jest/globals';
import { cleanup, render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import PrivacySettings from '../settings/SettingsScreen_PrivacySettings.svelte';

describe('PrivacySettings Component', () => {
    const token = 'test-token-456';
    const mockUserStore = {
        showSubscriptions: true
    };
    
    let onUpdateUser;
    let onGoBack;

    beforeEach(() => {
        global.fetch = jest.fn();
        global.alert = jest.fn();
        onUpdateUser = jest.fn();
        onGoBack = jest.fn();
        jest.clearAllMocks();
    });

    afterEach(() => {
        cleanup();
    });

    //Тест №1 - рендеринг и инициализация из пропсов
    test('should initialize with value from userStore', () => {
        render(PrivacySettings, { 
            token, 
            userStore: mockUserStore, 
            onUpdateUser, 
            onGoBack 
        });

        const checkbox = document.querySelector('#showSubscriptions');
        expect(checkbox.checked).toBe(true);
    });

    //Тест №2- переключение состояния по клику
    test('should toggle privacy setting on click', async () => {
        render(PrivacySettings, { 
            token, 
            userStore: mockUserStore, 
            onUpdateUser, 
            onGoBack 
        });

        const button = screen.getByRole('button', { name: /Показывать мои подписки/i });
        await fireEvent.click(button);

        const checkbox = document.querySelector('#showSubscriptions');
        expect(checkbox.checked).toBe(false);
    });

    //Тест №3 - управление клавиатурой (Enter/Space)
    test('should toggle setting on Space and Enter keys', async () => {
        render(PrivacySettings, { 
            token, 
            userStore: mockUserStore, 
            onUpdateUser, 
            onGoBack 
        });

        const button = screen.getByRole('button', { name: /Показывать мои подписки/i });
        const checkbox = document.querySelector('#showSubscriptions');

        // Тестируем Space
        await fireEvent.keyDown(button, { key: ' ' });
        expect(checkbox.checked).toBe(false);

        // Тестируем Enter
        await fireEvent.keyDown(button, { key: 'Enter' });
        expect(checkbox.checked).toBe(true);
    });

    //Тест №4 - успешное сохранение
    test('should save settings and call onUpdateUser on success', async () => {
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'success' })
        });

        render(PrivacySettings, { 
            token, 
            userStore: { showSubscriptions: false }, 
            onUpdateUser, 
            onGoBack 
        });

        // Включаем настройку
        await fireEvent.click(screen.getByRole('button', { name: /Показывать мои подписки/i }));
        
        // Кликаем сохранить
        const saveBtn = screen.getByText(/Сохранить изменения/i);
        await fireEvent.click(saveBtn);

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith('/api/v1/users/me', expect.objectContaining({
                method: 'PUT',
                body: JSON.stringify({ show_sub: true })
            }));
            expect(onUpdateUser).toHaveBeenCalledWith({ showSubscriptions: true });
            expect(global.alert).toHaveBeenCalledWith('Изменения успешно сохранены');
            expect(onGoBack).toHaveBeenCalled();
        });
    });

    //Тест №5 - обработка ошибки сервера
    test('should handle server error on save', async () => {
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
        global.fetch.mockResolvedValueOnce({ ok: false });

        render(PrivacySettings, { token, userStore: mockUserStore, onUpdateUser, onGoBack });

        await fireEvent.click(screen.getByText(/Сохранить изменения/i));

        await waitFor(() => {
            expect(global.alert).toHaveBeenCalledWith(expect.stringContaining('Не удалось сохранить изменения'));
            expect(consoleSpy).toHaveBeenCalled();
        });
        consoleSpy.mockRestore();
    });

});