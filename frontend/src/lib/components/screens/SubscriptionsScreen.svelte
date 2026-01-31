<script>
    import Avatar from '../ui/Avatar.svelte';
    import TextField from '../ui/TextField.svelte';
    import { subscriptionsStore } from '../../stores/data.js';
    import { 
        getMySubscriptions, 
        unsubscribeFromUser, 
        unsubscribeFromWishlist,
        SubscriptionItem,
        SubscriptionsResponse
    } from '../../../types/subscription.js';
    
    import { onMount } from 'svelte';

    // Lyse Modifications

    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();


    // Иконки
    const ICON_WISHLIST = '../../../../static/icons/maingift.svg';
    const ICON_ARROW = '../../../../static/icons/arrow-right.png';

    let searchQuery = '';
    let sortBy = 'default'; // 'default', 'users', 'wishlists', 'birth_date_asc', 'birth_date_desc'
    let isLoading = true;
    let errorMessage = '';

    // Фильтрация подписок по поисковому запросу
    $: sortedSubscriptions = (() => {
        let result = $subscriptionsStore;
        const query = searchQuery.trim().toLowerCase();

        if (query) {
            result = result.filter(item => {
                if (item.type_sub) {
                    // Подписка на пользователя
                    const userName = item.user?.name?.toLowerCase() || '';
                    return userName.includes(query);
                } else {
                    // Подписка на вишлист
                    const wishlistName = item.wishlist?.name?.toLowerCase() || '';
                    const wishlistOwner = item.wishlist?.user_name?.toLowerCase() || '';
                    return wishlistName.includes(query) || wishlistOwner.includes(query);
                }
            });
        }

        return sortSubscriptions(result, sortBy);
    })();


    onMount(async () => {
        await loadSubscriptions();
    });

    async function loadSubscriptions() {
        try {
            isLoading = true;
            errorMessage = '';
            const token = getToken();
            
            if (!token) {
                errorMessage = 'Пользователь не авторизован';
                return;
            }
            
            await getMySubscriptions(token, 100);
        } catch (error) {
            errorMessage = error.message || 'Не удалось загрузить подписки';
            console.error('Ошибка загрузки подписок:', error);
        } finally {
            isLoading = false;
        }
    }
    
    function getToken() {
        const tokenFromStorage = localStorage.getItem('token') || 
                                localStorage.getItem('authToken') || 
                                sessionStorage.getItem('token');
        return tokenFromStorage || '';
    }

    const getFilteredAndSortedSubscriptions = (subscriptions) => {
        let result = [...subscriptions];
        const query = searchQuery.trim().toLowerCase();
        
        // Фильтрация по поиску
        if (query) {
            result = result.filter(item => {
                if (item.type === 'user') {
                    const userName = item.name.toLowerCase();
                    return userName.includes(query);
                } else {
                    const wishlistName = item.name.toLowerCase();
                    const wishlistOwner = item.owner_name.toLowerCase();
                    return wishlistName.includes(query) || wishlistOwner.includes(query);
                }
            });
        }
        
        // Сортировка
        return sortSubscriptions(result, sortBy);
    };

    // Функция сортировки
    const sortSubscriptions = (subscriptions, sortType) => {
        let result = [...subscriptions];
        
        switch (sortType) {
            case 'users':
                // Только пользователи
                return result.filter(item => item.type === 'user');
                
            case 'wishlists':
                // Только вишлисты
                return result.filter(item => item.type === 'wishlist');
                
            case 'birth_date_asc':
                // Сначала сортируем пользователей по дате рождения по возрастанию
                const usersAsc = result
                    .filter(item => item.type === 'user')
                    .sort((a, b) => {
                        const dateA = parseBirthDate(a.birth_date);
                        const dateB = parseBirthDate(b.birth_date);
                        
                        // Если нет даты, идет в конец
                        if (!dateA && !dateB) return 0;
                        if (!dateA) return 1;
                        if (!dateB) return -1;
                        
                        return dateA - dateB; // Старшие сначала
                    });
                
                // Вишлисты идут после пользователей (без сортировки)
                const wishlists = result.filter(item => item.type === 'wishlist');
                
                return [...usersAsc, ...wishlists];
                
            case 'birth_date_desc':
                // Сначала сортируем пользователей по дате рождения по убыванию
                const usersDesc = result
                    .filter(item => item.type === 'user')
                    .sort((a, b) => {
                        const dateA = parseBirthDate(a.birth_date);
                        const dateB = parseBirthDate(b.birth_date);
                        
                        // Если нет даты, идет в конец
                        if (!dateA && !dateB) return 0;
                        if (!dateA) return 1;
                        if (!dateB) return -1;
                        
                        return dateB - dateA; // Младшие сначала
                    });
                
                // Вишлисты идут после пользователей (без сортировки)
                const wishlistsDesc = result.filter(item => item.type === 'wishlist');
                
                return [...usersDesc, ...wishlistsDesc];
                
            default:
                // 'default' - выводятся пользователи и вишлисты без упорядочивания
                return result;
        }
    };

    // Функция для парсинга даты рождения из формата "DD.MM.YYYY"
    const parseBirthDate = (dateStr) => {
        if (!dateStr) return null;
        
        const parts = dateStr.split('.');
        if (parts.length !== 3) return null;
        
        const [day, month, year] = parts.map(Number);
        if (isNaN(day) || isNaN(month) || isNaN(year)) return null;
        
        return new Date(year, month - 1, day);
    };

    // Обработчик отписки
    const handleUnsubscribe = async (subscription, event) => {
        if (event) event.stopPropagation();

        const token = getToken();
        if (!token) {
            alert('Ошибка авторизации. Пожалуйста, войдите в систему.');
            return;
        }
        
        const confirmMessage = subscription.type === 'user' 
            ? `Вы уверены, что хотите отписаться от пользователя ${subscription.name}?`
            : `Вы уверены, что хотите отписаться от вишлиста "${subscription.name}"?`;
        
        if (!confirm(confirmMessage)) return;
        
        try {
            if (subscription.type === 'user') {
                await unsubscribeFromUser(token, subscription.user_id);
            } else {
                await unsubscribeFromWishlist(token, subscription.wishlist_id);
            }
            
            // Перезагружаем список подписок
            await loadSubscriptions();
        } catch (error) {
            alert(error.message || 'Ошибка отписки');
            console.error('Ошибка отписки:', error);
        }
    };

    // Обработчик открытия профиля/вишлиста
    const handleOpenItem = (subscription) => {
        if (subscription.type === 'user') {
            dispatch('open-profile', { profileId: subscription.user_id });
        } else {
            // Для вишлиста
            dispatch('open-wishlist', { wishlistId: subscription.wishlist_id });
        }
    };

    // Получение инициалов для аватара
    const getInitials = (name) => {
        if (!name) return '??';
        const parts = name.trim().split(' ');
        return parts.slice(0, 2).map(p => p[0]).join('').toUpperCase();
    };

    // Получение слова "желание" в правильной форме
    const getWishesWord = (count) => {
        if (count === 0) return 'желаний';
        
        const lastDigit = count % 10;
        const lastTwoDigits = count % 100;
        
        if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
            return 'желаний';
        }
        
        if (lastDigit === 1) {
            return 'желание';
        } else if (lastDigit >= 2 && lastDigit <= 4) {
            return 'желания';
        } else {
            return 'желаний';
        }
    };
