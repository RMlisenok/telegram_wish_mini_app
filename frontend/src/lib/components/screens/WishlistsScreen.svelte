<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import Button from '../ui/Button.svelte';
    import { wishesStore } from '../../stores/data.js';
    import { wishlistsStore, loadWishlists, deleteWishlist } from '../../../types/wishlists.ts';

    const dispatch = createEventDispatcher();

    // Иконки
    const ICON_EDIT = '../../../../static/icons/edit.png';
    const ICON_TRASH = '../../../../static/icons/trash.png';
    const ICON_GIFT = '../../../../static/icons/maingift.svg';
    const ICON_ARROW = '../../../../static/icons/arrow-right.png';
    const ICON_WARNING = '../../../../static/icons/warning.png';
    
    // Иконки приватности   
    const ICON_PUBLIC_FRIENDS = '../../../../static/icons/view.png';
    const ICON_PRIVATE = '../../../../static/icons/unview.png';

    //add response all wishlists -->
    export let token;
    onMount(async () => {
        if (token) {
            await fetchWishlists();
        }
    });

    async function fetchWishlists() {
        if (!token) {
            console.error('Токен отсутствует');
            return;
        }

        try {
            await loadWishlists(token);
        } catch (err) {
            console.error('Ошибка загрузки вишлистов:', err);
        }
    }
    // <--

    const openCreateWishlists = () => {
        dispatch('openCreateWishlists');
    };
   
    const handleEditWishlist = (wishlistId) => {
        console.log('Редактирование вишлиста:', wishlistId);
        // TODO: Реализовать редактирование вишлиста
        dispatch('openEditWishlists', { id: wishlistId,
                                        token: token
         }) //2008_3_Dass_24.12.2025
    };

    const handleDeleteWishlist = (wishlistId) => {
        console.log('Удаление вишлиста:', wishlistId);
        //2008_4_Dass_25.12.2025
        const wishlist = $wishlistsStore.find(wl => wl.id === wishlistId);
        if (!wishlist) return;
        
        wishesInWishlist = getWishlistCount(wishlistId);
        
        wishlistToDelete = wishlistId;
        wishlistToDeleteName = wishlist.title;
        showDeleteWishlistModal = true;
    };

    const handleOpenWishlist = (wishlistId) => {
        console.log('Открытие вишлиста:', wishlistId);
        // TODO: Реализовать переход в вишлист
        dispatch('openWishlistDetail', { wishlistId }); //2009/0_Dass_25.12.2025
    };

    const handleOpenOwnerProfile = (ownerId) => {
        dispatch('openMainScreen');
    };

    // Получить слово "желание" в корректной форме в зависимости от числа
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

    // Получить количество желаний в вишлисте
    const getWishlistCount = (wishlistId) => {
        return $wishesStore.filter((wish) => 
            (wish.wishlistIds || []).includes(wishlistId)
        ).length;
    };

    // Получить текст и иконку для статуса приватности
    const getPrivacyInfo = (privacy) => {
        switch (privacy) {
            case 'public':
                return {
                    icon: ICON_PUBLIC_FRIENDS,
                    text: 'Виден всем'
                };
            case 'restricted':
                return {
                    icon: ICON_PUBLIC_FRIENDS,
                    text: 'Виден друзьям'
                };
            case 'private':
            default:
                return {
                    icon: ICON_PRIVATE,
                    text: 'Виден только вам'
                };
        }
    };

    // Получить владельца вишлиста
    const getWishlistOwner = (wishlist) => {
        // TODO: Получить данные владельца
        return {
            id: wishlist.ownerId || 'user_1',
            name: wishlist.ownerName || 'Вы'
        };
    };

    //2008_4_Dass_25.12.2025 -->
    let showDeleteWishlistModal = false;
    let wishlistToDelete = null;
    let wishlistToDeleteName = '';
    let wishesInWishlist = 0;

    // функция подтверждения удаления вишлиста
    const confirmDeleteWishlist = async () => {
        if (!wishlistToDelete) return;
        // Удаляем этот wishlistId из всех желаний
        try {
            // Вызываем API для удаления
            await deleteWishlist(token, wishlistToDelete);
            
            // Локальное обновление желаний
            $wishesStore = $wishesStore.map(wish => {
                const wishlistIds = wish.wishlistIds || [];
                if (wishlistIds.includes(wishlistToDelete)) {
                    const newWishlistIds = wishlistIds.filter(id => id !== wishlistToDelete);
                    return {
                        ...wish,
                        wishlistIds: newWishlistIds
                    };
                }
                return wish;
            });
            
            console.log('Вишлист успешно удален:', wishlistToDelete);
            
        } catch (error) {
            console.error('Ошибка при удалении вишлиста:', error);
            showDeleteWishlistModal = false;
            wishlistToDelete = null;
            wishlistToDeleteName = '';
            wishesInWishlist = 0;
            
            alert('Не удалось удалить вишлист. Попробуйте еще раз.');
            return;
        }
        
        cancelDeleteWishlist();
        console.log('Вишлист удален:', wishlistToDelete);
    };
    //отмена удаления
    const cancelDeleteWishlist = () => {
        showDeleteWishlistModal = false;
        wishlistToDelete = null;
        wishlistToDeleteName = '';
        wishesInWishlist = 0;
    };
    //2008_4_Dass_25.12.2025 <--
