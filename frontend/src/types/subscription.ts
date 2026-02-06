import { writable } from 'svelte/store';

// Тип подписки (может быть на пользователя или на вишлист)
export type SubscriptionType = 'user' | 'wishlist';

// Базовая информация о подписке на пользователя
export interface UserSubscriptionItem {
    type: 'user';
    sub_id: number;
    name: string;
    birth_date: string | null;
    photo: string | null;
    user_id: number;
    created_at: string;
    updated_at: string;
}

// Базовая информация о подписке на вишлист
export interface WishlistSubscriptionItem {
    type: 'wishlist';
    sub_id: number;
    wishlist_id: number;
    name: string;
    description: string | null;
    photo: string | null;
    type_privacy: 'public' | 'private' | 'secret';
    created_at: string;
    updated_at: string;
    total_wishes: number;
    owner_id: number;
    owner_name: string;
}

// Объединенный тип подписки
export type SubscriptionItem = UserSubscriptionItem | WishlistSubscriptionItem;

// Ответ с подписками
export interface SubscriptionsResponse {
    subscriptions: SubscriptionItem[];
    total: number;
}

// Ответ с подписчиками
export interface SubscribersResponse {
    subscribers: UserSubscriptionItem[];
    total: number;
}

// Обновление статуса посещения
export interface SubscribersVisitUpdate {
    status: boolean;
    updated_at: string;
}

// Запрос на подписку на пользователя
export interface SubscribeToUserRequest {
    target_user_id: number;
}

// Запрос на подписку на вишлист
export interface SubscribeToWishlistRequest {
    target_wishlist_id: number;
}

// Ответ проверки подписки
export interface CheckSubscriptionResponse {
    is_subscribed: boolean;
}

// Хранилище для подписок
export const subscriptionsStore = writable<SubscriptionItem[]>([]);
export const userSubscriptionsStore = writable<UserSubscriptionItem[]>([]);
export const wishlistSubscriptionsStore = writable<WishlistSubscriptionItem[]>([]);
export const subscribersStore = writable<UserSubscriptionItem[]>([]);

// Функции для работы с API подписок

// Подписаться на пользователя
export async function subscribeToUser(
    token: string, 
    targetUserId: number
): Promise<{ message: string }> {
    try {
        const response = await fetch('/api/v1/subscriptions/users', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ target_user_id: targetUserId })
        });
        
        if (!response.ok) {
            if (response.status === 400) {
                throw new Error('Невозможно подписаться на этого пользователя');
            }
            throw new Error('Ошибка подписки');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка подписки на пользователя:', error);
        throw error;
    }
}

// Подписаться на вишлист
export async function subscribeToWishlist(
    token: string, 
    targetWishlistId: number
): Promise<{ message: string }> {
    try {
        const response = await fetch('/api/v1/subscriptions/wishlists', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ target_wishlist_id: targetWishlistId })
        });
        
        if (!response.ok) {
            if (response.status === 400) {
                throw new Error('Невозможно подписаться на этот вишлист');
            }
            throw new Error('Ошибка подписки');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка подписки на вишлист:', error);
        throw error;
    }
}

