<script>
    import Avatar from '../ui/Avatar.svelte';
    import TextField from '../ui/TextField.svelte';
    import { 
        subscribersStore, 
        getMySubscribers
    } from '../../../types/subscribers.ts';

    //  Lyse Modifications

    import { createEventDispatcher, onMount } from 'svelte';
    const dispatch = createEventDispatcher();

    export let token;

    const ICON_ARROW = '../../../../static/icons/arrow-right.png';
    const ICON_CHECK = '../../../../static/icons/check.png';

    let searchQuery = '';
    let isLoading = true;
    let errorMessage = '';

    onMount(async () => {
        if (!token) {
            console.warn('Token не передан в SubscribersScreen');
            errorMessage = 'Требуется авторизация';
            isLoading = false;
            return;
        }
        await loadSubscribers();
    });

    async function loadSubscribers() {
        try {
            isLoading = true;
            errorMessage = '';
            
            if (!token) {
                errorMessage = 'Токен не найден';
                console.error('Токен не найден для загрузки подписчиков');
                return;
            }
            
            await getMySubscribers(token, true, 100);
        } catch (error) {
            errorMessage = error.message || 'Не удалось загрузить подписчиков';
            console.error('Ошибка загрузки подписчиков:', error);
        } finally {
            isLoading = false;
        }
    }

    // Фильтрация подписчиков по поисковому запросу
    $: filteredSubscribers = (() => {
        let result = $subscribersStore;
        const query = searchQuery.trim().toLowerCase();

        if (query) {
            result = result.filter(subscriber => {
                const userName = subscriber?.name?.toLowerCase() || '';
                return userName.includes(query);
            });
        }

        return result;
    })();

    // Определение статуса блокировки
    const getBlockStatus = (subscriber) => {
        const hasProfileAccess = subscriber.can_view_profile;
        const hasWishlistsAccess = subscriber.can_view_wishlists;
        
        if (!hasProfileAccess && !hasWishlistsAccess) {
            return 'blocked'; // Полностью заблокирован
        } else if (!hasProfileAccess || !hasWishlistsAccess) {
            return 'partial'; // Частично заблокирован
        } else {
            return 'unblocked'; // Не заблокирован
        }
    };

    // Получение текста статуса блокировки
    const getBlockStatusText = (subscriber) => {
        const status = getBlockStatus(subscriber);
        switch (status) {
            case 'blocked':
                return 'Полная блокировка';
            case 'partial':
                if (!subscriber.can_view_profile && subscriber.can_view_wishlists) {
                    return 'Только профиль заблокирован';
                } else if (subscriber.can_view_profile && !subscriber.can_view_wishlists) {
                    return 'Только вишлисты заблокированы';
                }
                return 'Частичная блокировка';
            case 'unblocked':
                return 'Полный доступ ко всему';
            default:
                return '';
        }
    };

    // Обработчик изменения прав доступа к профилю
    const handleToggleProfileAccess = (subscriberId, event) => {
        if (event) event.stopPropagation();
        
        subscribersStore.update(list => {
            return list.map(subscriber => {
                if (subscriber.id === subscriberId) {
                    const newProfileAccess = !subscriber.can_view_profile;
                    // Обновляем общий статус блокировки
                    const newBlockedStatus = !newProfileAccess && !subscriber.can_view_wishlists;
                    return {
                        ...subscriber,
                        can_view_profile: newProfileAccess,
                        is_blocked: newBlockedStatus
                    };
                }
                return subscriber;
            });
        });
    };

    // Обработчик изменения прав доступа к вишлистам
    const handleToggleWishlistsAccess = (subscriberId, event) => {
        if (event) event.stopPropagation();
        
        subscribersStore.update(list => {
            return list.map(subscriber => {
                if (subscriber.id === subscriberId) {
                    const newWishlistsAccess = !subscriber.can_view_wishlists;
                    // Обновляем общий статус блокировки
                    const newBlockedStatus = !subscriber.can_view_profile && !newWishlistsAccess;
                    return {
                        ...subscriber,
                        can_view_wishlists: newWishlistsAccess,
                        is_blocked: newBlockedStatus
                    };
                }
                return subscriber;
            });
        });
    };

    // Обработчик подписки/отписки
    const handleToggleSubscription = async (subscriber, event) => {
        if (event) event.stopPropagation();
        
        try {
            if (!token) {
                alert('Ошибка авторизации');
                return;
            }
            
            // TODO: Реализовать API для подписки/отписки
            // Временная заглушка
            console.log('Переключение подписки на пользователя:', subscriber.user_id);
            
            // Обновляем локальное состояние
            // subscribersStore.update(list => {
            //     return list.map(sub => {
            //         if (sub.user_id === subscriber.user_id) {
            //             // Здесь будет логика обновления статуса подписки
            //             // после реализации API
            //         }
            //         return sub;
            //     });
            // });
            
            alert('Функция подписки будет реализована в ближайшее время');
            
        } catch (error) {
            console.error('Ошибка переключения подписки:', error);
            alert('Произошла ошибка при изменении подписки');
        }
    };

    // Получение инициалов для аватара
    const getInitials = (name) => {
        if (!name) return '??';
        const parts = name.trim().split(' ');
        return parts.slice(0, 2).map(p => p[0]).join('').toUpperCase();
    };

    // Обработчик открытия профиля подписчика
    const handleOpenProfile = (subscriber) => {

        // Lyse Modifications

        dispatch('open-profile', { profileId: subscriber.user_id });

        console.log('Открытие профиля подписчика:', subscriber.user_id);
        // TODO: Реализовать переход к профилю подписчика
    };

    // Форматирование даты для отображения
    const formatDateForDisplay = (dateStr) => {
        if (!dateStr) return 'не указана';
        
        // Если дата в формате YYYY-MM-DD
        if (dateStr.includes('-')) {
            const parts = dateStr.split('-');
            if (parts.length === 3) {
                const [year, month, day] = parts;
                return `${day}.${month}.${year}`;
            }
        }
        
        // Если дата уже в правильном формате
        return dateStr;
    };

