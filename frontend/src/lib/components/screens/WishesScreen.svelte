<script>
    import { createEventDispatcher } from 'svelte';
    import Button from '../ui/Button.svelte';
    import { wishesStore, wishlistsStore } from '../../stores/data.js';

    const dispatch = createEventDispatcher();

    const iconGift = '/icons/gift3.png';
    const ICON_WARNING = '/icons/warning.png';
    export let wishlistId = null; //2009/0_Dass_25.12.2025

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
    const openDetailModal = (wish) => {
        selectedWish = wish;
        showDetailModal = true;
    };

    // Закрыть модальное окно
    const closeDetailModal = () => {
        showDetailModal = false;
        selectedWish = null;
    };

    // Получить названия вишлистов по их ID
    const getWishlistNames = (wishlistIds) => {
        if (!wishlistIds || wishlistIds.length === 0) return [];
        
        return wishlistIds
            .map(id => {
                const wishlist = $wishlistsStore.find(wl => wl.id === id);
                return wishlist ? wishlist.title : null;
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

    // открытие вишлиста 2009/0_Dass_25.12.2025
    $: filteredWishes = wishlistId 
        ? $wishesStore.filter(wish => 
            (wish.wishlistIds || []).includes(wishlistId)
          )
        : $wishesStore;

    $: currentWishlist = wishlistId 
        ? $wishlistsStore.find(wl => wl.id === wishlistId)
        : null;

    // 2009_1_Dass_25.12.2025 -->
    let showAddExistingModal = false;
    let selectedWishesForAdding = new Set();
    const openAddExistingModal = () => {
        selectedWishesForAdding = new Set();
        showAddExistingModal = true;
    };
    const addSelectedWishesToWishlist = () => {
        if (!wishlistId) return;
        
        $wishesStore = $wishesStore.map(wish => {
            if (selectedWishesForAdding.has(wish.id)) {
                const existingWishlistIds = wish.wishlistIds || [];
                if (!existingWishlistIds.includes(wishlistId)) {
                    return {
                        ...wish,
                        wishlistIds: [...existingWishlistIds, wishlistId]
                    };
                }
            }
            return wish;
        });
            
        // Закрываем модальное окно
        showAddExistingModal = false;
        selectedWishesForAdding.clear();
    };
    
    $: availableWishes = $wishesStore.filter(wish => 
        !wish.wishlistIds?.includes(wishlistId)
    );
    // 2009_1_Dass_25.12.2025 <--

    // 2009_2_Dass_25.12.2025 -->
    const handleRemoveFromWishlist = (wishId) => {
        if (!wishlistId) return;
        //2006_7_Dass_25.12.2025
        deleteOption = 'fromwishlists';
        
        const wish = $wishesStore.find(w => w.id === wishId);
        if (wish) {
            selectedWish = wish;
            showFromWishlistDeleteModal = true;
        }
    };
    // 2009_2_Dass_25.12.2025 <--

    // 2009_3_Dass_25.12.2025 -->
    let showCopyMoveModal = false;
    let actionType = 'copy'; // 'copy' или 'move'
    let targetWishlists = new Set(); // Выбранные вишлисты для копирования/перемещения
    let wishToCopyMove = null;

    const openCopyMoveModal = (wishId, type) => {
        wishToCopyMove = wishId;
        actionType = type;
        targetWishlists = new Set();
        showCopyMoveModal = true;
    };
    //выполнить перемещение/копирование
    const executeCopyMove = () => {
        if (!wishToCopyMove || targetWishlists.size === 0) return;
        
        $wishesStore = $wishesStore.map(wish => {
            if (wish.id === wishToCopyMove) {
                const existingWishlistIds = wish.wishlistIds || [];
                let newWishlistIds = [...existingWishlistIds];
                // Добавляем выбранные вишлисты
                targetWishlists.forEach(wishlistId => {
                    if (!newWishlistIds.includes(wishlistId)) {
                        newWishlistIds.push(wishlistId);
                    }
                });
                // Если это перемещение, удаляем текущий вишлист
                if (actionType === 'move' && wishlistId) {
                    newWishlistIds = newWishlistIds.filter(id => id !== wishlistId);
                }
                return {
                    ...wish,
                    wishlistIds: newWishlistIds
                };
            }
            return wish;
        });
        
        // Закрываем модальные окна
        closeCopyMoveModal();
        closeDetailModal();
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
    $: availableWishlists = $wishlistsStore.filter(wl => 
        !wishlistId || wl.id !== wishlistId
    );
    // 2009_3_Dass_25.12.2025 <--

    //2006_7_Dass_25.12.2025 -->
    let deleteOption = null;  
    let showFullDeleteModal = false;
    let showFromWishlistDeleteModal = false;  

    const executeFullDelete = () => {
        if (!selectedWish) return;
        // Удалить полностью из всех вишлистов
        $wishesStore = $wishesStore.filter(wish => wish.id !== selectedWish.id);
        console.log('Желание полностью удалено:', selectedWish.id);
        // Закрываем модальные окна
        closeFullDeleteModal();
        closeDetailModal();
    };

    const executeFromWishlistDelete = () => {
        if (!selectedWish || !wishlistId) return;
        // Удалить только из текущего вишлиста
        $wishesStore = $wishesStore.map(wish => {
            if (wish.id === selectedWish.id) {
                const existingWishlistIds = wish.wishlistIds || [];
                const newWishlistIds = existingWishlistIds.filter(id => id !== wishlistId);
                return {
                    ...wish,
                    wishlistIds: newWishlistIds
                };
            }
            return wish;
        });
        console.log('Желание удалено из вишлиста:', selectedWish.id);
        // Закрываем модальные окна
        closeFromWishlistDeleteModal();
        closeDetailModal();
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
</script>

<!--2009/0_Dass_25.12.2025-->
{#if wishlistId && currentWishlist}
    <!-- Шапка для режима просмотра вишлиста -->
    <header class="app-header">
        <div class="h1">{currentWishlist.title}</div>
        <div class="wishlist-subtitle">
            {filteredWishes.length} {filteredWishes.length === 1 ? 'желание' : 
            filteredWishes.length >= 2 && filteredWishes.length <= 4 ? 'желания' : 'желаний'}
        </div>
    </header>
{:else}
    <!-- Стандартная шапка -->
    <header class="app-header">
        <div class="h1">Все ваши желания</div>
    </header>
{/if}

<section class="section-card">
    <!--2009/0_Dass_25.12.2025-->
    {#if filteredWishes.length === 0}
        <p class="empty-note">
            {#if wishlistId}
                В этом вишлисте пока нет желаний.
            {:else}
                У вас пока нет желаний. Нажмите «Новое желание», чтобы добавить первое.
            {/if}
        </p>
    {:else}
        <div class="wish-grid">
            {#each filteredWishes as wish (wish.id)}
                <!-- svelte-ignore a11y_no_noninteractive_element_to_interactive_role -->
                <article 
                    class="wish-card" 
                    on:click={() => openDetailModal(wish)}
                    role="button"
                    tabindex="0"
                    on:keydown={(e) => e.key === 'Enter' && openDetailModal(wish)}
                >
                    <div class="wish-card-image">
                        {#if wish.imageUrl}
                            <img src={wish.imageUrl} alt={wish.title} class="wish-image" />
                        {:else}
                            <img src={iconGift} alt="Подарок" class="wish-image placeholder" />
                        {/if}
                    </div>

                    <div class="wish-card-body">
                        <div class="wish-title" title={wish.title}>{wish.title}</div>
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
{:else}
    <div style="padding:0 16px 12px;">
        <Button full on:click={openAddExistingModal}>
            + Добавить существующее желание
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
                <!-- Изображение -->
                <div class="detail-image">
                    {#if selectedWish.imageUrl}
                        <img src={selectedWish.imageUrl} alt={selectedWish.title} />
                    {:else}
                        <img src={iconGift} alt="Подарок" class="detail-placeholder" />
                    {/if}
                </div>

                <!-- Название -->
                <h2 class="detail-title">{selectedWish.title}</h2>

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
                {#if selectedWish.link}
                    <div class="detail-section">
                        <h3>Ссылка на товар</h3>
                        <a 
                            href={selectedWish.link} 
                            class="detail-link"
                            on:click|stopPropagation={(e) => openLink(selectedWish.link, e)}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            {selectedWish.link}
                        </a>
                    </div>
                {/if}

                <!-- Вишлисты -->
                {#if selectedWish.wishlistIds && selectedWish.wishlistIds.length > 0}
                    <div class="detail-section">
                        <h3>Добавлено в вишлисты</h3>
                        <div class="detail-wishlists">
                            {#each getWishlistNames(selectedWish.wishlistIds) as wishlistName}
                                <span class="wishlist-tag">{wishlistName}</span>
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
                    {#if wishlistId}
                        <!-- Если мы в режиме вишлиста -->
                        <Button kind="ghost" on:click={() => openCopyMoveModal(selectedWish.id, 'copy')}>
                            Копировать в...
                        </Button>
                        <Button kind="ghost" on:click={() => openCopyMoveModal(selectedWish.id, 'move')}>
                            Переместить в...
                        </Button>
                        <Button kind="danger" on:click={() => handleRemoveFromWishlist(selectedWish.id)}>
                            Удалить из вишлиста
                        </Button>
                    {:else}
                        <!-- В обычном режиме показываем стандартные кнопки -->
                        <Button kind="ghost" on:click={handleEdit}>Редактировать</Button>
                        <Button kind="danger" on:click={handleDelete}>Удалить</Button>
                    {/if}
                </div>
            </div>
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
                                    <div class="wish-selection-title">{wish.title}</div>
                                    {#if wish.price != null}
                                        <div class="wish-selection-price">{formatPrice(wish)}</div>
                                    {/if}
                                </div>
                                
                                <div class="wish-selection-image">
                                    {#if wish.imageUrl}
                                        <img src={wish.imageUrl} alt={wish.title} />
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
                
                {#if availableWishlists.length === 0}
                    <p class="empty-message">
                        Нет доступных вишлистов для {actionType === 'copy' ? 'копирования' : 'перемещения'}
                    </p>
                {:else}
                    <div class="wishlists-selection-list">
                        {#each availableWishlists as wishlist (wishlist.id)}
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
                                        {$wishesStore.filter(w => 
                                            (w.wishlistIds || []).includes(wishlist.id)
                                        ).length} желаний
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
                Вы собираетесь удалить желание "<strong>{selectedWish.title}</strong>".
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
                Вы хотите удалить "<strong>{selectedWish.title}</strong>" только из этого вишлиста.
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


</style>

