<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import Button from '../ui/Button.svelte';
    //import { wishlistsStore } from '../../stores/data.js';
    import { wishesStore, loadWishes, deleteWish, updateWishStatus, removeWishFromAllWishlists } from '../../../types/wishes.ts';
    import { wishlistsStore, loadWishlists } from '../../../types/wishlists.ts';
    import { 
        checkWishlistSubscription,
        subscribeToWishlist,
        unsubscribeFromWishlist
    } from '../../../types/subscription.ts';
    import { 
        addMultipleWishesToWishlist, 
        getWishesFromWishlist, 
        wishWishlistsStore,
        toggleWishPinInWishlist,
        removeWishFromWishlist,
        addWishToWishlist 
    } from '../../../types/wish_wishlist.ts';
    import { 
        makeWishlistTgUrl, 
        makeWishlistShareUrl 
    } from '../../stores/data.js';
    import { deleteFile } from '../../../types/storage3.ts';

    const dispatch = createEventDispatcher();

    const iconGift = '../../../../static/icons/gift3.png';
    const ICON_WARNING = '../../../../static/icons/warning.png';
    const iconPinned = '../../../../static/icons/pinned.svg';
    const iconPinnedOff = '../../../../static/icons/pinned-off.svg';
    export let wishlistId = null; //2009/0_Dass_25.12.2025
    export let isExternalWishlist = false; //является ли вишлист внешним

    export let token;

    let isLoading = false;
    let isSubscribedToWishlist = false; // Состояние подписки на вишлист
    let wishlistOwnerId = null; // ID владельца вишлиста
    let isCurrentUserOwner = false; // Является ли текущий пользователь владельцем

    onMount(async () => {
        console.log(1);
        if (token) {
            await fetchWishes();
        }

        // Если мы в режиме вишлиста, загружаем его желания
        if (wishlistId) {
            console.log(2);
            try {
                const wishesInWishlist = await getWishesFromWishlist(token, wishlistId);
                console.log(wishesInWishlist);
                wishWishlistsStore.set(wishesInWishlist);

                // Проверяем подписку на вишлист (только для внешних вишлистов)
                if (isExternalWishlist && token) {
                    await checkWishlistSubscriptionStatus();
                }
                
                // Загружаем информацию о владельце вишлиста
                await loadWishlistOwnerInfo();
            } catch (error) {
                console.error('Ошибка загрузки желаний вишлиста:', error);
            }
        }
    });

    let wishlistOwnerData = null;
    let wishlistOwnerName = '';
    let wishlistOwnerAvatar = '';

    // Функция загрузки информации о владельце вишлиста
    async function loadWishlistOwnerInfo() {
        if (!token || !wishlistId) return;
        
        try {
            // Здесь нужно загрузить информацию о вишлисте, включая owner_id
            const response = await fetch(`/api/v1/wishlists/${wishlistId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                wishlistOwnerId = data.owner_id;
                wishlistOwnerName = data.owner_name || '';
                wishlistOwnerAvatar = data.owner_photo || '';
                console.log('loadWishlistOwnerInfo - wishlistOwnerId:', wishlistOwnerId);

                currentWishlist = {
                    ...data,
                    title: data.name,
                    photo: data.photo,
                    description: data.description,
                    privacy: data.typeprivacy,
                    count: data.wishes_count || 0
                };
                console.log(currentWishlist);
                console.log('currentWishlist.privacy:', currentWishlist.privacy);
                console.log('privacy type:', typeof currentWishlist.privacy);
                if (currentWishlist.privacy !== 'private')
                {
                    console.log('not privacy');
                }
                
                // Проверяем, является ли текущий пользователь владельцем
                // Для этого нужно получить ID текущего пользователя
                const userResponse = await fetch('/api/v1/users/me', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                if (userResponse.ok) {
                    const userData = await userResponse.json();
                    const currentUserId = userData.id.toString();
                    isCurrentUserOwner = userData.id.toString() === wishlistOwnerId?.toString();
                    console.log('loadWishlistOwnerInfo - isCurrentUserOwner check:', {
                        currentUserId,
                        wishlistOwnerId,
                        result: isCurrentUserOwner
                    });
                }
            }
        } catch (error) {
            console.error('Ошибка загрузки информации о владельце вишлиста:', error);
        }
    }

    let isCurrentWishOwner = false;

    const checkWishOwnership = async (wishId) => {
        if (!token || !wishId) return false;
        
        try {
            // Загружаем информацию о желании
            const wishResponse = await fetch(`/api/v1/wishes/${wishId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (wishResponse.ok) {
                const wishData = await wishResponse.json();
                
                // Получаем ID текущего пользователя
                const userResponse = await fetch('/api/v1/users/me', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (userResponse.ok) {
                    const userData = await userResponse.json();
                    console.log('checkWishOwnership - userData:', userData);
                    const currentUserId = userData.id.toString();
                    const wishOwnerId = wishData.user_id.toString();
                    
                    isCurrentWishOwner = currentUserId === wishOwnerId;
                    console.log('checkWishOwnership:', {
                        currentUserId,
                        wishOwnerId,
                        isCurrentWishOwner
                    });
                    
                    return isCurrentWishOwner;
                }
            }
        } catch (error) {
            console.error('Ошибка проверки владельца желания:', error);
        }
        
        return false;
    };

    // Функция проверки подписки на вишлист
    async function checkWishlistSubscriptionStatus() {
        if (!token || !wishlistId) return;
        
        try {
            isSubscribedToWishlist = await checkWishlistSubscription(token, parseInt(wishlistId));
        } catch (error) {
            console.error('Ошибка проверки подписки на вишлист:', error);
        }
    }

    // Функция подписки/отписки от вишлиста
    async function toggleWishlistSubscription() {
        if (!token || !wishlistId || isLoading) return;
        
        isLoading = true;
        try {
            if (isSubscribedToWishlist) {
                // Отписаться от вишлиста
                await unsubscribeFromWishlist(token, parseInt(wishlistId));
                isSubscribedToWishlist = false;
            } else {
                // Подписаться на вишлист
                await subscribeToWishlist(token, parseInt(wishlistId));
                isSubscribedToWishlist = true;
            }
        } catch (error) {
            console.error('Ошибка подписки/отписки от вишлиста:', error);
            showNotification(error.message || 'Произошла ошибка');
        } finally {
            isLoading = false;
        }
    }

    async function fetchWishes() {
        if (!token) {
            console.error('Токен отсутствует');
            return;
        }

        try {
            await loadWishes(token);
        } catch (err) {
            console.error('Ошибка загрузки желаний:', err);
        }
    }

    const formatPrice = (wish) => {
        if (wish.price == null || wish.price === '') return '';
        
        let currencySymbol = wish.currency || '';
        if (currencySymbol === 'RUB') currencySymbol = '₽';
        if (currencySymbol === 'BYN') currencySymbol = 'Br';
        if (currencySymbol === 'USD') currencySymbol = '$';
        if (currencySymbol === 'EUR') currencySymbol = '€';
        if (currencySymbol === 'UAH') currencySymbol = '₴';
        if (currencySymbol === 'KZT') currencySymbol = '₸';
        
        return `${wish.price} ${currencySymbol}`;
    };

    let selectedWish = null;
    let showDetailModal = false;

    // Открыть модальное окно с детальной информацией
    const openDetailModal = async (wish) => {
        console.log('openDetailModal - входные данные:', {
            wish,
            wishlistId,
            isExternalWishlist,
            isCurrentUserOwner
        });
        await loadWishDetails(wish.id);
    };

    // Закрыть модальное окно
    const closeDetailModal = () => {
        showDetailModal = false;
        selectedWish = null;
    };

    $: pinnedWishesCount = wishlistId 
        ? $wishWishlistsStore.filter(wish => wish.is_pinned).length
        : 0;

    // Получить названия вишлистов по их ID
    const getWishlistNames = (wishlistIds) => {
        if (!wishlistIds || wishlistIds.length === 0) return [];
        
        return wishlistIds
            .map(id => {
                const wishlist = $wishlistsStore.find(wl => wl.id === id);
                return wishlist ? wishlist.name : null;
            })
            .filter(name => name !== null);
    };

    // Обработчик клика по ссылке (открывает в новой вкладке)
    const openLink = (url, event) => {
        if (event) event.stopPropagation();
        if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
            window.open(url, '_blank', 'noopener,noreferrer');
        }
    };

    // Заглушки для кнопок создания, редактирования и удаления желания
    export let onNavigateToCreateWishes; //2005_Dass_20.12.2025
    const openForm = () => {
        console.log('Создание нового желания');
        // TODO: Реализовать создание
        onNavigateToCreateWishes(); //2005_Dass_20.12.2025
    };
    
    const handleEdit = () => {
        console.log('Редактирование желания:', selectedWish.id);
        // TODO: Реализовать редактирование
        dispatch('openEditWishes', { id: selectedWish.id }) //2006_2_Dass_24.12.2025
    };

    const handleDelete = () => {
        console.log('Удаление желания:', selectedWish.id);
        //2006_3_Dass_25.12.2025
        if (!selectedWish) return;
        //2006_7_Dass_25.12.2025
        showFullDeleteModal = true;
    };

    // Функция для переключения закрепления желания
    const togglePinWish = async (wishId, connectionId, currentPinnedState, currentOrderPosition) => {
        if (!token || !connectionId) return;

        if (!currentPinnedState && pinnedWishesCount >= 5) {
            showNotification('В этом вишлисте можно закрепить не более 5 желаний');
            return;
        }
        
        try {
            const newPinnedState = !currentPinnedState;
            await toggleWishPinInWishlist(token, connectionId, newPinnedState, currentOrderPosition || 0);
            
            // Обновляем локальное состояние
            wishWishlistsStore.update(items => 
                items.map(item => 
                    item.connection_id === connectionId 
                        ? { ...item, is_pinned: newPinnedState }
                        : item
                )
            );
            
            // Обновляем также в основном списке желаний, если нужно
            if (wishlistId) {
                await updateWishesInWishlist();
            }
            
        } catch (error) {
            console.error('Ошибка при переключении закрепления:', error);
        }
    };

    let showNotificationFlag = false;
    let notificationMessage = '';
    
    const showNotification = (message) => {
        notificationMessage = message;
        showNotificationFlag = true;
        
        // Автоматически скрываем уведомление через 3 секунды
        setTimeout(() => {
            showNotificationFlag = false;
        }, 3000);
    };

    // открытие вишлиста 2009/0_Dass_25.12.2025
    $: filteredWishes = wishlistId 
        ? $wishWishlistsStore.map(item => ({
            id: item.id.toString(),
            name: item.name,
            photo: item.photo,
            price: item.price,
            currency: item.currency,
            description: item.description,
            url_gift: item.url_gift,
            wishlistIds: [wishlistId],
            connection_id: item.connection_id,
            is_pinned: item.is_pinned || false
        }))
    : $wishesStore.map(wish => ({
        ...wish,
        is_pinned: false,
        connection_id: null
    }));

    $: sortedFilteredWishes = wishlistId 
    ? [...$wishWishlistsStore]
        .sort((a, b) => {
            // Сначала закрепленные, потом обычные
            if (a.is_pinned && !b.is_pinned) return -1;
            if (!a.is_pinned && b.is_pinned) return 1;
            // Затем по order_position
            return (a.order_position || 0) - (b.order_position || 0);
        })
        .map(item => ({
            id: item.id,
            name: item.name,
            photo: item.photo,
            price: item.price,
            currency: item.currency,
            description: item.description,
            url_gift: item.url_gift,
            wishlistIds: [wishlistId],
            connection_id: item.connection_id,
            is_pinned: item.is_pinned || false,
            order_position: item.order_position || 0
        }))
        : $wishesStore.map(wish => ({
            ...wish,
            is_pinned: false,
            connection_id: null,
            order_position: 0
        }));

    $: currentWishlist = wishlistId 
        ? $wishlistsStore.find(wl => wl.id === wishlistId)
        : null;

    // 2009_1_Dass_25.12.2025 -->
    let showAddExistingModal = false;
    let selectedWishesForAdding = new Set();
    const openAddExistingModal = async () => {
        if (!token || !wishlistId) {
            console.error('Токен или ID вишлиста отсутствует');
            return;
        }

        selectedWishesForAdding = new Set();

        try {
            await loadAvailableWishes();
            showAddExistingModal = true;
        } catch (error) {
            console.error('Ошибка загрузки доступных желаний:', error);
        }
    };
    const addSelectedWishesToWishlist = async () => {
        // if (!wishlistId) return;
        
        // $wishesStore = $wishesStore.map(wish => {
        //     if (selectedWishesForAdding.has(wish.id)) {
        //         const existingWishlistIds = wish.wishlistIds || [];
        //         if (!existingWishlistIds.includes(wishlistId)) {
        //             return {
        //                 ...wish,
        //                 wishlistIds: [...existingWishlistIds, wishlistId]
        //             };
        //         }
        //     }
        //     return wish;
        // });
            
        // // Закрываем модальное окно
        // showAddExistingModal = false;
        // selectedWishesForAdding.clear();
        if (!wishlistId || !token) return;
        
        try {
            // Конвертируем Set в массив ID
            const wishIds = Array.from(selectedWishesForAdding);
            
            // Используем метод из wish_wishlist.ts для массового добавления
            await addMultipleWishesToWishlist(token, wishlistId, wishIds);
            
            // После успешного добавления обновляем данные
            await updateWishesInWishlist();
            
            // Закрываем модальное окно
            showAddExistingModal = false;
            selectedWishesForAdding.clear();
            
        } catch (error) {
            console.error('Ошибка добавления желаний в вишлист:', error);
        }
    };

    const updateWishesInWishlist = async () => {
        if (!wishlistId || !token) return;
        
        try {
            // Загружаем обновленный список желаний из вишлиста
            const wishesInWishlist = await getWishesFromWishlist(token, wishlistId);
            
            // Обновляем локальный store
            wishWishlistsStore.set(wishesInWishlist);
            
        } catch (error) {
            console.error('Ошибка обновления списка желаний:', error);
        }
    };

    // Функция для загрузки доступных желаний
    const loadAvailableWishes = async () => {
        if (!token || !wishlistId) return;
        
        try {
            // Загружаем все желания пользователя
            await loadWishes(token);
            
            // Загружаем желания, которые уже в вишлисте
            const wishesInWishlist = await getWishesFromWishlist(token, wishlistId);
            wishWishlistsStore.set(wishesInWishlist);
            
        } catch (error) {
            console.error('Ошибка загрузки доступных желаний:', error);
            throw error;
        }
    };
    
    // Функция для получения ID желаний, которые уже в вишлисте
    const getWishIdsInCurrentWishlist = () => {
        return $wishWishlistsStore.map(item => item.id);
    };
    
    $: availableWishes = $wishesStore.filter(wish => {
        // !wish.wishlistIds?.includes(wishlistId)
        // Проверяем, нет ли этого желания в текущем вишлисте
        const wishIdsInWishlist = getWishIdsInCurrentWishlist();
        return !wishIdsInWishlist.includes(wish.id);
    });
    // 2009_1_Dass_25.12.2025 <--

    // 2009_2_Dass_25.12.2025 -->
    const handleRemoveFromWishlist = (wishId) => {
        if (!wishlistId) return;
        //2006_7_Dass_25.12.2025
        const wish = $wishWishlistsStore.find(item => item.id === wishId.toString());
    
        if (wish) {
            selectedWish = {
                id: wish.id,
                name: wish.name,
                connection_id: wish.connection_id
            };
            showFromWishlistDeleteModal = true;
        }
    };
    // 2009_2_Dass_25.12.2025 <--

    // 2009_3_Dass_25.12.2025 -->
    let showCopyMoveModal = false;
    let actionType = 'copy'; // 'copy' или 'move'
    let targetWishlists = new Set(); // Выбранные вишлисты для копирования/перемещения
    let wishToCopyMove = null;

    const openCopyMoveModal = async (wishId, type) => {
        wishToCopyMove = wishId;
        actionType = type;
        targetWishlists = new Set();
        try {
            // Загружаем вишлисты
            await loadWishlists(token);
            
            // Загружаем информацию о желании для получения списка вишлистов, где оно уже есть
            await loadWishDetails(wishId);
            
            showCopyMoveModal = true;
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
            showNotification('Не удалось загрузить данные');
        }
    };
    //выполнить перемещение/копирование
    const executeCopyMove = async () => {
        if (!wishToCopyMove || targetWishlists.size === 0) return;
        
        try {
            const targetWishlistIds = Array.from(targetWishlists);
            console.log(targetWishlists);
            console.log(targetWishlistIds);
            for (const targetWishlistId of targetWishlistIds) {
                console.log(targetWishlistId);
                if (actionType === 'copy') {
                    await addWishToWishlist(
                        token, 
                        targetWishlistId, 
                        wishToCopyMove, 
                        {
                            is_pinned: false,
                            order_position: 0
                        }
                    );
                } else if (actionType === 'move') {
                    if (wishlistId) {
                        await removeWishFromWishlist(token, wishlistId, wishToCopyMove);
                    }
                    await addWishToWishlist(
                        token, 
                        targetWishlistId, 
                        wishToCopyMove,
                        {
                            is_pinned: false,
                            order_position: 0
                        }
                    );
                }
            }
            
            await loadWishes(token);
        
            await loadWishlists(token);
            
            if (wishlistId) {
                if (actionType === 'move') {
                    wishWishlistsStore.update(items => 
                        items.filter(item => item.id !== wishToCopyMove.toString())
                    );
                }
                // Обновляем список желаний в вишлисте
                await updateWishesInWishlist();
            }
            
            closeCopyMoveModal();
            closeDetailModal();
        } catch (error) {
            console.error('Ошибка при выполнении операции:', error);
            showNotification('Произошла ошибка при выполнении операции');
        }
    };
    const closeCopyMoveModal = () => {
        showCopyMoveModal = false;
        wishToCopyMove = null;
        targetWishlists = new Set();
    };
    //переключить выбор вишлистов
    const toggleWishlistSelection = (wishlistId) => {
        const newSet = new Set(targetWishlists);
        if (newSet.has(wishlistId)) {
            newSet.delete(wishlistId);
        } else {
            newSet.add(wishlistId);
        }
        targetWishlists = newSet;
    };
    // 2009_3_Dass_25.12.2025 <--

    //2006_7_Dass_25.12.2025 -->
    let showFullDeleteModal = false;
    let showFromWishlistDeleteModal = false;  

    const executeFullDelete = async () => {
        if (!selectedWish || !token) return;
    
        try {
            if (selectedWish.photo && selectedWish.photo.includes('selstorage.ru')) {
                try {
                    await deleteFile(selectedWish.photo, token);
                    console.log('Фото желания удалено из S3');
                } catch (s3Error) {
                    console.warn('Не удалось удалить фото из S3:', s3Error);
                }
            }
            
            await deleteWish(token, selectedWish.id);

            await loadWishes(token);
            
            //если в режиме вишлиста
            if (wishlistId) {
                wishWishlistsStore.update(items => 
                    items.filter(item => item.id !== selectedWish.id)
                );
            }
            
            console.log('Желание полностью удалено:', selectedWish.id);
            
            // Закрываем модальные окна
            closeFullDeleteModal();
            closeDetailModal();
            
            // Показываем уведомление об успехе
            showNotification('Желание успешно удалено');
        } catch (error) {
            console.error('Ошибка при удалении желания:', error);
        }
    }

    const executeFromWishlistDelete = async () => {
        if (!selectedWish || !wishlistId) return;
        // Удалить только из текущего вишлиста
        try {
            await removeWishFromWishlist(token, wishlistId, selectedWish.id);

            wishWishlistsStore.update(items => 
                items.filter(item => item.id !== selectedWish.id.toString())
            );
            
            await loadWishes(token);
        
            console.log('Желание удалено из вишлиста:', selectedWish.id);
            // Закрываем модальные окна
            closeFromWishlistDeleteModal();
            closeDetailModal();
        } catch (error) {
            console.error('Ошибка при удалении из вишлиста:', error);
        }
    };

    const closeFullDeleteModal = () => {
        showFullDeleteModal = false;
        selectedWish = null;
    };

    const closeFromWishlistDeleteModal = () => {
        showFromWishlistDeleteModal = false;
        selectedWish = null;
    };
    //2006_7_Dass_25.12.2025 <--

    const loadWishDetails = async (wishId) => {
        console.log('loadWishDetails - начал загрузку для wishId:', wishId);
        console.log('Текущие параметры:', {
            wishlistId,
            isExternalWishlist,
            isCurrentUserOwner
        });
        try {
            const response = await fetch(`/api/v1/wishes/${wishId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('loadWishDetails - полученные данные:', data);

                let connectionInfo = null;
                if (wishlistId) {
                    connectionInfo = $wishWishlistsStore.find(item => 
                        item.id === wishId.toString()
                    );
                }
                
                selectedWish = {
                    id: data.id,
                    name: data.name,
                    photo: data.photo,
                    description: data.description,
                    price: data.price,
                    currency: data.currency,
                    url_gift: data.url_gift,
                    wishlistIds: data.wishlists?.map(w => w.id) || [],
                    wishlists: data.wishlists || [],
                    isBooked: data.is_booked,
                    isFinished: data.status_is_finished,
                    createdAt: data.created_at,
                    updatedAt: data.updated_at,
                    connection_id: connectionInfo?.connection_id || null,
                    is_pinned: connectionInfo?.is_pinned || false,
                    order_position: connectionInfo?.order_position || 0,
                    user_id: data.user_id
                };

                console.log('selectedWish после обработки:', selectedWish);

                // Проверяем владельца желания
                const wishOwnerCheck = await checkWishOwnership(wishId);
                
                console.log('loadWishDetails - ключевые параметры:', {
                    isExternalWishlist,
                    isCurrentUserOwner, // Владелец вишлиста
                    isCurrentWishOwner, // Владелец желания
                    selectedWishId: selectedWish.id,
                    selectedWishIsFinished: selectedWish.isFinished,
                    selectedWishUserId: selectedWish.user_id,
                    // Показывать ли кнопку "Исполнено"? 
                    shouldShowFinishedButton: !isExternalWishlist && wishOwnerCheck
                });
                console.log('selectedWish после обработки:', selectedWish);
                console.log('loadWishDetails - selectedWish после обработки:', selectedWish);
                
                showDetailModal = true;
            }
        } catch (error) {
            console.error('Ошибка загрузки деталей желания:', error);
        }
    };

    const getWishlistIdsWithWishFromDB = () => {
        if (!selectedWish) return [];
        console.log('selectedWish.wishlistIds:', selectedWish.wishlistIds);
        return selectedWish.wishlistIds.map(id => id.toString());
    };
    
    $: availableWishlistsForCopyMove = $wishlistsStore
    .filter(wl => {
        // получаем ID вишлистов, где уже есть желание
        const wishlistIdsWithWish = getWishlistIdsWithWishFromDB();
        const currentWishlistId = wl.id.toString();
        const isAlreadyInWishlist = wishlistIdsWithWish.some(id => 
            id.toString() === currentWishlistId
        );
        
        return !isAlreadyInWishlist;
    });

    const handleShareWishlist = () => {
        if (!wishlistId || !currentWishlist) return;
        
        // Проверяем, можно ли делиться этим вишлистом
        if (currentWishlist.privacy === 'private') {
            // Для приватных вишлистов проверяем, владелец ли это
            if (isExternalWishlist && !isCurrentUserOwner) {
                showNotification('Это приватный вишлист, нельзя поделиться');
                return;
            }
        }
        
        // Используем данные из currentWishlist согласно интерфейсу Wishlist
        const shareData = {
            id: parseInt(wishlistId),
            title: currentWishlist.title || currentWishlist.name || 'Вишлист',
            photo: currentWishlist.photo || '',
            description: currentWishlist.description || '',
            typeprivacy: currentWishlist.privacy || 'private',
            count: currentWishlist.count || filteredWishes.length,
            wishesCount: filteredWishes.length,
            isExternalWishlist: isExternalWishlist || false,
            isCurrentUserOwner: isCurrentUserOwner || false,
            ownerName: wishlistOwnerName || '',
            ownerAvatar: wishlistOwnerAvatar || ''
        };
        
        console.log('Данные для шаринга вишлиста:', shareData);
        dispatch('shareWishlist', shareData);
    };

    const openFinishedWishes = () => {
        console.log('Открытие экрана исполненных желаний');
        dispatch('openFinishedWishes');
    };

    // Функция для пометки желания как исполненного
    const markWishAsFinished = async (wishId) => {
        if (!token || !wishId) return;
        
        try {
            // Обновляем статус желания на Исполнено
            await updateWishStatus(token, wishId, {
                status_is_finished: true
            });
            
            // Удаляем желание из всех вишлистов
            await removeWishFromAllWishlists(token, wishId);
            
            // Обновляем локальные stores
            wishesStore.update(wishes => 
                wishes.map(w => 
                    w.id === wishId 
                        ? { ...w, status_is_finished: true, is_booked: false }
                        : w
                )
            );
            
            // // Если в режиме вишлиста, удаляем из текущего вишлиста
            // if (wishlistId) {
            //     wishWishlistsStore.update(items => 
            //         items.filter(item => item.id !== wishId.toString())
            //     );
            // }
            
            showNotification('Желание отмечено как исполненное');
            
            if (showDetailModal && selectedWish?.id === wishId) {
                closeDetailModal();
            }
            
        } catch (error) {
            console.error('Ошибка при пометке желания как исполненного:', error);
            showNotification('Не удалось отметить желание как исполненное');
        }
    };

    $: {
        if (showDetailModal && selectedWish) {
            console.log('=== MODAL AUTO-DEBUG ===');
            console.log('isExternalWishlist:', isExternalWishlist);
            console.log('isCurrentUserOwner:', isCurrentUserOwner);
            console.log('isCurrentWishOwner:', isCurrentWishOwner);
            console.log('selectedWish.id:', selectedWish?.id);
            console.log('selectedWish.isFinished:', selectedWish?.isFinished);
            console.log('Показывать чекбокс "Исполнено"?', !isExternalWishlist && isCurrentWishOwner);
            console.log('======================');
        }
    }

</script>

<!--2009/0_Dass_25.12.2025-->
{#if wishlistId && currentWishlist}
    <!-- Шапка для режима просмотра вишлиста -->
    <header class="app-header">
        <div style="display: flex; align-items: flex-start; justify-content: space-between; width: 100%;">
            <div style="flex: 1; display: flex; flex-direction: column;">
                <div class="h1" style="margin-bottom: 4px;">{currentWishlist.title}</div>
                
                <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 4px;">
                    <div class="wishlist-subtitle">
                        {filteredWishes.length} {filteredWishes.length === 1 ? 'желание' : 
                        filteredWishes.length >= 2 && filteredWishes.length <= 4 ? 'желания' : 'желаний'}
                    </div>                    
                </div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; margin-left: 12px;">
                {#if currentWishlist.privacy !== 'private'}
                    <button 
                        class="share-button"
                        on:click={handleShareWishlist}
                        aria-label="Поделиться вишлистом"
                        title="Поделиться вишлистом"
                        style="margin-bottom: 8px; padding: 6px;"
                    >
                        <img 
                            src="../../../../static/icons/share.png" 
                            alt="Поделиться" 
                            width="24" 
                            height="24"
                        />
                    </button>
                {:else if !isExternalWishlist || isCurrentUserOwner}
                    <!-- Для приватных вишлистов показываем кнопку только владельцу -->
                    <button 
                        class="share-button"
                        on:click={handleShareWishlist}
                        aria-label="Поделиться вишлистом"
                        title="Поделиться вишлистом"
                        style="margin-bottom: 8px; padding: 6px;"
                    >
                        <img 
                            src="../../../../static/icons/share.png" 
                            alt="Поделиться" 
                            width="24" 
                            height="24"
                        />
                    </button>
                {/if}         
                <!-- {#if !isExternalWishlist}
                    <button 
                        class="finished-button"
                        on:click={openFinishedWishes}
                        aria-label="Показать исполненные желания"
                        style="padding: 6px 12px; font-size: 13px;"
                    >
                        Исполненные
                    </button>
                {/if} -->
            </div>
    </header>
{:else}
    <!-- Стандартная шапка -->
    <header class="app-header">
        <div style="display: flex; align-items: flex-start; justify-content: space-between; width: 100%;">
            <div style="flex: 1;">
                <div class="h1">Все ваши желания</div>
            </div>
            {#if !isExternalWishlist}
                <div style="margin-left: 12px; display: flex; align-items: center;">
                    <button 
                        class="finished-button"
                        on:click={openFinishedWishes}
                        aria-label="Показать исполненные желания"
                    >
                        Исполненные
                    </button>
                </div>
            {/if}
        </div>
    </header>
{/if}

<section class="section-card">
    <!--2009/0_Dass_25.12.2025-->
    {#if sortedFilteredWishes.length === 0}
        <p class="empty-note">
            {#if wishlistId}
                В этом вишлисте пока нет желаний.
            {:else}
                У вас пока нет желаний. Нажмите «Новое желание», чтобы добавить первое.
            {/if}
        </p>
    {:else}
        <div class="wish-grid">
            {#each sortedFilteredWishes as wish (wish.id)}
                <!-- svelte-ignore a11y_no_noninteractive_element_to_interactive_role -->
                <article 
                    class="wish-card" 
                    on:click={() => openDetailModal(wish)}
                    role="button"
                    tabindex="0"
                    on:keydown={(e) => e.key === 'Enter' && openDetailModal(wish)}
                >
                    <div class="wish-card-image">
                        {#if wish.photo}
                            <img src={wish.photo} alt={wish.name} class="wish-image" />
                        {:else}
                            <img src={iconGift} alt="Подарок" class="wish-image placeholder" />
                        {/if}

                        <!-- Иконка закрепления (только в режиме вишлиста) -->
                        {#if wishlistId && wish.connection_id && !isExternalWishlist}
                            <button 
                                class="pin-button {wish.is_pinned ? 'pinned' : ''}"
                                on:click|stopPropagation={() => togglePinWish(wish.id, wish.connection_id, wish.is_pinned, wish.order_position)}
                                aria-label="{wish.is_pinned ? 'Открепить' : 'Закрепить'}"
                                title="{wish.is_pinned ? 'Открепить' : 'Закрепить'}"
                            >
                                <img 
                                    src={wish.is_pinned ? iconPinned : iconPinnedOff} 
                                    alt="{wish.is_pinned ? 'Закреплено' : 'Не закреплено'}"
                                    class="pin-icon"
                                />
                            </button>
                        {/if}
                    </div>

                    <div class="wish-card-body">
                        <div class="wish-title" title={wish.name}>{wish.name}</div>
                        {#if wish.price != null}
                            <div class="wish-price">{formatPrice(wish)}</div>
                        {/if}
                    </div>
                </article>
            {/each}
        </div>
    {/if}
</section>

<!--2009/0_Dass_25.12.2025-->
{#if !wishlistId}
    <div style="padding:0 16px 12px;">
        <Button full on:click={openForm}>+ Новое желание</Button>
    </div>
<!--2009_1_Dass_25.12.2025-->
{:else if wishlistId && !isExternalWishlist}  
    <div style="padding:0 16px 12px;">
        <Button full on:click={openAddExistingModal}>
            + Добавить существующее желание
        </Button>
    </div>
{:else if wishlistId && isExternalWishlist}
    <!-- Если это чужой вишлист - кнопка подписки/отписки -->
    <div style="padding:0 16px 12px;">
        <Button 
            full 
            kind="ghost"
            on:click={toggleWishlistSubscription}
            disabled={isLoading || !wishlistId}
        >
            {#if isLoading}
                <span>Загрузка...</span>
            {:else}
                <img
                    src={isSubscribedToWishlist ? '../../../../static/icons/bell-on.png' : '../../../../static/icons/bell-off.png'}
                    alt=""
                    class="icon-16"
                    loading="lazy"
                    style="margin-right: 8px;"
                />
                <span>{isSubscribedToWishlist ? 'Вы подписаны' : 'Подписаться на вишлист'}</span>
            {/if}
        </Button>
    </div>
{/if}

<!-- Модальное окно детального просмотра -->
{#if showDetailModal && selectedWish}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="detail-backdrop" on:click={closeDetailModal}>
        <div class="detail-panel" on:click|stopPropagation>
            <!-- Кнопка закрытия -->
            <button class="close-button" on:click={closeDetailModal} aria-label="Закрыть">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M18 6L6 18M6 6L18 18" stroke="#6B7280" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
            <h2>Детальное описание желания</h2>
            <div class="detail-content">
                <!-- Добавляем кнопку закрепления в детальном просмотре -->
                {#if wishlistId && selectedWish.connection_id && !isExternalWishlist}
                    <div class="detail-section">
                        <h3>Действия</h3>
                        <div class="detail-actions">
                            <Button 
                                kind="ghost" 
                                on:click={async () => {
                                    if (!selectedWish.connection_id) return;

                                    if (!selectedWish.is_pinned && pinnedWishesCount >= 5) {
                                        showNotification('В этом вишлисте можно закрепить не более 5 желаний');
                                        return;
                                    }
                            
                                    try {
                                        await togglePinWish(
                                            selectedWish.id, 
                                            selectedWish.connection_id, 
                                            selectedWish.is_pinned,
                                            selectedWish.order_position
                                        );
                                        
                                        // Обновляем локальное состояние
                                        selectedWish.is_pinned = !selectedWish.is_pinned;
                                        
                                        // Обновляем wishWishlistsStore
                                        wishWishlistsStore.update(items => 
                                            items.map(item => 
                                                item.connection_id === selectedWish.connection_id
                                                    ? { ...item, is_pinned: selectedWish.is_pinned }
                                                    : item
                                            )
                                        );
                                        
                                    } catch (error) {
                                        console.error('Ошибка при переключении закрепления:', error);
                                    }
                                }}
                            >
                                {#if selectedWish.is_pinned}
                                    <img src={iconPinned} alt="Открепить" class="action-icon" />
                                    Открепить
                                {:else}
                                    <img src={iconPinnedOff} alt="Закрепить" class="action-icon" />
                                    Закрепить
                                {/if}
                            </Button>
                        </div>
                    </div>
                {/if}

                <!-- {#if !isExternalWishlist && isCurrentWishOwner} -->
                    <!-- Секция статуса -->
                    <div class="detail-section">
                        <h3>Статус</h3>
                        
                        {#if !selectedWish.isFinished && !isExternalWishlist}
                            <!-- Кнопка для пометки как исполненного -->
                            <Button 
                                kind="primary" 
                                full
                                on:click={async () => {
                                    if (confirm('Отметить желание как исполненное?\n\nОно будет перемещено в список "Исполненные" и удалено из всех вишлистов.')) {
                                        await markWishAsFinished(selectedWish.id);
                                    }
                                }}
                            >
                                <img 
                                    src="../../../../static/icons/check-circle-filled.png" 
                                    alt="Исполнено" 
                                    class="action-icon"
                                />
                                Отметить как исполненное
                            </Button>
                        {/if}
                    </div>
                <!-- {/if} -->
                
                <!-- Изображение -->
                <div class="detail-image">
                    {#if selectedWish.photo}
                        <img src={selectedWish.photo} alt={selectedWish.name} />
                    {:else}
                        <img src={iconGift} alt="Подарок" class="detail-placeholder" />
                    {/if}
                </div>

                <!-- Название -->
                <h2 class="detail-title">{selectedWish.name}</h2>

                <!-- Цена -->
                {#if selectedWish.price != null}
                    <div class="detail-price">{formatPrice(selectedWish)}</div>
                {/if}

                <!-- Описание -->
                {#if selectedWish.description}
                    <div class="detail-section">
                        <h3>Описание</h3>
                        <p class="detail-description">{selectedWish.description}</p>
                    </div>
                {/if}

                <!-- Ссылка -->
                {#if selectedWish.url_gift}
                    <div class="detail-section">
                        <h3>Ссылка на товар</h3>
                        <a 
                            href={selectedWish.url_gift} 
                            class="detail-link"
                            on:click|stopPropagation={(e) => openLink(selectedWish.url_gift, e)}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            {selectedWish.url_gift}
                        </a>
                    </div>
                {/if}

                <!-- Вишлисты -->
                {#if selectedWish.wishlists && selectedWish.wishlists.length > 0}
                    <div class="detail-section">
                        <h3>Добавлено в вишлисты</h3>
                        <div class="detail-wishlists">
                            {#each selectedWish.wishlists as wishlist}
                                <span class="wishlist-tag">{wishlist.name}</span>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Если нет дополнительной информации -->
                {#if !selectedWish.description && !selectedWish.link && (!selectedWish.wishlistIds || selectedWish.wishlistIds.length === 0)}
                    <p class="detail-no-info">Нет дополнительной информации</p>
                {/if}

                <!-- Кнопки действий -->
                <div class="panel-actions">
                    {#if wishlistId && !isExternalWishlist}
                        <!-- Если мы в режиме вишлиста -->
                        <div style="display: flex; flex-direction: column; gap: 8px; width: 100%;">
                            <div style="display: flex; gap: 12px;">
                                <Button kind="ghost" on:click={() => openCopyMoveModal(selectedWish.id, 'copy')}>
                                    Копировать в
                                </Button>
                                <Button kind="ghost" on:click={() => openCopyMoveModal(selectedWish.id, 'move')}>
                                    Переместить в
                                </Button>
                            </div>
                            <Button kind="danger" on:click={() => handleRemoveFromWishlist(selectedWish.id)} full>
                                Удалить из вишлиста
                            </Button>
                        </div>
                    {:else if !isExternalWishlist}
                        <!-- В обычном режиме показываем стандартные кнопки -->
                        <Button kind="ghost" on:click={handleEdit}>Редактировать</Button>
                        <Button kind="danger" on:click={handleDelete}>Удалить</Button>
                    {/if}
                </div>
            </div>
        </div>
    </div>
{/if}

{#if showNotificationFlag}
    <div class="notification-overlay">
        <div class="notification">
            {notificationMessage}
        </div>
    </div>
{/if}

<!--2009_1_Dass_25.12.2025-->
{#if showAddExistingModal}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="modal-backdrop" on:click={() => showAddExistingModal = false}>
        <div class="modal-content" on:click|stopPropagation>
            <div class="modal-header">
                <h2>Выберите желания для добавления</h2>
                <button class="modal-close" on:click={() => showAddExistingModal = false}>✕</button>
            </div>
            
            <div class="modal-body">
                {#if availableWishes.length === 0}
                    <p class="empty-message">Нет доступных желаний для добавления</p>
                {:else}
                    <div class="wishes-selection-list">
                        {#each availableWishes as wish (wish.id)}
                            <label class="wish-selection-item {selectedWishesForAdding.has(wish.id) ? 'selected' : ''}">
                                <input 
                                    type="checkbox" 
                                    checked={selectedWishesForAdding.has(wish.id)}
                                    on:change={() => {
                                        const newSet = new Set(selectedWishesForAdding);
                                        if (selectedWishesForAdding.has(wish.id)) {
                                            newSet.delete(wish.id);
                                        } else {
                                            newSet.add(wish.id);
                                        }
                                        selectedWishesForAdding = newSet;
                                    }}
                                    style="display: none;"
                                />
                                
                                <div class="selection-checkbox">
                                    {#if selectedWishesForAdding.has(wish.id)}
                                        <div class="checkbox-checked">✓</div>
                                    {:else}
                                        <div class="checkbox-empty"></div>
                                    {/if}
                                </div>
                                
                                <div class="wish-selection-info">
                                    <div class="wish-selection-title">{wish.name}</div>
                                    {#if wish.price != null}
                                        <div class="wish-selection-price">{formatPrice(wish)}</div>
                                    {/if}
                                </div>
                                
                                <div class="wish-selection-image">
                                    {#if wish.photo}
                                        <img src={wish.photo} alt={wish.name} />
                                    {:else}
                                        <img src={iconGift} alt="Подарок" class="placeholder" />
                                    {/if}
                                </div>
                            </label>
                        {/each}
                    </div>
                {/if}
            </div>
            
            <div class="modal-footer">
                <Button 
                    kind="ghost" 
                    on:click={() => showAddExistingModal = false}
                >
                    Отмена
                </Button>
                <Button 
                    on:click={addSelectedWishesToWishlist}
                    disabled={selectedWishesForAdding.size === 0}
                >
                    Добавить выбранные ({selectedWishesForAdding.size})
                </Button>
            </div>
        </div>
    </div>
{/if}

<!--2009_3_Dass_25.12.2025-->
<!-- Модальное окно копирования/перемещения -->
{#if showCopyMoveModal}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="modal-backdrop" on:click={closeCopyMoveModal}>
        <div class="modal-content copy-move-modal" on:click|stopPropagation>
            <div class="modal-header">
                <h2>{actionType === 'copy' ? 'Копировать в' : 'Переместить в'}</h2>
                <button class="modal-close" on:click={closeCopyMoveModal}>✕</button>
            </div>
            
            <div class="modal-body">
                <p class="modal-description">
                    {actionType === 'copy' 
                        ? 'Выберите один или несколько вишлистов, в которые хотите скопировать это желание.'
                        : 'Выберите один или несколько вишлистов, в которые хотите переместить это желание.'}
                    {actionType === 'move' && wishlistId && 
                        ' Текущий вишлист будет удален из списка.'}
                </p>
                
                {#if availableWishlistsForCopyMove.length === 0}
                    <p class="empty-message">
                        Нет доступных вишлистов для {actionType === 'copy' ? 'копирования' : 'перемещения'}
                    </p>
                {:else}
                    <div class="wishlists-selection-list">
                        {#each availableWishlistsForCopyMove as wishlist (wishlist.id)}
                            <div 
                                class="wishlist-selection-item {targetWishlists.has(wishlist.id) ? 'selected' : ''}"
                                on:click={() => toggleWishlistSelection(wishlist.id)}
                            >
                                <div class="selection-checkbox">
                                    {#if targetWishlists.has(wishlist.id)}
                                        <div class="checkbox-checked">✓</div>
                                    {:else}
                                        <div class="checkbox-empty"></div>
                                    {/if}
                                </div>
                                
                                <div class="wishlist-selection-info">
                                    <div class="wishlist-selection-title">{wishlist.title}</div>
                                    <div class="wishlist-selection-count">
                                        {wishlist.count} {wishlist.count === 1 ? 'желание' : 
                                        wishlist.count >= 2 && wishlist.count <= 4 ? 'желания' : 'желаний'}
                                    </div>
                                </div>
                                
                                <div class="wishlist-selection-cover">
                                    {#if wishlist.rUrl}
                                        <img src={wishlist.rUrl} alt={wishlist.title} />
                                    {:else}
                                        <img src={iconGift} alt="Вишлист" class="placeholder" />
                                    {/if}
                                </div>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
            
            <div class="modal-footer">
                <Button 
                    kind="ghost" 
                    on:click={closeCopyMoveModal}
                >
                    Отмена
                </Button>
                <Button 
                    on:click={executeCopyMove}
                    disabled={targetWishlists.size === 0}
                >
                    {actionType === 'copy' ? 'Копировать' : 'Переместить'} 
                    {targetWishlists.size > 0 && ` (${targetWishlists.size})`}
                </Button>
            </div>
        </div>
    </div>
{/if}

<!--2006_7_Dass_25.12.2025-->
<!-- Модальное окно для полного удаления (из общего списка) -->
{#if showFullDeleteModal && selectedWish}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="modal-backdrop" on:click={closeFullDeleteModal}>
        <div class="confirm-delete-modal" on:click|stopPropagation>
            <div class="confirm-icon">
                <img src={ICON_WARNING} alt="Внимание" class="warning-icon" />
            </div>
            
            <h2 class="confirm-title">Удалить желание полностью?</h2>
            
            <p class="confirm-message">
                Вы собираетесь удалить желание "<strong>{selectedWish.name}</strong>".
                Оно будет удалено из всех вишлистов и списка желаний.
            </p>
            
            <div class="confirm-actions">
                <Button 
                    kind="ghost" 
                    on:click={closeFullDeleteModal}
                    style="flex: 1;"
                >
                    Отмена
                </Button>
                <Button 
                    kind="danger" 
                    on:click={executeFullDelete}
                    style="flex: 1;"
                >
                    Удалить полностью
                </Button>
            </div>
        </div>
    </div>
{/if}

<!-- Модальное окно для удаления из вишлиста -->
{#if showFromWishlistDeleteModal && selectedWish}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="modal-backdrop" on:click={closeFromWishlistDeleteModal}>
        <div class="confirm-delete-modal" on:click|stopPropagation>
            <div class="confirm-icon">
                <img src={ICON_WARNING} alt="Внимание" class="warning-icon" />
            </div>
            
            <h2 class="confirm-title">Удалить из вишлиста?</h2>
            
            <p class="confirm-message">
                Вы хотите удалить "<strong>{selectedWish.name}</strong>" только из этого вишлиста.
            </p>
            
            <div class="confirm-actions">
                <Button 
                    kind="ghost" 
                    on:click={closeFromWishlistDeleteModal}
                    style="flex: 1;"
                >
                    Отмена
                </Button>
                <Button 
                    kind="danger" 
                    on:click={executeFromWishlistDelete}
                    style="flex: 1;"
                >
                    Удалить из вишлиста
                </Button>
            </div>
        </div>
    </div>
{/if}

<style>

    .wish-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(214px, 1fr));
        gap: 16px;
        padding: 0 16px;
        justify-content: center;
        justify-items: center;
    }

    .wish-card {
        width: 214px;
        height: 277px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        flex-shrink: 0;
    }

    .wish-card-image {
        position: relative;
        width: 214px;
        height: 214px;
        background: #f9fafb;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        flex-shrink: 0;
    }

    /* Иконка закрепления */
    .pin-button {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 32px;
        height: 32px;
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid #e5e7eb;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
        z-index: 2;
        padding: 0;
    }

    .pin-button:hover {
        background: white;
        border-color: #3b82f6;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transform: scale(1.05);
    }

    .pin-button.pinned {
        background: #3b82f6;
        border-color: #3b82f6;
    }

    .pin-button.pinned:hover {
        background: #2563eb;
        border-color: #2563eb;
    }

    .pin-icon {
        width: 18px;
        height: 18px;
        transition: all 0.2s ease;
    }

    .pin-button .pin-icon {
        filter: brightness(0.6);
    }

    .pin-button.pinned .pin-icon {
        filter: brightness(1) invert(1);
    }

    .action-icon {
        width: 16px;
        height: 16px;
        margin-right: 8px;
        vertical-align: middle;
    }

    .wish-image {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Масштабирование и обрезка по центру */
        display: block;
    }

    .wish-image.placeholder {
        object-fit: contain; /* Для иконки-заглушки - показываем полностью */
        width: 80px;
        height: 80px;
        opacity: 0.7;
    }

    .wish-card-body {
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 4px;
        flex: 1;
        min-height: 63px; /* 277 - 214 = 63px */
        box-sizing: border-box;
    }

    .wish-title {
        font-size: 14px;
        font-weight: 500;
        color: #111827;
        width: 190px; /* 214px - padding (12px * 2) = 190px */
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.3;
        flex-shrink: 0;
    }

    .wish-price {
        font-size: 15px;
        font-weight: 600;
        color: #1f2937;
        margin-top: 2px;
        flex-shrink: 0;
    }

    .empty-note {
        text-align: center;
        padding: 40px 16px;
        color: #6b7280;
        font-size: 16px;
    }

    /* Стили для модального окна "Детальный просмотр желания" */
    .detail-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 20px;
        animation: fadeIn 0.2s ease-out;
    }

    .detail-panel {
        width: 100%;
        max-width: 500px;
        background: white;
        border-radius: 24px;
        padding: 24px;
        position: relative;
        max-height: 90vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.3s ease-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .panel-actions {
        margin-top: 24px;
        display: flex;
        justify-content: flex-end;
        gap: 12px;
        padding-top: 16px;
        border-top: 1px solid #e5e7eb;
    }
    
    .detail-image {
        width: 100%;
        height: 250px;
        background: #f9fafb;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .detail-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .detail-image .detail-placeholder {
        width: 100px;
        height: 100px;
        object-fit: contain;
        opacity: 0.7;
    }

    .detail-title {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
        margin: 0 0 8px 0;
        line-height: 1.3;
    }

    .detail-price {
        font-size: 16px;
        font-weight: 700;
        color: #059669;
        margin-bottom: 16px;
    }

    .detail-section {
        margin-bottom: 16px;
    }

    .detail-description {
        font-size: 14px;
        line-height: 1.5;
        color: #4b5563;
        margin: 0;
        white-space: pre-wrap;
    }

    .detail-link {
        display: inline-block;
        font-size: 14px;
        color: #3b82f6;
        text-decoration: none;
        word-break: break-all;
        padding: 8px 12px;
        background: #eff6ff;
        border-radius: 8px;
        border: 1px solid #dbeafe;
        transition: background-color 0.2s;
    }

    .detail-link:hover {
        background: #dbeafe;
        text-decoration: underline;
    }

    .detail-wishlists {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .wishlist-tag {
        padding: 6px 12px;
        background: #f3f4f6;
        border-radius: 20px;
        font-size: 12px;
        color: #374151;
        border: 1px solid #e5e7eb;
    }

    .detail-no-info {
        text-align: center;
        color: #6b7280;
        font-style: italic;
        padding: 20px 0;
        font-size: 14px;
    }

    .close-button {
        position: absolute;
        top: 16px;
        right: 16px;
        width: 40px;
        height: 40px;
        border: none;
        background: transparent;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: background-color 0.2s;
        z-index: 10;
    }
    /*Стили для модального окна добавления желаний */
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1001; /* Выше чем detail-backdrop */
        padding: 20px;
    }

    .modal-content {
        width: 100%;
        max-width: 500px;
        background: white;
        border-radius: 24px;
        max-height: 80vh;
        display: flex;
        flex-direction: column;
    }

    .modal-header {
        padding: 24px 24px 16px;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .modal-header h2 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
    }

    .modal-close {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #6b7280;
        padding: 4px;
        line-height: 1;
    }

    .modal-body {
        flex: 1;
        overflow-y: auto;
        padding: 16px 24px;
    }

    .empty-message {
        text-align: center;
        color: #6b7280;
        padding: 40px 0;
    }

    .wishes-selection-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .wish-selection-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .wish-selection-item:hover {
        background: #f9fafb;
        border-color: #d1d5db;
    }

    .wish-selection-item.selected {
        background: #eff6ff;
        border-color: #3b82f6;
    }

    .selection-checkbox {
        width: 24px;
        height: 24px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .checkbox-empty {
        width: 20px;
        height: 20px;
        border: 2px solid #d1d5db;
        border-radius: 6px;
    }

    .checkbox-checked {
        width: 20px;
        height: 20px;
        background: #3b82f6;
        color: white;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: bold;
    }

    .checkbox-empty {
        width: 20px;
        height: 20px;
        border: 2px solid #d1d5db;
        border-radius: 6px;
        background: white;
    }

    .wish-selection-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;
        position: relative;
    }

    .wish-selection-info {
        flex: 1;
        min-width: 0;
    }

    .wish-selection-title {
        font-size: 14px;
        font-weight: 500;
        color: #111827;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 4px;
    }

    .wish-selection-price {
        font-size: 13px;
        color: #059669;
        font-weight: 500;
    }

    .wish-selection-image {
        width: 50px;
        height: 50px;
        flex-shrink: 0;
        border-radius: 8px;
        overflow: hidden;
        background: #f9fafb;
    }

    .wish-selection-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .wish-selection-image .placeholder {
        object-fit: contain;
        width: 30px;
        height: 30px;
        margin: 10px;
        opacity: 0.7;
    }

    .modal-footer {
        padding: 16px 24px 24px;
        border-top: 1px solid #e5e7eb;
        display: flex;
        justify-content: flex-end;
        gap: 12px;
    }
    .wishlist-subtitle
    {
        text-align: right;
        font-size: 12px;
        color: var(--tg-theme-hint-color, #8e8e93);
        margin-top: 4px;
    }  
    .copy-move-modal {
        max-width: 500px;
    }

    .modal-description {
        font-size: 14px;
        color: #6b7280;
        line-height: 1.5;
        margin: 0 0 20px 0;
        padding: 0 4px;
    }

    .wishlists-selection-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .wishlist-selection-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .wishlist-selection-item:hover {
        background: #f9fafb;
        border-color: #d1d5db;
    }

    .wishlist-selection-item.selected {
        background: #eff6ff;
        border-color: #3b82f6;
    }

    .wishlist-selection-info {
        flex: 1;
        min-width: 0;
    }

    .wishlist-selection-title {
        font-size: 14px;
        font-weight: 500;
        color: #111827;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .wishlist-selection-count {
        font-size: 12px;
        color: #6b7280;
    }

    .wishlist-selection-cover {
        width: 50px;
        height: 50px;
        flex-shrink: 0;
        border-radius: 8px;
        overflow: hidden;
        background: #f9fafb;
    }

    .wishlist-selection-cover img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .wishlist-selection-cover .placeholder {
        object-fit: contain;
        width: 30px;
        height: 30px;
        margin: 10px;
        opacity: 0.7;
    }
    /* Общие стили для обоих модальных окон удаления */
    .confirm-delete-modal {
        width: 90%;
        max-width: 400px;
        background: white;
        border-radius: 24px;
        padding: 32px 24px 24px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }

    .confirm-delete-modal .confirm-icon {
        margin: 0 auto 20px;
        width: 64px;
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #EF4444;
    }

    .confirm-delete-modal .confirm-title {
        font-size: 20px;
        font-weight: 600;
        color: #111827;
        margin: 0 0 16px 0;
    }

    .confirm-delete-modal .confirm-message {
        font-size: 14px;
        line-height: 1.5;
        color: #6B7280;
        margin: 0 0 20px 0;
        padding: 0 4px;
    }

    .confirm-delete-modal .confirm-message strong {
        color: #111827;
        font-weight: 600;
    }

    .confirm-delete-modal .confirm-actions {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin: 0 auto;
        max-width: 300px;
    }

    .notification-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 2000;
        display: flex;
        justify-content: center;
        padding: 20px;
        pointer-events: none;
        animation: slideDown 0.3s ease-out;
    }
    
    .notification {
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 12px 20px;
        border-radius: 12px;
        font-size: 14px;
        text-align: center;
        max-width: 400px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        animation: fadeIn 0.3s ease-out;
    }

    .icon-16 {
        width: 16px;
        height: 16px;
        vertical-align: middle;
    }
    
    @keyframes slideDown {
        from {
            transform: translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Для кнопки поделиться в шапке */
    .app-header {
        position: relative;
    }

    .app-header .h1 {
        flex: 1;
    }

    .share-button {
        background: none;
        border: none;
        padding: 8px;
        margin: -8px;
        cursor: pointer;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background-color 0.2s;
    }

    .share-button:hover {
        background-color: #f3f4f6;
    }

    .share-button:active {
        background-color: #e5e7eb;
    }

    /* Исполненные */
    .finished-button {
        background: none;
        border: none;
        color: var(--tg-theme-link-color, #2563eb);
        font-size: 14px;
        font-weight: 500;
        padding: 8px 12px;
        margin-left: 12px;
        cursor: pointer;
        border-radius: 8px;
        transition: background-color 0.2s;
    }

    .finished-button:hover {
        background-color: #f3f4f6;
    }

    .finished-button:active {
        background-color: #e5e7eb;
    }


</style>

