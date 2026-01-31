// import { writable } from 'svelte/store';

// export interface SubscriptionBase {
//     type: 'user' | 'wishlist';
//     created_at: Date;
//     updated_at: Date;
// }

// export interface UserSubscription extends SubscriptionBase {
//     type: 'user';
//     sub_id: number;
//     name: string;
//     photo: string | null;
//     user_id: number;
// }

// export interface WishlistSubscription extends SubscriptionBase {
//     type: 'wishlist';
//     sub_id: number;
//     wishlist_id: number;
//     name: string;
//     description: string | null;
//     photo: string | null;
//     type_privacy: string;
//     owner_id: number;
//     owner_name: string;
// }

// export interface SubscriptionsResponse {
//     subscriptions: Array<UserSubscription | WishlistSubscription>;
//     total: number;
// }

// export interface CheckSubscriptionResponse {
//     is_subscribed: boolean;
// }

// export interface SubscribeToUserRequest {
//     target_user_id: number;
// }

// export interface SubscribeToWishlistRequest {
//     target_wishlist_id: number;
// }

// export const subscriptionsStore = writable<SubscriptionsResponse>({
//     subscriptions: [],
//     total: 0
// });

// // Получение всех моих подписок
// export async function getMySubscriptions(
//     token: string, 
//     limit: number = 100
// ): Promise<SubscriptionsResponse> {
//     try {
//         const response = await fetch(`/api/v1/subscriptions/my?limit=${limit}`, {
//             method: 'GET',
//             headers: {
//                 'Authorization': `Bearer ${token}`,
//                 'Content-Type': 'application/json'
//             }
//         });
        
//         if (!response.ok) {
//             throw new Error('Ошибка загрузки подписок');
//         }
        
//         const data = await response.json();
//         subscriptionsStore.set(data);
//         return data;
//     } catch (error) {
//         console.error('Ошибка загрузки подписок:', error);
//         throw error;
//     }
// }

// // Получение моих подписок на пользователей
// export async function getMyUserSubscriptions(
//     token: string, 
//     limit: number = 100
// ): Promise<SubscriptionsResponse> {
//     try {
//         const response = await fetch(`/api/v1/subscriptions/my/users?limit=${limit}`, {
//             method: 'GET',
//             headers: {
//                 'Authorization': `Bearer ${token}`,
//                 'Content-Type': 'application/json'
//             }
//         });
        
//         if (!response.ok) {
//             throw new Error('Ошибка загрузки подписок на пользователей');
//         }
        
//         const data = await response.json();
//         return data;
//     } catch (error) {
//         console.error('Ошибка загрузки подписок на пользователей:', error);
//         throw error;
//     }
// }

// // Получение моих подписок на вишлисты
// export async function getMyWishlistSubscriptions(
//     token: string, 
//     limit: number = 100
// ): Promise<SubscriptionsResponse> {
//     try {
//         const response = await fetch(`/api/v1/subscriptions/my/wishlists?limit=${limit}`, {
//             method: 'GET',
//             headers: {
//                 'Authorization': `Bearer ${token}`,
//                 'Content-Type': 'application/json'
//             }
//         });
        
//         if (!response.ok) {
//             throw new Error('Ошибка загрузки подписок на вишлисты');
//         }
        
//         const data = await response.json();
//         return data;
//     } catch (error) {
//         console.error('Ошибка загрузки подписок на вишлисты:', error);
//         throw error;
//     }
// }

// // Получение подписок пользователя (публичных)
// export async function getUserSubscriptions(
//     token: string, 
//     userId: number,
//     limit: number = 100
// ): Promise<SubscriptionsResponse> {
//     try {
//         const response = await fetch(`/api/v1/subscriptions/users/${userId}?limit=${limit}`, {
//             method: 'GET',
//             headers: {
//                 'Authorization': `Bearer ${token}`,
//                 'Content-Type': 'application/json'
//             }
//         });
        
