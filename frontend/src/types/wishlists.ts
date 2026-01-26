import { writable } from 'svelte/store';

export interface Wishlist {
    id: string;
    name: string;
    description: string;
    photo: string;
    typeprivacy: 'public' | 'restricted' | 'private';
    created_At: Date;
    updated_At: Date;
}

export const wishlistsStore = writable<Wishlist[]>([]);

export async function loadWishlists(token: string) {
    try {
        const response = await fetch('/api/v1/wishlists/', {
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
        
        const transformedWishlists = data.map((wishlist: any) => ({
            id: wishlist.id.toString(),
            title: wishlist.name,
            description: wishlist.description,
            photo: wishlist.photo,
            privacy: mapPrivacy(wishlist.typeprivacy),
            count: wishlist.wishes_count || 0
        }));
        
        wishlistsStore.set(transformedWishlists);
        
        return data;
    } catch (error) {
        console.error('Ошибка загрузки вишлистов:', error);
        wishlistsStore.set([]);
        throw error;
    }
}

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

export async function createWishlist(token: string, wishlistData: {
    name: string;
    description: string;
    photo: string;
    typeprivacy: 'public' | 'protected' | 'private';
}): Promise<Wishlist> {
    try {
        const response = await fetch('/api/v1/wishlists/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(wishlistData)
        });
        
        if (!response.ok) {
            throw new Error('Ошибка создания вишлиста');
        }
        
        const newWishlist = await response.json();
        
        return newWishlist;
    } catch (error) {
        console.error('Ошибка создания вишлиста:', error);
        throw error;
    }
}

export async function updateWishlist(
    token: string, 
    wishlistId: string, 
    wishlistData: {
        name: string;
        description: string;
        photo: string;
        typeprivacy: 'public' | 'protected' | 'private';
    }
): Promise<Wishlist> {
    try {
        const response = await fetch(`/api/v1/wishlists/${wishlistId}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(wishlistData)
        });
        
        if (!response.ok) {
            throw new Error('Ошибка обновления вишлиста');
        }
        
        const updatedWishlist = await response.json();
        
        return updatedWishlist;
    } catch (error) {
        console.error('Ошибка обновления вишлиста:', error);
        throw error;
    }
}

export async function deleteWishlist(token: string, wishlistId: string): Promise<void> {
    try {
        const response = await fetch(`/api/v1/wishlists/${wishlistId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Ошибка удаления вишлиста');
        }
        
        wishlistsStore.update(wishlists => 
            wishlists.filter(wishlist => wishlist.id !== wishlistId)
        );
        
    } catch (error) {
        console.error('Ошибка удаления вишлиста:', error);
        throw error;
    }
}
