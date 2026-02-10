import { writable } from 'svelte/store';

// Типы для подписчика
export interface SubscriberItem {
    type: 'user';
    sub_id: number;
    name: string;
    birth_date: string | null;
    photo: string | null;
    user_id: number;
    created_at: string;
    updated_at: string;
}

// Ответ с подписчиками
export interface SubscribersResponse {
    subscribers: SubscriberItem[];
    total: number;
}

// Хранилище для подписчиков
export const subscribersStore = writable<SubscriberItem[]>([]);

// Функция для получения подписчиков текущего пользователя
export async function getMySubscribers(
    token: string,
    isDesc: boolean = true,
    limit: number = 100
): Promise<SubscribersResponse> {
    try {
        const response = await fetch(
            `/api/v1/subscriptions/my/subscribers?is_desc=${isDesc}&limit=${limit}`, 
            {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }
        );
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки подписчиков');
        }
        
        const data = await response.json();
        subscribersStore.set(data.subscribers || []);
        return data;
    } catch (error) {
        console.error('Ошибка загрузки подписчиков:', error);
        subscribersStore.set([]);
        throw error;
    }
}