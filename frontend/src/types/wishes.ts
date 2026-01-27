import { writable } from 'svelte/store';

export interface Wish {
    id: string;
    name: string;
    photo: string;
    url_gift: string;
    price: number;
    currency: 'RUB' | 'BYN' | 'USD' | 'EUR' | 'UAH' | 'KZT';
    description: string;
    is_booked: boolean;
    status_is_finished: boolean;
    created_At: Date;
    updated_At: Date;
}

export const wishesStore = writable<Wish[]>([]);

export async function loadWishes(token: string) {
    try {
        const response = await fetch('/api/v1/wishes/', {
            method: 'GET',
            headers: {
                "Authorization": 'Bearer ' + token,
                "Content-Type": "application/json"
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки вишлистов');
        }
        
        const data = await response.json();
        console.log(data)
        
        const transformedWishlists = data.map((wish: any) => ({
            id: wish.id.toString(),
            name: wish.name,
            photo: wish.photo,
            url_gift: wish.url_gift,
            price: wish.price,
            currency: wish.currency,
            is_booked: wish.is_booked
        }));
        
        wishesStore.set(transformedWishlists);
        
        return data;
    } catch (error) {
        console.error('Ошибка загрузки вишлистов:', error);
        wishesStore.set([]);
        throw error;
    }
}