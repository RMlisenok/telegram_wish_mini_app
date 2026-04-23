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

});