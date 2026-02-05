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