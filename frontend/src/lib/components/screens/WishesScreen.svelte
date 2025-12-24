<script>
    import Button from '$lib/components/ui/Button.svelte';
    import { wishesStore, wishlistsStore } from '$lib/stores/data.js';

    const iconGift = '/icons/gift3.png';
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
    };

    const handleDelete = () => {
        console.log('Удаление желания:', selectedWish.id);
        // TODO: Реализовать удаление
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


</script>

<!--2009/0_Dass_25.12.2025-->
{#if wishlistId && currentWishlist}
    <!-- Шапка для режима просмотра вишлиста -->
    <header class="app-header with-back">
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
                    <Button kind="ghost" on:click={handleEdit}>Редактировать</Button>
                    <Button kind="danger" on:click={handleDelete}>Удалить</Button>
                </div>
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
</style>