// Отметить посещение подписки
export async function visitSubscribe(
    token: string, 
    subscribeId: number
): Promise<SubscribersVisitUpdate> {
    try {
        const response = await fetch(`/api/v1/subscriptions/visit/${subscribeId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 400) {
                throw new Error('Подписка не найдена');
            }
            throw new Error('Ошибка обновления посещения');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка обновления посещения:', error);
        throw error;
    }
}

// Отписаться от пользователя
export async function unsubscribeFromUser(
    token: string, 
    targetUserId: number
): Promise<{ message: string }> {
    try {
        const response = await fetch(`/api/v1/subscriptions/users/${targetUserId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Подписка не найдена');
            }
            throw new Error('Ошибка отписки');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка отписки от пользователя:', error);
        throw error;
    }
}

// Отписаться от вишлиста
export async function unsubscribeFromWishlist(
    token: string, 
    wishlistId: number
): Promise<{ message: string }> {
    try {
        const response = await fetch(`/api/v1/subscriptions/wishlists?wishlist_id=${wishlistId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Подписка не найдена');
            }
            throw new Error('Ошибка отписки');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка отписки от вишлиста:', error);
        throw error;
    }
}

// Получить все мои подписки
export async function getMySubscriptions(
    token: string,
    limit: number = 100
): Promise<SubscriptionsResponse> {
    try {
        const response = await fetch(`/api/v1/subscriptions/my?limit=${limit}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки подписок');
        }
        
        const data = await response.json();
        subscriptionsStore.set(data.subscriptions || []);
        return data;
    } catch (error) {
        console.error('Ошибка загрузки подписок:', error);
        subscriptionsStore.set([]);
        throw error;
    }
}

// Получить мои подписки на пользователей
export async function getMyUserSubscriptions(
    token: string,
    limit: number = 100
): Promise<SubscriptionsResponse> {
    try {
        const response = await fetch(`/api/v1/subscriptions/my/users?limit=${limit}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки подписок на пользователей');
        }
        
        const data = await response.json();
        const userSubs = data.subscriptions?.filter((sub: any) => sub.type === 'user') || [];
        userSubscriptionsStore.set(userSubs);
        return data;
    } catch (error) {
        console.error('Ошибка загрузки подписок на пользователей:', error);
        userSubscriptionsStore.set([]);
        throw error;
    }
}

// Получить мои подписки на вишлисты
export async function getMyWishlistSubscriptions(
    token: string,
    limit: number = 100
): Promise<SubscriptionsResponse> {
    try {
        const response = await fetch(`/api/v1/subscriptions/my/wishlists?limit=${limit}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки подписок на вишлисты');
        }
        
        const data = await response.json();
        const wishlistSubs = data.subscriptions?.filter((sub: any) => sub.type === 'wishlist') || [];
        wishlistSubscriptionsStore.set(wishlistSubs);
        return data;
    } catch (error) {
        console.error('Ошибка загрузки подписок на вишлисты:', error);
        wishlistSubscriptionsStore.set([]);
        throw error;
    }
}

// Получить подписки пользователя (публичные)
export async function getUserSubscriptions(
    token: string,
    userId: number,
    limit: number = 100
): Promise<SubscriptionsResponse> {
    try {
        const response = await fetch(`/api/v1/subscriptions/users/${userId}?limit=${limit}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 403) {
                throw new Error('Подписки этого пользователя приватны');
            }
            throw new Error('Ошибка загрузки подписок пользователя');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Ошибка загрузки подписок пользователя:', error);
        throw error;
    }
}

// Проверить подписку на пользователя
export async function checkUserSubscription(
    token: string,
    targetUserId: number
): Promise<boolean> {
    try {
        const response = await fetch(`/api/v1/subscriptions/check/user/${targetUserId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка проверки подписки');
        }
        
        const data: CheckSubscriptionResponse = await response.json();
        return data.is_subscribed;
    } catch (error) {
        console.error('Ошибка проверки подписки на пользователя:', error);
        return false;
    }
}

// Проверить подписку на вишлист
export async function checkWishlistSubscription(
    token: string,
    wishlistId: number
): Promise<boolean> {
    try {
        const response = await fetch(`/api/v1/subscriptions/check/wishlist/${wishlistId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка проверки подписки');
        }
        
        const data: CheckSubscriptionResponse = await response.json();
        return data.is_subscribed;
    } catch (error) {
        console.error('Ошибка проверки подписки на вишлист:', error);
        return false;
    }
}

// Получить моих подписчиков
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

// Вспомогательная функция для определения типа подписки
export function isUserSubscription(item: SubscriptionItem): item is UserSubscriptionItem {
    return item.type === 'user';
}

export function isWishlistSubscription(item: SubscriptionItem): item is WishlistSubscriptionItem {
    return item.type === 'wishlist';
}