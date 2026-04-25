import { jest } from '@jest/globals';
import { tick } from 'svelte';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/svelte';
import InterfaceSettings from '../settings/SettingsScreen_InterfaceSettings.svelte';

Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
    })),
});

describe('InterfaceSettings Component', () => {
    let mockUserStore;
    const token = 'test-token';

    beforeEach(() => {
        localStorage.clear();
        document.documentElement.style.cssText = '';
        document.body.innerHTML = '';
        document.documentElement.removeAttribute('data-theme');
        mockUserStore = {
            ui: {
                theme: 'system',
                textSize: 'medium'
            }
        };
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            json: async () => ({ status: 'success' })
        });

        jest.spyOn(window, 'alert').mockImplementation(() => {});
        
        jest.clearAllMocks();
    });

    //Тест №1 - загружает настройки из localStorage при монтировании, если стор пуст
    test('should load settings from localStorage on mount if store is empty', async () => {
        localStorage.setItem('app-font-size', 'large');
        localStorage.setItem('app-theme', 'dark');
        
        global.fetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

        render(InterfaceSettings, { 
            token, 
            userStore: { ui: {} },
            onUpdateUser: jest.fn() 
        });

        await tick();
        
        // проверяем, что значения подтянулись в объект
        expect(screen.getByText('Большой')).toBeInTheDocument();
        expect(screen.getByText('Темная')).toBeInTheDocument();
    });

    //Тест №2 - переключает видимость выпадающего списка размера текста при клике
    test('should toggle textSize dropdown on click', async () => {
        render(InterfaceSettings, { 
            token: 'test-token', 
            userStore: { ui: { theme: 'system', textSize: 'medium' } } 
        });
        
        const toggle = screen.getByLabelText('Выберите размер текста').previousElementSibling;
        
        expect(toggle).toHaveAttribute('aria-expanded', 'false');

        await fireEvent.click(toggle);
        expect(toggle).toHaveAttribute('aria-expanded', 'true');

        await fireEvent.click(toggle);
        expect(toggle).toHaveAttribute('aria-expanded', 'false');
    });

    //Тест №3 - применяет CSS-переменные и классы при изменении размера текста
    test('should apply CSS variables and classes when text size changes', async () => {
        // подготавливаем внешний контейнер, который ищет компонент
        const appRoot = document.createElement('div');
        appRoot.className = 'app-root';
        document.body.appendChild(appRoot);

        render(InterfaceSettings, { 
            token, 
            userStore: mockUserStore,
            onUpdateUser: jest.fn()
        });

        const section = screen.getByText('Размер текста').closest('section');
        const toggle = within(section).getByRole('button', { name: /средний/i });
        await fireEvent.click(toggle); 

        const smallOption = screen.getByText('Малый');
        await fireEvent.click(smallOption);

        await tick();
        await new Promise(resolve => setTimeout(resolve, 0));

        expect(document.documentElement.style.getPropertyValue('--app-font-size')).toBe('14px');
        expect(appRoot).toHaveClass('small');
        expect(localStorage.getItem('app-font-size')).toBe('small');
    });

    //Тест №4 - корректно устанавливает атрибут data-theme для системной темы
    test('should set data-theme attribute correctly', async () => {
        render(InterfaceSettings, { 
            token, 
            userStore: mockUserStore,
            onUpdateUser: jest.fn()
        });

        const themeSection = screen.getByText('Тема').closest('section');
        
        const toggle = within(themeSection).getByRole('button', { name: /как в системе/i });
        await fireEvent.click(toggle);

        const lightOption = screen.getByText('Светлая');
        await fireEvent.click(lightOption);

        await tick();

        expect(document.documentElement.getAttribute('data-theme')).toBe('light');
        expect(localStorage.getItem('app-theme')).toBe('light');
    });

    //Тест №5 - вызывает API при изменении настроек
    test('should call API when setting is changed', async () => {
        const onUpdateUser = jest.fn();
        
        global.fetch.mockResolvedValueOnce({ 
            ok: true, 
            json: async () => ({ status: 'success' }) 
        });

        render(InterfaceSettings, { token, userStore: mockUserStore, onUpdateUser });

        const themeSection = screen.getByText('Тема').closest('section');
        
        const toggle = within(themeSection).getByRole('button', { name: /как в системе/i });
        await fireEvent.click(toggle);

        const darkOption = screen.getByText('Темная');
        await fireEvent.click(darkOption);

        await tick();

        expect(global.fetch).toHaveBeenCalledWith('/api/v1/users/me', expect.objectContaining({
            method: 'PUT',
            headers: expect.objectContaining({
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }),
            body: JSON.stringify({ theme: 'dark', text_size: 'medium' })
        }));

        await waitFor(() => {
            expect(onUpdateUser).toHaveBeenCalledWith({
                ui: { theme: 'dark', textSize: 'medium' }
            });
        });
    });

    //Тест №6 - вызывает onGoBack при клике на кнопку "Назад"
    test('should call onGoBack when back button is clicked', async () => {
        const onGoBack = jest.fn();
        render(InterfaceSettings, { token, userStore: mockUserStore, onGoBack });

        await fireEvent.click(screen.getByText('←'));
        expect(onGoBack).toHaveBeenCalled();
    });
});