</script>

<header class="app-header">
    <div class="h1">Все ваши подписки</div>
</header>

<section class="section-card">
    <TextField 
        bind:value={searchQuery} 
        label="Поиск" 
        placeholder="Введите имя пользователя или название вишлиста..."
    />

    <!-- Панель сортировки -->
    <div class="sort-panel">
        <div class="sort-header">
            <div class="sort-title">Сортировка</div>
        </div>
        
        <div class="sort-options">
            <label class="sort-option">
                <input 
                    type="radio" 
                    name="sort" 
                    value="default" 
                    bind:group={sortBy}
                    class="sort-radio"
                />
                <span class="sort-label">По умолчанию (без сортировки)</span>
            </label>
            
            <label class="sort-option">
                <input 
                    type="radio" 
                    name="sort" 
                    value="users" 
                    bind:group={sortBy}
                    class="sort-radio"
                />
                <span class="sort-label">Только пользователи</span>
            </label>
            
            <label class="sort-option">
                <input 
                    type="radio" 
                    name="sort" 
                    value="wishlists" 
                    bind:group={sortBy}
                    class="sort-radio"
                />
                <span class="sort-label">Только вишлисты</span>
            </label>
            
            <label class="sort-option">
                <input 
                    type="radio" 
                    name="sort" 
                    value="birth_date_asc" 
                    bind:group={sortBy}
                    class="sort-radio"
                />
                <span class="sort-label">Дата рождения (по убыванию)</span>
            </label>
            
            <label class="sort-option">
                <input 
                    type="radio" 
                    name="sort" 
                    value="birth_date_desc" 
                    bind:group={sortBy}
                    class="sort-radio"
                />
                <span class="sort-label">Дата рождения (по возрастанию)</span>
            </label>
        </div>
    </div>
