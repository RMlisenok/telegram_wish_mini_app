import { jest } from '@jest/globals';
import { cleanup, render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import { notificationSettingsStore } from '../../../stores/data';
import NotificationSettings from '../settings/SettingsScreen_NotificationSettings.svelte';

describe('NotificationSettings Component', () => {
    const token = 'test-token-123';
    const mockSettings = {
        new_followers: true,
        access_requests: false,
        birt_after: true,
        birt_before: false
    };

    beforeEach(() => {
        global.fetch = jest.fn();
        global.alert = jest.fn();
        // Сбрасываем стор в начальное состояние
        notificationSettingsStore.set({
            birthdayReminders: false,
            newFollowers: false,
            postBirthdayNotifications: false,
            wishlistAccessRequests: false
        });
        jest.clearAllMocks();
    });

    afterEach(() => {
        cleanup();
    });

    //Тест №1 - загружает настройки с сервера при монтировании
    test('should fetch and display settings on mount', async () => {
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => mockSettings
        });

        render(NotificationSettings, { token });

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith('/api/v1/settings/notifications', expect.any(Object));
            
            const checkbox = document.querySelector('#newFollowers'); 
            
            expect(checkbox).not.toBeNull();
            expect(checkbox.checked).toBe(true);
        });
    });

    //Тест №2 - переключает состояние настройки при клике
    test('should toggle setting state on click', async () => {
        global.fetch.mockResolvedValueOnce({ ok: true, json: async () => mockSettings });
        render(NotificationSettings, { token });

        const button = await screen.findByRole('button', { name: /Новые подписчики/i });
        await fireEvent.click(button);

        //проверяем состояние вложенного инпута по его ID
        const checkbox = document.querySelector('#newFollowers');
        expect(checkbox.checked).toBe(false);
    });

    //Тест №3 - поддерживает управление с клавиатуры (Enter/Space)
    test('should toggle setting on Enter key press', async () => {
        global.fetch.mockResolvedValueOnce({ ok: true, json: async () => mockSettings });
        render(NotificationSettings, { token });

        const button = await screen.findByRole('button', { name: /Новые подписчики/i });
        const checkbox = document.querySelector('#newFollowers');

        await waitFor(() => expect(checkbox.checked).toBe(true));

        await fireEvent.keyDown(button, { key: 'Enter' });
        
        expect(checkbox.checked).toBe(false);
    });

    //Тест №4 - успешно сохраняет настройки и вызывает навигацию назад
    test('should save settings and call onGoBack on success', async () => {
        const onGoBack = jest.fn();
        
        //мок для GET (загрузка)
        global.fetch.mockResolvedValueOnce({ ok: true, json: async () => mockSettings });
        //мок для PATCH (сохранение)
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ status: 'success', update_data: mockSettings })
        });

        render(NotificationSettings, { token, onGoBack });

        const saveBtn = screen.getByText(/Сохранить изменения/i);
        await fireEvent.click(saveBtn);

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith('/api/v1/settings/notifications', expect.objectContaining({
                method: 'PATCH'
            }));
            expect(onGoBack).toHaveBeenCalled();
        });
    });

    //Тест №5 - проверяет корректность маппинга данных при сохранении
    test('should send correct field names to API on save', async () => {
        global.fetch.mockResolvedValueOnce({ ok: true, json: async () => mockSettings });
        render(NotificationSettings, { token });

        const toggle = await screen.findByLabelText(/Заявки на доступ к вишлистам/i);
        await fireEvent.click(toggle);

        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ update_data: mockSettings })
        });

        await fireEvent.click(screen.getByText(/Сохранить изменения/i));

        await waitFor(() => {
            const lastCall = global.fetch.mock.calls.find(call => call[1].method === 'PATCH');
            const body = JSON.parse(lastCall[1].body);
            
            // Проверяем, что в API ушло access_requests, а не wishlistAccessRequests
            expect(body).toHaveProperty('access_requests', true);
            expect(body).toHaveProperty('new_followers', true);
        });
    });

    //Тест №6 - корректно работает кнопка "Назад"
    test('should call onGoBack when back button is clicked', async () => {
        const onGoBack = jest.fn();
        global.fetch.mockResolvedValueOnce({ ok: true, json: async () => mockSettings });
        
        render(NotificationSettings, { onGoBack, token });

        await fireEvent.click(screen.getByText('←'));
        expect(onGoBack).toHaveBeenCalled();
    });

});
