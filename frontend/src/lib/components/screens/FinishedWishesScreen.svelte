<!-- frontend/src/lib/components/screens/FinishedWishesScreen.svelte -->
<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import Button from '../ui/Button.svelte';
    import { wishesStore, loadFinishedWishes } from '../../../types/wishes.ts';
    
    export let token;
    const dispatch = createEventDispatcher();
    
    const iconGift = '../../../../static/icons/gift3.png';
    
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
    
    onMount(async () => {
        console.log('Загрузка исполненных желаний...');
        if (token) {
            await fetchWishes();
        } else {
            console.error('Токен не найден');
        }
    });
    
    async function fetchWishes() {
        if (!token) {
            console.error('Токен отсутствует');
            return;
        }
        try {
            await loadFinishedWishes(token);
        } catch (err) {
            console.error('Ошибка загрузки желаний:', err);
        }
    }
    
    $: finishedWishes = $wishesStore;
    
    const goBack = () => {
        dispatch('back');
    };

    $: {
        console.log('Текущие желания в store:', $wishesStore);
        console.log('Типы id в store:', $wishesStore.map(w => ({ 
            id: w.id, 
            type: typeof w.id,
            value: w.id
        })));
    }
</script>

<header class="app-header">
    <div class="h1">Исполненные желания</div>
</header>

<section class="section-card">
    {#if finishedWishes.length === 0}
        <p class="empty-note">
            У вас пока нет исполненных желаний.
        </p>
    {:else}
        <div class="wish-grid">
            {#each finishedWishes as wish (wish.id)}
                <article class="wish-card">
                    <div class="wish-card-image">
                        {#if wish.photo}
                            <img src={wish.photo} alt={wish.name} class="wish-image" />
                        {:else}
                            <img src={iconGift} alt="Подарок" class="wish-image placeholder" />
                        {/if}
                        
                        <!-- Бейдж "Исполнено" -->
                        <div class="finished-badge">Исполнено</div>
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

<div style="padding:0 16px 12px;">
    <Button kind="ghost" full on:click={goBack}>Назад</Button>
</div>

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
        position: relative;
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
    
    .finished-badge {
        position: absolute;
        top: 8px;
        left: 8px;
        background: #059669;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        z-index: 2;
    }
    
    .wish-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    
    .wish-image.placeholder {
        object-fit: contain;
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
        min-height: 63px;
        box-sizing: border-box;
    }
    
    .wish-title {
        font-size: 14px;
        font-weight: 500;
        color: #111827;
        width: 190px;
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