</section>

<section class="section-card">
    {#if isLoading}
        <div class="loading-indicator">
            Загрузка подписок...
        </div>
    {:else if errorMessage}
        <div class="error-message">
            {errorMessage}
        </div>
    {:else if $subscriptionsStore.length === 0}
        <p class="empty-note">
            У вас пока нет подписок. Вы можете подписаться на других пользователей или их вишлисты.
        </p>
    {:else if filteredAndSortedSubscriptions.length === 0}
        <p class="empty-note">
            По вашему запросу ничего не найдено. Попробуйте изменить параметры поиска или сортировки.
        </p>
    {:else}
        <div class="subscriptions-list">
            {#each filteredAndSortedSubscriptions as subscription (subscription.sub_id)}
                <div 
                    class="subscription-card"
                    on:click={() => handleOpenItem(subscription)}
                    role="button"
                    tabindex="0"
                    on:keydown={(e) => e.key === 'Enter' && handleOpenItem(subscription)}
                >
                    <!-- Контент подписки -->
                    {#if subscription.type === 'user'}
                        <!-- Подписка на пользователя -->
                        <div class="subscription-content">
                            <Avatar 
                                size={60}
                                src={subscription.photo}
                                initials={getInitials(subscription.name)}
                            />
                            
                            <div class="subscription-info">
                                <div class="subscription-title" title={subscription.name}>
                                    {subscription.name || 'Пользователь'}
                                </div>
                                
                                <div class="subscription-meta">
                                    <span>Дата рождения: {subscription.birth_date || 'не указана'}</span>
                                </div>
                                
                            </div>
                        </div>
                    {:else}
                        <!-- Подписка на вишлист -->
                        <div class="subscription-content">
                            <div class="wishlist-cover">
                                {#if subscription.photo}
                                    <img 
                                        src={subscription.photo} 
                                        alt={subscription.name}
                                        class="cover-image"
                                    />
                                {:else}
                                    <img 
                                        src={ICON_WISHLIST} 
                                        alt="Вишлист"
                                        class="cover-placeholder"
                                    />
                                {/if}
                            </div>
                            
                            <div class="subscription-info">
                                <div class="subscription-title" title={subscription.name}>
                                    {subscription.name || 'Вишлист'}
                                </div>
                                
                                <div class="subscription-meta">
                                    <span>Владелец: {subscription.owner_name || 'не указан'}</span>
                                    <span> · </span>
                                    <span>{subscription.total_wishes || 0} {getWishesWord(subscription.total_wishes || 0)}</span>
                                </div>

                            </div>
                        </div>
                    {/if}

                    <!-- Кнопки действий -->
                    <div class="subscription-actions">
                        <!-- Кнопка отписки -->
                        <button
                            class="action-button unsubscribe-button"
                            on:click|stopPropagation={() => handleUnsubscribe(subscription)}
                            aria-label="Отписаться"
                        >
                            Отписаться
                        </button>

                        <!-- Стрелка для перехода -->
                        <button
                            class="action-button arrow-button"
                            on:click|stopPropagation={() => handleOpenItem(subscription)}
                            aria-label="Открыть"
                        >
                            <img src={ICON_ARROW} alt=">" />
                        </button>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</section>

<style>
    .subscriptions-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 0 16px;
    }

    .subscription-card {
        display: flex;
        gap: 12px;
        align-items: center;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
    }

    .subscription-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .subscription-card:focus-visible {
        outline: 2px solid #3b82f6;
        outline-offset: 2px;
    }

    .subscription-content {
        flex: 1;
        display: flex;
        gap: 12px;
        align-items: center;
    }

    .subscription-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 4px;
        min-width: 0;
    }

    .subscription-title {
        font-size: 16px;
        font-weight: 600;
        color: #111827;
        line-height: 1.3;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .subscription-meta {
        font-size: 13px;
        color: #6b7280;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 4px;
    }

    /* Стили для обложки вишлиста */
    .wishlist-cover {
        width: 60px;
        height: 60px;
        flex-shrink: 0;
        border-radius: 12px;
        background: #f9fafb;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }

    .cover-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .cover-placeholder {
        width: 32px;
        height: 32px;
        opacity: 0.7;
        object-fit: contain;
    }

    /* Кнопки действий */
    .subscription-actions {
        display: flex;
        flex-direction: column;
        gap: 8px;
        align-items: flex-end;
    }

    .action-button {
        border: none;
        cursor: pointer;
        transition: background-color 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .unsubscribe-button {
        padding: 6px 12px;
        font-size: 13px;
        background: #fee2e2;
        color: #dc2626;
        border-radius: 8px;
        font-weight: 500;
    }

    .unsubscribe-button:hover {
        background: #fecaca;
    }

    .arrow-button {
        width: 36px;
        height: 36px;
        background: transparent;
        border-radius: 50%;
        padding: 6px;
    }

    .arrow-button:hover {
        background: #f3f4f6;
    }

    .arrow-button img {
        width: 20px;
        height: 20px;
        object-fit: contain;
    }

    .empty-note {
        text-align: center;
        padding: 40px 16px;
        color: #6b7280;
        font-size: 16px;
    }

        /* Панель сортировки */
    .sort-panel {
        margin-top: 16px;
        padding: 12px;
        background: #f9fafb;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }

    .sort-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    .sort-title {
        font-size: 14px;
        font-weight: 600;
        color: #374151;
    }

    /* .subscriptions-counts {
        display: flex;
        gap: 8px;
    }

    .count-badge {
        font-size: 12px;
        padding: 4px 8px;
        background: #e0e7ff;
        color: #4f46e5;
        border-radius: 12px;
        font-weight: 500;
    } */

    .sort-options {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .sort-option {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        padding: 6px 8px;
        border-radius: 8px;
        transition: background-color 0.2s;
    }

    .sort-option:hover {
        background: #f3f4f6;
    }

    .sort-radio {
        margin: 0;
        cursor: pointer;
    }

    .sort-label {
        font-size: 13px;
        color: #4b5563;
        cursor: pointer;
        user-select: none;
    }

    .sort-radio:checked + .sort-label {
        font-weight: 600;
        color: #111827;
    }
    
    .loading-indicator {
        text-align: center;
        padding: 40px;
        color: #6b7280;
        font-size: 16px;
    }
    
    .error-message {
        text-align: center;
        padding: 40px;
        color: #dc2626;
        font-size: 16px;
        background: #fee2e2;
        border-radius: 12px;
        margin: 16px;
    }

    /* Адаптивность */
    @media (max-width: 480px) {
        .subscription-card {
            flex-direction: column;
            align-items: stretch;
            gap: 16px;
        }

        .sort-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }

        .subscription-content {
            width: 100%;
        }

        .subscription-actions {
            flex-direction: row;
            justify-content: space-between;
            width: 100%;
            margin-top: 12px;
            border-top: 1px solid #e5e7eb;
            padding-top: 12px;
        }
    }
</style>