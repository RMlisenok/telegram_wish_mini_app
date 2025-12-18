<script>
    import { wishesStore } from '$lib/stores/data.js';

    const iconGift = '/icons/gift3.png';

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

</script>

<header class="app-header">
    <div class="h1">Все ваши желания</div>
</header>

<section class="section-card">
    {#if $wishesStore.length === 0}
        <p class="empty-note">
            У вас пока нет желаний. Нажмите «Новое желание», чтобы добавить первое.
        </p>
    {:else}
        <div class="wish-grid">
            {#each $wishesStore as wish (wish.id)}
                <article class="wish-card">
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

<style>

    .wish-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(214px, 1fr));
        gap: 16px;
        padding: 0 16px;
        justify-content: center;
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
</style>