</script>

<header class="app-header">
    <div class="h1">Все ваши подписчики</div>
</header>

<section class="section-card">
    <TextField 
        bind:value={searchQuery} 
        label="Поиск" 
        placeholder="Введите имя пользователя..."
    />
</section>

<section class="section-card">
    {#if $subscribersStore.length === 0}
        <p class="empty-note">
            У вас пока нет подписчиков.
        </p>
    {:else if filteredSubscribers.length === 0}
        <p class="empty-note">
            По вашему запросу ничего не найдено. Попробуйте изменить поисковый запрос.
        </p>
    {:else}
        <div class="subscribers-list">
            {#each filteredSubscribers as subscriber (subscriber.sub_id)}
                <div 
                    class="subscriber-card"
                    on:click={() => handleOpenProfile(subscriber)}
                    role="button"
                    tabindex="0"
                    on:keydown={(e) => e.key === 'Enter' && handleOpenProfile(subscriber)}
                >
                    <!-- Аватар и основная информация -->
                    <div class="subscriber-content">
                        <!-- <Avatar 
                            size={60}
                            src={subscriber.photo}
                            initials={getInitials(subscriber.name)}
                            style={subscriber.is_blocked ? 'opacity: 0.5; filter: grayscale(100%);' : ''}
                        /> -->
                        <Avatar 
                            size={60}
                            src={subscriber.photo}
                            initials={getInitials(subscriber.name)}
                        />
                        
                        <div class="subscriber-info">
                            <div class="subscriber-name" title={subscriber.name}>
                                {subscriber.name}
                            </div>
                            
                            <div class="subscriber-meta">
                                <span>Дата рождения: {formatDateForDisplay(subscriber.birth_date)}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Кнопки управления -->
                    <div class="subscriber-controls">
                        <!-- Кнопка подписки/отписки -->
                        <!-- <button
                            class="control-button {subscriber.am_i_subscribed_to_them ? 'subscribed-btn' : 'subscribe-btn'}"
                            on:click|stopPropagation={() => handleToggleSubscription(subscriber.id)}
                            aria-label="{subscriber.am_i_subscribed_to_them ? 'Отписаться' : 'Подписаться'}"
                        >
                            {#if subscriber.am_i_subscribed_to_them}
                                <img src={ICON_CHECK} alt="✓" class="control-icon" />
                                <span>Вы подписаны</span>
                            {:else}
                                <span>Подписаться</span>
                            {/if}
                        </button> -->

                        <button
                            class="control-button subscribe-btn"
                            on:click|stopPropagation={(e) => handleToggleSubscription(subscriber, e)}
                            aria-label="Подписаться"
                        >
                            Подписаться
                        </button>

                        <!-- Чекбоксы управления доступом
                        <div class="access-controls">
                            <label class="access-checkbox">
                                <input 
                                    type="checkbox" 
                                    checked={subscriber.can_view_profile}
                                    on:click={(e) => handleToggleProfileAccess(subscriber.id, e)}
                                    class="access-input"
                                />
                                <span class="access-label">Доступ к профилю</span>
                            </label>
                            
                            <label class="access-checkbox">
                                <input 
                                    type="checkbox" 
                                    checked={subscriber.can_view_wishlists}
                                    on:click={(e) => handleToggleWishlistsAccess(subscriber.id, e)}
                                    class="access-input"
                                />
                                <span class="access-label">Доступ к вишлистам</span>
                            </label> -->

                            <!-- Надпись со статусом блокировки -->
                            <!-- <div class="block-status {getBlockStatus(subscriber)}">
                                {getBlockStatusText(subscriber)}
                            </div>
                        </div>  -->

                        <!-- Стрелка для перехода -->
                        <button
                            class="control-button arrow-button"
                            on:click|stopPropagation={() => handleOpenProfile(subscriber)}
                            aria-label="Открыть профиль"
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
    .subscribers-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 0 16px;
    }

    .subscriber-card {
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

    .subscriber-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .subscriber-card:focus-visible {
        outline: 2px solid #3b82f6;
        outline-offset: 2px;
    }

    .subscriber-content {
        display: flex;
        gap: 12px;
        align-items: center;
        flex: 1;
    }

    .subscriber-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 4px;
        min-width: 0;
    }

    .subscriber-name {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
        line-height: 1.3;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .subscriber-meta {
        font-size: 13px;
        color: #6b7280;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 4px;
    }

    /* Управление подписчиками */
    .subscriber-controls {
        display: flex;
        flex-direction: column;
        gap: 12px;
        align-items: flex-end;
        min-width: 280px;
    }

    .control-button {
        border: none;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        font-size: 13px;
        font-weight: 500;
        padding: 8px 12px;
        border-radius: 8px;
        white-space: nowrap;
    }

    .arrow-button {
        width: 36px;
        height: 36px;
        background: transparent;
        border-radius: 50%;
        padding: 8px;
    }

    .arrow-button:hover {
        background: #f3f4f6;
    }

    .arrow-button img {
        width: 20px;
        height: 20px;
        object-fit: contain;
    }

    /* Кнопки подписки */
    .subscribe-btn {
        background: #dbeafe;
        color: #1d4ed8;
    }

    .subscribe-btn:hover {
        background: #bfdbfe;
    }

    .subscribed-btn {
        background: #dcfce7;
        color: #16a34a;
    }

    .subscribed-btn:hover {
        background: #bbf7d0;
    }

    .control-icon {
        width: 16px;
        height: 16px;
        object-fit: contain;
    }

    /* Управление доступом */
    .access-controls {
        display: flex;
        flex-direction: column;
        gap: 8px;
        background: #f9fafb;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        width: 100%;
    }

    .access-checkbox {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        font-size: 13px;
        color: #4b5563;
    }

    .access-input {
        margin: 0;
        cursor: pointer;
    }

    .access-label {
        cursor: pointer;
        user-select: none;
    }
    
    /* Статус блокировки */
    .block-status {
        font-size: 12px;
        font-weight: 500;
        padding: 6px 10px;
        border-radius: 6px;
        text-align: center;
        margin-top: 4px;
    }

    .block-status.blocked {
        background: #fee2e2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }

    .block-status.partial {
        background: #fef3c7;
        color: #d97706;
        border: 1px solid #fde68a;
    }

    .block-status.unblocked {
        background: #d1fae5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }

    .empty-note {
        text-align: center;
        padding: 40px 16px;
        color: #6b7280;
        font-size: 16px;
    }

    /* Адаптивность */
    @media (min-width: 769px) {
        .subscriber-controls {
            min-width: 250px;
        }
    }

    @media (max-width: 768px) {
        .subscriber-card {
            flex-direction: column;
            align-items: stretch;
            gap: 16px;
        }
        
        .subscriber-content {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
            width: 100%;
        }
        
        .subscriber-info {
            width: 100%;
        }
        
        .subscriber-name {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }

        .subscriber-controls {
            min-width: auto;
            width: 100%;
            align-items: stretch;
            gap: 16px;
            position: relative;
        }

        .subscribe-btn,
        .subscribed-btn {
            align-self: flex-start;
            width: auto;
            min-width: 120px;
        }

        .access-controls {
            padding: 10px;
            align-self: flex-start;
            width: auto;
            min-width: 120px;
        }

        .block-status {
            font-size: 11px;
            padding: 4px 8px;
        }

        .arrow-button {
            position: absolute;
            bottom: 0;
            right: 0;
            width: 32px;
            height: 32px;
            margin-top: 18px;
        }
    }

    @media (max-width: 480px) {
        .subscriber-card {
            padding: 12px;
        }
        
        .subscriber-content {
            gap: 10px;
        }

        .subscriber-name {
            font-size: 16px;
        }

        .subscriber-meta {
            font-size: 12px;
        }

        .control-button {
            padding: 6px 10px;
            font-size: 12px;
        }

        .subscribe-btn,
        .subscribed-btn {
            min-width: 110px;
        }

        .access-controls {
            padding: 8px;
            gap: 6px;
            min-width: 110px;
        }

        .arrow-button {
            width: 30px;
            height: 30px;
        }

        .arrow-button img {
            width: 16px;
            height: 16px;
        }

        .access-checkbox {
            font-size: 12px;
        }

        .block-status {
            font-size: 10px;
            padding: 3px 6px;
        }
    }
</style>