</script>

<header class="app-header">
    <div class="h1">Все ваши вишлисты</div>
</header>

<section class="section-card">
    {#if $wishlistsStore.length === 0}
        <p class="empty-note">
            У вас пока нет вишлистов. Создайте первый, чтобы сгруппировать свои желания.
        </p>
    {:else}
        <div class="wishlists-list">
            {#each $wishlistsStore as wishlist (wishlist.id)}
                <div class="wishlist-card">
                    <!-- Обложка вишлиста -->
                    <div class="wishlist-cover">
                        {#if wishlist.rUrl}
                            <img 
                                src={wishlist.rUrl} 
                                alt={wishlist.title}
                                class="cover-image"
                            />
                        {:else}
                            <img 
                                src={ICON_GIFT} 
                                alt="Подарок"
                                class="cover-placeholder"
                            />
                        {/if}
                    </div>

                    <!-- Основная информация -->
                    <div class="wishlist-info">
                        <!-- Название -->
                        <div class="wishlist-title" title={wishlist.title}>
                            {wishlist.title}
                        </div>

                        <!-- Статус приватности -->
                        <div class="wishlist-privacy">
                            <img 
                                src={getPrivacyInfo(wishlist.privacy).icon} 
                                alt="" 
                                class="privacy-icon"
                            />
                            <span>{getPrivacyInfo(wishlist.privacy).text}</span>
                        </div>

                        <!-- Количество желаний -->
                        <div class="wishlist-count">
                            {wishlist.count} {getWishesWord(wishlist.count)}
                        </div>

                        <!-- Владелец -->
                        <div 
                            class="wishlist-owner"
                            on:click|stopPropagation={() => handleOpenOwnerProfile(getWishlistOwner(wishlist).id)}
                            role="button"
                            tabindex="0"
                            on:keydown={(e) => e.key === 'Enter' && handleOpenOwnerProfile(getWishlistOwner(wishlist).id)}
                        >
                            Владелец: {getWishlistOwner(wishlist).name}
                        </div>
                    </div>

                    <!-- Кнопки действий -->
                    <div class="wishlist-actions">
                        <!-- Кнопка редактирования -->
                        <button
                            class="action-button edit-button"
                            on:click|stopPropagation={() => handleEditWishlist(wishlist.id)}
                            aria-label="Редактировать вишлист"
                        >
                            <img src={ICON_EDIT} alt="Редактировать" />
                        </button>

                        <!-- Кнопка удаления -->
                        <button
                            class="action-button delete-button"
                            on:click|stopPropagation={() => handleDeleteWishlist(wishlist.id)}
                            aria-label="Удалить вишлист"
                        >
                            <img src={ICON_TRASH} alt="Удалить" />
                        </button>

                        <!-- Интерактивная стрелка для перехода -->
                        <button
                            class="action-button arrow-button"
                            on:click|stopPropagation={() => handleOpenWishlist(wishlist.id)}
                            aria-label="Открыть вишлист"
                        >
                            <img src={ICON_ARROW} alt=">" />
                        </button>

                    </div>
                </div>
            {/each}
        </div>
    {/if}
</section>

{#if showDeleteWishlistModal}
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div class="modal-backdrop" on:click={cancelDeleteWishlist}>
        <div class="confirm-modal" on:click|stopPropagation>
            <div class="confirm-icon">
                <img src={ICON_WARNING} alt="Внимание" class="warning-icon" />
            </div>
            
            <h2 class="confirm-title">Удалить вишлист?</h2>
            
            <div class="confirm-details">
                <p><strong>"{wishlistToDeleteName}"</strong></p>
                <p class="wishlist-stats">
                    В этом вишлисте <strong>{wishesInWishlist} {getWishesWord(wishesInWishlist)}</strong>
                </p>
            </div>
            
            <p class="confirm-message">
                Все желания останутся и будут доступны в списке "Все ваши желания". 
            </p>
            
            <div class="confirm-actions">
                <Button 
                    kind="ghost" 
                    on:click={cancelDeleteWishlist}
                    style="flex: 1;"
                >
                    Отмена
                </Button>
                <Button 
                    kind="danger" 
                    on:click={confirmDeleteWishlist}
                    style="flex: 1;"
                >
                    Удалить
                </Button>
            </div>
        </div>
    </div>
{/if}

<div style="padding:0 16px 12px;">
    <Button full on:click={openCreateWishlists}>+ Создать вишлист</Button>
</div>

<style>
    .wishlists-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
        padding: 0 16px;
    }

    .wishlist-card {
        display: flex;
        gap: 12px;
        align-items: flex-start;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .wishlist-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    /* Обложка */
    .wishlist-cover {
        width: 152px;
        height: 152px;
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
        width: 80px;
        height: 80px;
        opacity: 0.7;
        object-fit: contain;
    }

    /* Информация о вишлисте */
    .wishlist-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 6px;
        min-width: 0; /* Для корректной работы text-overflow */
    }

    .wishlist-title {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
        line-height: 1.3;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 2px;
    }

    .wishlist-privacy {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        color: #6b7280;
    }

    .privacy-icon {
        width: 16px;
        height: 16px;
        opacity: 0.8;
    }

    .wishlist-count {
        font-size: 14px;
        color: #059669;
        font-weight: 500;
        margin-top: 2px;
    }

    .wishlist-owner {
        font-size: 13px;
        color: #3b82f6;
        cursor: pointer;
        margin-top: 4px;
        padding: 4px 8px;
        border-radius: 8px;
        background: #eff6ff;
        border: 1px solid transparent;
        transition: all 0.2s;
        width: fit-content;
    }

    .wishlist-owner:hover {
        background: #dbeafe;
        border-color: #93c5fd;
        text-decoration: underline;
    }

    .wishlist-owner:focus-visible {
        outline: 2px solid #3b82f6;
        outline-offset: 2px;
    }

    /* Кнопки действий */
    .wishlist-actions {
        display: flex;
        flex-direction: column;
        gap: 8px;
        align-items: flex-end;
        margin-left: auto;
    }

    .action-button {
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
        padding: 8px;
    }

    .arrow-button img {
        width: 24px;
        height: 24px;
    }

    .action-button:hover {
        background: #f3f4f6;
    }

    .action-button:active {
        background: #e5e7eb;
    }

    .action-button img {
        width: 20px;
        height: 20px;
        object-fit: contain;
    }

    .edit-button img {
        opacity: 0.7;
    }

    .delete-button img {
        opacity: 0.7;
    }

    .empty-note {
        text-align: center;
        padding: 40px 16px;
        color: #6b7280;
        font-size: 16px;
    }

    /* Адаптивность */
    @media (max-width: 480px) {
        .wishlist-card {
            flex-direction: column;
            align-items: stretch;
        }

        .wishlist-cover {
            width: 100%;
            height: 200px;
            margin-bottom: 12px;
        }

        .wishlist-actions {
            flex-direction: row;
            justify-content: flex-end;
            margin-left: 0;
            margin-top: 12px;
            border-top: 1px solid #e5e7eb;
            padding-top: 12px;
        }

        .wishlist-owner {
            align-self: flex-start;
        }
    }

    /* Стили для модального окна подтверждения удаления вишлиста */
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
        z-index: 1000;
        padding: 20px;
    }

    .confirm-modal {
        width: 90%;
        max-width: 400px;
        background: white;
        border-radius: 24px;
        padding: 32px 24px 24px;
        text-align: center;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        animation: slideIn 0.3s ease-out;
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

    .confirm-icon {
        margin: 0 auto 20px;
        width: 64px;
        height: 64px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .confirm-title {
        font-size: 20px;
        font-weight: 600;
        color: #111827;
        margin: 0 0 16px 0;
    }

    .confirm-details {
        background: #F9FAFB;
        border-radius: 12px;
        padding: 16px;
        margin: 0 0 20px 0;
        border: 1px solid #E5E7EB;
    }

    .confirm-details p {
        margin: 8px 0;
        font-size: 14px;
        color: #4B5563;
    }

    .confirm-details strong {
        color: #111827;
        font-weight: 600;
    }

    .wishlist-stats {
        color: #059669 !important;
        font-weight: 500;
    }

    .confirm-message {
        font-size: 14px;
        line-height: 1.5;
        color: #6B7280;
        margin: 0 0 24px 0;
        padding: 0 4px;
    }

    .confirm-actions {
        display: flex;
        gap: 12px;
        justify-content: center;
        gap: 12px;
        max-width: 300px;
        margin: 0 auto;
    }
</style>