//         if (!response.ok) {
//             const error = await response.json();
//             throw new Error(error.detail || 'Ошибка загрузки подписок пользователя');
//         }
        
//         const data = await response.json();
//         return data;
//     } catch (error) {
//         console.error('Ошибка загрузки подписок пользователя:', error);
//         throw error;
//     }
// }

// // Подписка на пользователя
// export async function subscribeToUser(
//     token: string, 
//     targetUserId: number
// ): Promise<{ message: string }> {
//     try {
//         const requestData: SubscribeToUserRequest = {
//             target_user_id: targetUserId
//         };

//         const response = await fetch('/api/v1/subscriptions/users', {
//             method: 'POST',
//             headers: {
//                 'Authorization': `Bearer ${token}`,
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(requestData)
//         });
        
//         if (!response.ok) {
//             const error = await response.json();
//             throw new Error(error.detail || 'Ошибка подписки на пользователя');
//         }
        
//         const data = await response.json();
//         // Обновляем список подписок
//         await getMySubscriptions(token);
//         return data;
//     } catch (error) {
//         console.error('Ошибка подписки на пользователя:', error);
//         throw error;
//     }
// }

// // Подписка на вишлист
// export async function subscribeToWishlist(
//     token: string, 
//     targetWishlistId: number
// ): Promise<{ message: string }> {
//     try {
//         const requestData: SubscribeToWishlistRequest = {
//             target_wishlist_id: targetWishlistId
//         };

//         const response = await fetch('/api/v1/subscriptions/wishlists', {
//             method: 'POST',
//             headers: {
//                 'Authorization': `Bearer ${token}`,
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(requestData)
//         });
        
//         if (!response.ok) {
//             const error = await response.json();
//             throw new Error(error.detail || 'Ошибка подписки на вишлист');
//         }
        
//         const data = await response.json();
//         // Обновляем список подписок
//         await getMySubscriptions(token);
//         return data;
//     } catch (error) {
//         console.error('Ошибка подписки на вишлист:', error);
//         throw error;
//     }
// }

// // Отписка от пользователя
// export async function unsubscribeFromUser(
//     token: string, 
//     targetUserId: number
// ): Promise<{ message: string }> {
//     try {
//         const response = await fetch(`/api/v1/subscriptions/users/${targetUserId}`, {
//             method: 'DELETE',
//             headers: {
//                 'Authorization': `Bearer ${token}`,
//                 'Content-Type': 'application/json'
//             }
//         });
        
//         if (!response.ok) {
//             const error = await response.json();
//             throw new Error(error.detail || 'Ошибка отписки от пользователя');
//         }
        
//         const data = await response.json();
//         // Обновляем список подписок
//         await getMySubscriptions(token);
//         return data;
//     } catch (error) {
//         console.error('Ошибка отписки от пользователя:', error);
//         throw error;
//     }
// }

// // Отписка от вишлиста
// export async function unsubscribeFromWishlist(
//     token: string, 
//     targetWishlistId: number
// ): Promise<{ message: string }> {
//     try {
//         const response = await fetch(`/api/v1/subscriptions/wishlists/${targetWishlistId}`, {
//             method: 'DELETE',
//             headers: {
//                 'Authorization': `Bearer ${token}`,
//                 'Content-Type': 'application/json'
//             }
//         });
        
//         if (!response.ok) {
//             const error = await response.json();
//             throw new Error(error.detail || 'Ошибка отписки от вишлиста');
//         }
        
//         const data = await response.json();
//         // Обновляем список подписок
//         await getMySubscriptions(token);
//         return data;
//     } catch (error) {
//         console.error('Ошибка отписки от вишлиста:', error);
//         throw error;
//     }
// }

