import { writable } from 'svelte/store';

export const telegram = writable<typeof window.Telegram.WebApp | null>(null);
export const user = writable<any>(null);
export const initData = writable<string>('');

export function initializeTelegram() {
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
        const tg = window.Telegram.WebApp;
        
        // Сохраняем в store
        telegram.set(tg);
        initData.set(tg.initData);
        user.set(tg.initDataUnsafe?.user);
        
        // Инициализируем WebApp
        tg.ready();
        tg.expand();
        tg.enableClosingConfirmation();
        
        // Устанавливаем тему
        tg.setHeaderColor(tg.themeParams.bg_color || '#2481cc');
        tg.setBackgroundColor(tg.themeParams.bg_color || '#ffffff');
        
        return tg;
    }
    return null;
}

// Типы для TypeScript (если не устанавливаете @twa-dev/types)
declare global {
    interface Window {
        Telegram: {
            WebApp: any;
        };
    }
}