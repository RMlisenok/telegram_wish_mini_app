import { writable, get } from 'svelte/store';
export interface User {
    id: string;
    fullName: string;
    birthDate: Date | null;
    avatarUrl: string;
    showSubscriptions: boolean;
    ui: {
        textSize: 'small' | 'medium' | 'large';
        theme: 'light' | 'dark' | 'system';
    };
}

export const userStore = writable<User>({
    id: '',
    fullName: '',
    birthDate: null,
    avatarUrl: '',
    showSubscriptions: true,
    ui: {
        textSize: 'medium',
        theme: 'system'
    }
});

export const tokenStore = writable<string | null>(null);
export const telegramStore = writable<any>(null);

function mapApiToUser(apiUser: any, token: string): User {
    console.log('Преобразование API данных:', apiUser);
    return {
        id: apiUser.id?.toString() || '',
        fullName: apiUser.name || 'Гость',
        birthDate: apiUser.birth_date ? new Date(apiUser.birth_date) : null,
        avatarUrl: apiUser.photo || '/default-avatar.png',
        showSubscriptions: apiUser.show_sub ?? true,
        ui: {
            textSize: apiUser.text_size || 'medium',
            theme: apiUser.theme || 'system'
        }
    };
}

export async function authenticateWithTelegram(tg: any): Promise<{ token: string; user: User }> {
    try {
        console.log('Начало аутентификации, tg:', tg);
        if (!tg?.initData || !tg?.initDataUnsafe?.user) {
            throw new Error('Нет данных от Telegram');
        }

        console.log('Отправка запроса на аутентификацию...');
        const response = await fetch('/api/v1/auth/telegram', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                initData: tg.initData, 
                user: tg.initDataUnsafe.user 
            })
        });

        console.log('Ответ получен, статус:', response.status);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Ошибка аутентификации');
        }

        const data = await response.json();
        console.log('Данные ответа:', data);

        if (!data.success || !data.token) {
            throw new Error(data.error || 'Ошибка получения токена');
        }

        const user = mapApiToUser(data.user, data.token);
    
        tokenStore.set(data.token); // Сохраняем токен
        userStore.set(user);
        
        return { token: data.token, user: user };
    } catch (error) {
        console.error('Ошибка аутентификации:', error);
        throw error;
    }
}

 export async function initializeApp(): Promise<{ 
    token: string | null; 
    user: User; 
    needsProfile: boolean 
}> {
    const tg = (window as any).Telegram?.WebApp;
    telegramStore.set(tg);
    
    if (!tg) {
        console.warn('Приложение запущено вне Telegram');
        return { token: null, user: getCurrentUser(), needsProfile: false };
    }
    
    try {
        const { token, user: apiUser } = await authenticateWithTelegram(tg);
        const user = getCurrentUser();
        const needsProfile = !apiUser.birthDate;
        
        return { token, user, needsProfile };
    } catch (error) {
        console.error('Ошибка инициализации:', error);
        return { token: null, user: getCurrentUser(), needsProfile: false };
    }
}

export function getCurrentUser(): User {
    return get(userStore);
}

export function getCurrentToken(): string | null {
    return get(tokenStore);
}