// // Проверка подписки на пользователя
// export async function checkUserSubscription(
//     token: string, 
//     userId: number
// ): Promise<CheckSubscriptionResponse> {
//     try {
//         const response = await fetch(`/api/v1/subscriptions/check/user/${userId}`, {
//             method: 'GET',
//             headers: {
//                 'Authorization': `Bearer ${token}`,
//                 'Content-Type': 'application/json'
//             }
//         });
        
//         if (!response.ok) {
//             const error = await response.json();
//             throw new Error(error.detail || 'Ошибка проверки подписки на пользователя');
//         }
        
//         return await response.json();
//     } catch (error) {
//         console.error('Ошибка проверки подписки на пользователя:', error);
//         throw error;
//     }
// }

// // Проверка подписки на вишлист
// export async function checkWishlistSubscription(
//     token: string, 
//     wishlistId: number
// ): Promise<CheckSubscriptionResponse> {
//     try {
//         const response = await fetch(`/api/v1/subscriptions/check/wishlist/${wishlistId}`, {
//             method: 'GET',
//             headers: {
//                 'Authorization': `Bearer ${token}`,
//                 'Content-Type': 'application/json'
//             }
//         });
        
//         if (!response.ok) {
//             const error = await response.json();
//             throw new Error(error.detail || 'Ошибка проверки подписки на вишлист');
//         }
        
//         return await response.json();
//     } catch (error) {
//         console.error('Ошибка проверки подписки на вишлист:', error);
//         throw error;
//     }
// }

// // Обновление статуса посещения (отметка подписки как просмотренной)
// export async function visitSubscription(
//     token: string, 
//     subscribeId: number
// ): Promise<any> {
//     try {
//         const response = await fetch(`/api/v1/subscriptions/visit/${subscribeId}`, {
//             method: 'PATCH',
//             headers: {
//                 'Authorization': `Bearer ${token}`,
//                 'Content-Type': 'application/json'
//             }
//         });
        
//         if (!response.ok) {
//             const error = await response.json();
//             throw new Error(error.detail || 'Ошибка обновления статуса подписки');
//         }
        
//         return await response.json();
//     } catch (error) {
//         console.error('Ошибка обновления статуса подписки:', error);
//         throw error;
//     }
// }

// // Переключения подписки на пользователя
// export async function toggleUserSubscription(
//     token: string, 
//     userId: number
// ): Promise<{ is_subscribed: boolean; message: string }> {
//     try {
//         // Сначала проверяем текущий статус подписки
//         const checkResponse = await checkUserSubscription(token, userId);
        
//         if (checkResponse.is_subscribed) {
//             // Если подписаны - отписываемся
//             await unsubscribeFromUser(token, userId);
//             return {
//                 is_subscribed: false,
//                 message: 'Отписались от пользователя'
//             };
//         } else {
//             // Если не подписаны - подписываемся
//             await subscribeToUser(token, userId);
//             return {
//                 is_subscribed: true,
//                 message: 'Подписались на пользователя'
//             };
//         }
//     } catch (error) {
//         console.error('Ошибка переключения подписки на пользователя:', error);
//         throw error;
//     }
// }

// // Переключение подписки на вишлист
// export async function toggleWishlistSubscription(
//     token: string, 
//     wishlistId: number
// ): Promise<{ is_subscribed: boolean; message: string }> {
//     try {
//         // Сначала проверяем текущий статус подписки
//         const checkResponse = await checkWishlistSubscription(token, wishlistId);
        
//         if (checkResponse.is_subscribed) {
//             // Если подписаны - отписываемся
//             await unsubscribeFromWishlist(token, wishlistId);
//             return {
//                 is_subscribed: false,
//                 message: 'Отписались от вишлиста'
//             };
//         } else {
//             // Если не подписаны - подписываемся
//             await subscribeToWishlist(token, wishlistId);
//             return {
//                 is_subscribed: true,
//                 message: 'Подписались на вишлист'
//             };
//         }
//     } catch (error) {
//         console.error('Ошибка переключения подписки на вишлист:', error);
//         throw error;
//     }
// }
