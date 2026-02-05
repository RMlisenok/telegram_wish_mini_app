// mainScreenData.js
import { writable, derived } from 'svelte/store';

export interface MainWishlist {
    id: string;
    name: string;
    description: string;
    photo: string;
    typeprivacy: 'public' | 'restricted' | 'private';
    created_at: string;
    updated_at: string;
    count: number;
}

export interface MainSubscription {
    type_sub: boolean;
    user?: {
        name: string;
        photo: string;
        user_id: number;
        birth_date: string;
    };
    wishlist?: {
        name: string;
        photo: string;
        description: string;
        typeprivacy: 'public' | 'restricted' | 'private';
        owner_name: string;
        id: number;
    };
}

export interface MainSubscriber {
    name: string;
    photo: string;
    birth_date: string;
    subscription_date: string;
}

// Хранилища для MainScreen
export const mainWishlistsStore = writable<MainWishlist[]>([]);
export const mainSubscriptionsStore = writable<MainSubscription[]>([]);
export const mainSubscribersStore = writable<MainSubscriber[]>([]);

export const totalWishesStore = writable(0);
export const totalWishlistsStore = writable(0);
export const totalSubscribersStore = writable(0);
export const totalSubscriptionsStore = writable(0);

// Функция загрузки всех данных профиля для MainScreen
export async function loadMainScreenData(token: string) {
    if (!token) {
        console.error('Токен не предоставлен');
        return;
    }

    try {
        const response = await fetch('/api/v1/users/me', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(data);
        
        // Обновляем вишлисты
        const transformedWishlists = data.wishlist_last_update.map((wl: any) => ({
            id: wl.id.toString(),
            name: wl.name,
            description: wl.description,
            photo: wl.photo,
            typeprivacy: mapPrivacy(wl.typeprivacy),
            created_at: wl.created_at,
            updated_at: wl.updated_at,
            count: wl.wishes_count
        }));
        mainWishlistsStore.set(transformedWishlists);
        
        // Обновляем подписки
        const transformedSubscriptions = data.subscription.subscription.subscriptions.map((sub: any) => {
            if (sub.type === 'user') {
                return {
                    type_sub: true,
                    user: {
                        name: sub.name,
                        photo: sub.photo,
                        user_id: sub.user_id,
                        birth_date: formatDateToDDMMYYYY(sub.birth_date)
                    }
                };
            } else {
                return {
                    type_sub: false,
                    wishlist: {
                        name: sub.name,
                        photo: sub.photo,
                        description: sub.description,
                        typeprivacy: mapPrivacy(sub.typeprivacy),
                        owner_name: sub.owner_name,
                        id: sub.id
                    }
                };
            }
        });
        mainSubscriptionsStore.set(transformedSubscriptions);
        
        // Обновляем подписчиков
        const transformedSubscribers = data.subsсribers.subscribers.map((sub: any) => ({
            name: sub.name,
            photo: sub.photo,
            birth_date: formatDateToDDMMYYYY(sub.birth_date)
        }));
        mainSubscribersStore.set(transformedSubscribers);
        console.log(data.subsсribers.total);

        totalWishesStore.set(data.total_wish || 0);
        totalWishlistsStore.set(data.total_wishlist || 0);
        totalSubscribersStore.set(data.subsсribers?.total || 0);
        totalSubscriptionsStore.set(data.subscription.subscription?.total || 0);
        
        return {
            wishlists: transformedWishlists,
            subscriptions: transformedSubscriptions,
            subscribers: transformedSubscribers,
            totalWish: data.total_wish,
            totalWishlist: data.total_wishlist,
            totalSubscribers: data.subsсribers.total,
            totalSubscription: data.subscription.subscription.total
        };
        
    } catch (error) {
        console.error('Ошибка загрузки данных для MainScreen:', error);
        throw error;
    }
}

export function formatDateToDDMMYYYY(dateString: string): string {
    if (!dateString) return '';
    
    const [year, month, day] = dateString.split('-');
    if (!year || !month || !day) return dateString; 
    
    return `${day}.${month}.${year}`;
}

// Вспомогательная функция для преобразования privacy
function mapPrivacy(typeprivacy: string): 'public' | 'restricted' | 'private' {
    switch (typeprivacy) {
        case 'public':
            return 'public';
        case 'protected':
            return 'restricted';
        case 'private':
            return 'private';
        default:
            return 'private';
    }
}
