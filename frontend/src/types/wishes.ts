import { writable } from 'svelte/store';

export interface Wish {
    id: string;
    name: string;
    photo: string;
    url_gift: string;
    price: number;
    currency: 'RUB' | 'BYN' | 'USD' | 'EUR' | 'UAH' | 'KZT' | null;
    description: string;
    is_booked: boolean;
    status_is_finished: boolean;
    created_At: Date;
    updated_At: Date;
}

export const wishesStore = writable<Wish[]>([]);

export async function loadWishes(token: string) {
    try {
        const response = await fetch('/api/v1/wishes/finish?is_finish=false', {
            method: 'GET',
            headers: {
                "Authorization": 'Bearer ' + token,
                "Content-Type": "application/json"
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки желаний');
        }
        
        const data = await response.json();
        console.log(data)
        
        const transformedWishlists = data.map((wish: any) => ({
            id: wish.id.toString(),
            name: wish.name,
            photo: wish.photo,
            url_gift: wish.url_gift,
            price: wish.price,
            currency: wish.currency || null,
            is_booked: wish.is_booked
        }));
        
        wishesStore.set(transformedWishlists);
        console.log(wishesStore);
        return data;
    } catch (error) {
        console.error('Ошибка загрузки желаний:', error);
        wishesStore.set([]);
        throw error;
    }
}

export async function loadFinishedWishes(token: string) {
    try {
        const response = await fetch('/api/v1/wishes/finish?is_finish=true', {
            method: 'GET',
            headers: {
                "Authorization": 'Bearer ' + token,
                "Content-Type": "application/json"
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки желаний');
        }
        
        const data = await response.json();
        console.log(data)
        
        const transformedWishlists = data.map((wish: any) => ({
            id: wish.id.toString(),
            name: wish.name,
            photo: wish.photo,
            url_gift: wish.url_gift,
            price: wish.price,
            currency: wish.currency || null,
            is_booked: wish.is_booked,
            status_is_finished: wish.status_is_finished,
            description: wish.description || "",
            created_At: new Date(wish.created_at),
            updated_At: new Date(wish.updated_at)
        }));
        
        wishesStore.set(transformedWishlists);
        console.log(wishesStore);
        return data;
    } catch (error) {
        console.error('Ошибка загрузки желаний:', error);
        wishesStore.set([]);
        throw error;
    }
}

export async function createWish(token: string, wishData: {
    name: string;
    photo: string;
    url_gift: string;
    price: number;
    currency?: 'RUB' | 'BYN' | 'USD' | 'EUR' | 'UAH' | 'KZT' | null;
    description: string;
    is_booked: boolean;
    status_is_finished: boolean;
}): Promise<Wish> {
    try {
        const requestData: any = {
            name: wishData.name,
            description: wishData.description,
            photo: wishData.photo,
            url_gift: wishData.url_gift,
            price: wishData.price,
            is_booked: wishData.is_booked,
            status_is_finished: wishData.status_is_finished
        };
        
        if (wishData.currency !== null && wishData.currency !== undefined) {
            requestData.currency = wishData.currency;
        }

        const response = await fetch('/api/v1/wishes/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(wishData)
        });
        
        if (!response.ok) {
            throw new Error('Ошибка создания желания');
        }
        
        const newWishlist = await response.json();
        
        return newWishlist;
    } catch (error) {
        console.error('Ошибка создания желания:', error);
        throw error;
    }
}

export async function updateWish(
    token: string, 
    wishId: string, 
    wishData: {
        name: string;
        description: string;
        photo: string;
        url_gift: string;
        price: number;
        currency: 'RUB' | 'BYN' | 'USD' | 'EUR' | 'UAH' | 'KZT' | null;
        is_booked: boolean;
        status_is_finished: boolean;
    }
): Promise<Wish> {
    try {
        const response = await fetch(`/api/v1/wishes/${wishId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(wishData)
        });
        
        if (!response.ok) {
            throw new Error('Ошибка обновления желания');
        }
        
        const updatedWish = await response.json();
        
        return updatedWish;
    } catch (error) {
        console.error('Ошибка обновления желания:', error);
        throw error;
    }
}

export async function deleteWish(token: string, wishId: string): Promise<boolean> {
    try {
        const response = await fetch(`/api/v1/wishes/${wishId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Желание не найдено');
            }
            throw new Error('Ошибка удаления желания');
        }
        
        return true;
    } catch (error) {
        console.error('Ошибка удаления желания:', error);
        throw error;
    }
}

// Функция для обновления статуса "Исполнено"
export async function updateWishStatus(
    token: string,
    wishId: string,
    statusData: {
        status_is_finished: boolean;
        is_booked?: boolean;
    }
): Promise<Wish> {
    try {
        // 1. Сначала получаем текущие данные желания
        const currentResponse = await fetch(`/api/v1/wishes/${wishId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!currentResponse.ok) {
            const errorText = await currentResponse.text();
            console.error('Ошибка получения текущих данных:', errorText);
            throw new Error('Не удалось получить данные желания');
        }
        
        const currentWish = await currentResponse.json();
        console.log('Текущие данные желания:', currentWish);
        
        // 2. Подготавливаем полные данные для обновления
        const updateData = {
            name: currentWish.name || '',
            description: currentWish.description || '',
            photo: currentWish.photo || '',
            url_gift: currentWish.url_gift || '',
            price: currentWish.price,
            currency: currentWish.currency,
            status_is_finished: statusData.status_is_finished,
            is_booked: statusData.is_booked !== undefined ? statusData.is_booked : false
        };
        
        console.log('Данные для отправки:', updateData);
        
        // 3. Отправляем обновление
        const response = await fetch(`/api/v1/wishes/${wishId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Ошибка сервера при обновлении:', errorText);
            throw new Error('Ошибка обновления статуса желания');
        }
        
        const updatedWish = await response.json();
        console.log('Обновленное желание:', updatedWish);
        
        return updatedWish;
    } catch (error) {
        console.error('Ошибка обновления статуса желания:', error);
        throw error;
    }
}

// Функция для удаления желания из всех вишлистов
export async function removeWishFromAllWishlists(
    token: string,
    wish_id: string
): Promise<boolean> {
    try {
        const response = await fetch(`/api/v1/wishes/wishlists/${wish_id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Желание не найдено');
            }
            throw new Error('Ошибка удаления желания из вишлистов');
        }
        
        return true;
    } catch (error) {
        console.error('Ошибка удаления желания из вишлистов:', error);
        throw error;
    }
}
