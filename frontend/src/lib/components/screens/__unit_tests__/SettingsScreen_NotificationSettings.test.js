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

});
