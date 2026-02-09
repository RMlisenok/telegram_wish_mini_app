<script>
    import { createEventDispatcher, onMount } from 'svelte';
    import Avatar from '../ui/Avatar.svelte';
    import Button from '../ui/Button.svelte';

    // import {
    //     wishlistsStore,
    //     wishesStore,
    //     subscriptionsStore,
    //     subscribersStore
    // } from '../../stores/data.js';

    import {
        mainWishlistsStore,
        mainSubscriptionsStore,
        mainSubscribersStore,
        totalWishesStore,
        totalWishlistsStore,
        totalSubscribersStore,
        totalSubscriptionsStore,
        loadMainScreenData
    } from '../../../types/mainScreenData.ts';

    import { wishesStore } from '../../stores/data.js';

    export let token;

    export let user;

    const dispatch = createEventDispatcher();

    const openSettings = () => dispatch('openSettings');
    const openQuestionnaire = () => dispatch('openQuestionnaire');
    const openWishes = () => dispatch('openWishes');
    const openWishlists = () => dispatch('openWishlists');
    const openSubscriptions = () => dispatch('openSubscriptions');
    const openSubscribers = () => dispatch('openSubscribers');
    const openShareProfile = () => dispatch('openShareProfile');
    const openCreateWishlists = () => dispatch('openCreateWishlists');

    const ICON_GIFT = '../../../../static/icons/maingift.svg';
    const ICON_ARROW_RIGHT = '../../../../static/icons/arrow-right.png';

    const getInitials = (name) => {
        if (!name) return '??';
        const parts = name.trim().split(' ');
        return parts.slice(0, 2).map((p) => p[0]).join('').toUpperCase();
    };

    $: n_wishes = $totalWishesStore;
    $: n_wishlist = $totalWishlistsStore;
    $: n_sub = $totalSubscriptionsStore;
    $: n_subi = $totalSubscribersStore;

    // $: sortedSubscribers = $subscribersStore
    //     .slice()
    //     .sort((a, b) => {
    //         const parseDate = (dateStr) => {
    //             const [day, month, year] = dateStr.split('.').map(Number);
    //             return new Date(year, month - 1, day);
    //         };
            
    //         return parseDate(b.subscription_date) - parseDate(a.subscription_date);
    //     });

    // $: latestSubscribers = sortedSubscribers.slice(0, 2);

    // const getWishlistCount = (wishlistId) =>
    //     $wishesStore.filter((w) => (w.wishlistIds || []).includes(wishlistId)).length;

    $: latestSubscribers = $mainSubscribersStore
        .slice()
        .sort((a, b) => {
            // Преобразуем даты для сортировки (если есть поле created_at или subscription_date)
            const dateA = a.created_at || a.subscription_date || '';
            const dateB = b.created_at || b.subscription_date || '';
            
            if (!dateA && !dateB) return 0;
            if (!dateA) return 1;
            if (!dateB) return -1;
            
            return new Date(dateB).getTime() - new Date(dateA).getTime();
        })
        .slice(0, 2);

    onMount(async () => {
        if (!token) {
            console.error('Токен не найден');
            return;
        }
        
        try {
            const result = await loadMainScreenData(token);
            console.log('Загруженные totals:', {
                totalWishes: result?.totalWish,
                totalWishlists: result?.totalWishlist,
                totalSubscribers: result?.totalSubscribers,
                totalSubscriptions: result?.totalSubscription
            });
        } catch (error) {
            console.error('Ошибка загрузки данных MainScreen:', error);
        }
    });

</script>



<div class="screen">
    <header class="app-header">
        <div class="h1">Профиль</div>
        <button class="icon-btn" type="button" on:click={openSettings}>
            <img src="../../../../static/icons/tab-settings.png" alt="" />
        </button>
    </header>


    <section class="section-card">
        <div class="profile-row">
            <Avatar size={152} src={user?.avatarUrl || ''} initials={getInitials(user?.fullName)} />
            <div class="profile-main">
                <div class="profile-name">{user.fullName}</div>
                <div class="profile-birth">{user.birthDate}</div>
                <div class="profile-actions">
                    <Button kind="ghost" on:click={openShareProfile}>
                        <img src="../../../../static/icons/share.png" alt="" class="btn-icon" />
                        <span>Поделиться профилем</span>
                    </Button>

                    <Button kind="ghost" on:click={openQuestionnaire}>
                        <img src="../../../../static/icons/edit.png" alt="" class="btn-icon" />
                        <span>Посмотреть анкету</span>
                    </Button>
                </div>
            </div>
        </div>
        <button class="ghost-link" type="button" on:click={openWishes}>
            Все ваши желания ({n_wishes}) 
        </button>
    </section>

    <!-- Вишлисты -->
    <section class="section-card">
        <div class="section-header">
            <div class="h2">Ваши вишлисты ({n_wishlist})</div>
            <button class="tiny-link" type="button" on:click={openWishlists}>
                Показать все
            </button>
        </div>

        {#if $mainWishlistsStore.length === 0}
            <div class="empty-note">
                Здесь появятся ваши вишлисты. Создайте первый, чтобы друзья знали, что вам подарить.
            </div>
        {:else}
            <div class="wishlist-list">
                {#each $mainWishlistsStore.slice(0, 3) as wl}
                    <button class="wishlist-row" type="button" on:click={openWishlists}>
                        <div class="wishlist-cover-small">
                            {#if wl.photo}
                                <img src={wl.photo} alt={wl.name} />
                            {:else}
                                <img src={ICON_GIFT} alt="Подарок"/>
                            {/if}
                        </div>

                        <div class="wishlist-main-small">
                            <div class="wishlist-title-small" title={wl.name}>{wl.name}</div>
                            <div class="wishlist-meta-small">
              <span class="privacy-chip">
                <img
                        class="privacy-icon"
                        src={wl.typeprivacy === 'public'
                    ? '../../../../static/icons/view.png'
                    : '../../../../static/icons/unview.png'}
                        alt=""
                />
                <span>
                  {wl.typeprivacy === 'public'
                      ? 'Виден всем'
                      : wl.typeprivacy === 'restricted'
                          ? 'Для определённых пользователей'
                          : 'Виден только вам'}
                </span>
              </span>
                                <span> · {wl.count} жел.</span>
                            </div>
                        </div>
                        <img 
                            class="wishlist-arrow" 
                            src={ICON_ARROW_RIGHT} 
                            alt="Перейти" 
                        />
                    </button>
                {/each}
            </div>
        {/if}

        <Button full kind="ghost" on:click={openCreateWishlists}>+ Создать вишлист</Button>
    </section>

    <!-- Подписки -->
    <!-- {#if user.showSubscriptions} -->
        <section class="section-card">
            <div class="section-header">
                <div class="h2">Подписки ({n_sub})</div>
                <button class="tiny-link" type="button" on:click={openSubscriptions}>
                    Показать всех
                </button>
            </div>

            {#if $mainSubscriptionsStore.length === 0}
                <div class="empty-note">Вы ещё ни на кого не подписаны.</div>
            {:else}
                <div class="subs-list">
                    {#each $mainSubscriptionsStore.slice(0, 2) as sub}
                        <button
                                type="button"
                                class="subs-row"
                                on:click={openSubscriptions}
                        >
                            {#if sub.type_sub}
                                <!-- Подписка на пользователя -->
                                <Avatar
                                        size={52}
                                        src={sub.user.photo}
                                        initials={getInitials(sub.user.name)}
                                />
                                <div class="subs-main">
                                    <div class="subs-name" title={sub.user.name}>{sub.user.name}</div>
                                    <div class="subs-meta">
                                        <span>{sub.user.birth_date}</span>
                                        {#if sub.wishlist}
                                            <span> · {sub.wishlist.name}</span>
                                        {/if}
                                    </div>
                                </div>
                            {:else}
                            <!-- Подписка на вишлист -->
                            <div class="wishlist-cover-small">
                                {#if sub.wishlist.photo}
                                    <img src={sub.wishlist.photo} alt={sub.wishlist.name} />
                                {:else}
                                    <img src={ICON_GIFT} alt="Подарок"/>
                                {/if}
                            </div>
                            <div class="subs-main">
                                <div class="subs-name" title={sub.wishlist.name}>{sub.wishlist.name}</div>
                                <div class="subs-meta">
                                    <span>{sub.wishlist.owner_name}</span>
                                    {#if sub.wishlist.count}
                                        <span> · {sub.wishlist.count} жел.</span>
                                    {/if}
                                </div>
                            </div>
                        {/if}
                        <img 
                            class="wishlist-arrow" 
                            src={ICON_ARROW_RIGHT} 
                            alt="Перейти" 
                        />
                        </button>
                    {/each}
                </div>
            {/if}
        </section>
    <!-- {/if} -->


    <!-- Подписчики -->
    <section class="section-card">
        <div class="section-header">
            <div class="h2">Подписчики ({n_subi})</div>
            <button class="tiny-link" type="button" on:click={openSubscribers}>
                Показать всех
            </button>
        </div>

        {#if $mainSubscribersStore.length === 0}
            <div class="empty-note">У вас пока нет подписчиков.</div>
        {:else}
            <div class="subs-list">
                {#each latestSubscribers as sub}
                    <button
                            type="button"
                            class="subs-row"
                            on:click={openSubscribers}
                    >
                        <Avatar
                                size={52}
                                src={sub.photo}
                                initials={getInitials(sub.name)}
                        />
                        <div class="subs-main">
                            <div class="subs-name" title={sub.name}>{sub.name}</div>
                            <div class="subs-meta">
                                <span>{sub.birth_date}</span>
                            </div>
                        </div>
                        <img 
                        class="wishlist-arrow" 
                        src={ICON_ARROW_RIGHT} 
                        alt="Перейти" 
                        />
                    </button>
                {/each}
            </div>
        {/if}
    </section>
</div>
<style>


    .icon-btn {
        border: none;
        background: transparent;
        cursor: pointer;
        width: 44px;
        height: 44px;
        padding: 12px;
        margin-right: 4px;
    }

    .icon-btn img {
        width: 20px;
        height: 20px;
        display: block;
    }

    .btn-icon {
        width: 16px;
        height: 16px;
        margin-right: 4px;
    }

    .profile-row {
        display: flex;
        gap: 12px;
        align-items: center;
    }

    .profile-main {
        flex: 1;
    }

    .profile-name {
        font-size: 18px;
        font-weight: 600;
    }

    .profile-birth {
        font-size: 13px;
        color: var(--tg-theme-hint-color, #6b7280);
        margin-top: 2px;
        margin-bottom: 6px;
    }

    .profile-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
    }

    .ghost-link {
        margin-top: 10px;
        padding: 8px 0 0;
        border: none;
        background: transparent;
        color: var(--tg-theme-link-color, #2563eb);
        font-size: 14px;
        cursor: pointer;
    }

    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }

    .tiny-link {
        border: none;
        background: transparent;
        color: var(--tg-theme-link-color, #2563eb);
        font-size: 13px;
        cursor: pointer;
    }

    .wishlist-list {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-bottom: 8px;
    }

    .wishlist-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px;
        width: 100%;
        border-radius: 12px;
        background: var(--tg-theme-secondary-bg-color, #f9fafb);
        border: 1px solid var(--tg-theme-secondary-bg-color, #e5e7eb);
        cursor: pointer;
        text-align: left;
    }


    .wishlist-cover-small {
        width: 52px;
        height: 52px;
        border-radius: 16px;
        background: var(--tg-theme-secondary-bg-color, #f3f4f6);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        overflow: hidden;
    }

    .wishlist-cover-small img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .wishlist-main-small {
        flex: 1;
    }

    .wishlist-title-small {
        font-size: 15px;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: var(--tg-theme-text-color, #111827);
    }

    .wishlist-meta-small {
        font-size: 12px;
        color: var(--tg-theme-hint-color, #6b7280);
        margin-top: 2px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .privacy-chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    .privacy-icon {
        width: 14px;
        height: 14px;
        display: block;
    }

    /* Подписки / Подписчики – тот же стиль, что и у wishlist-row */
    .subs-list {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-bottom: 4px;
    }

    .subs-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px;
        width: 100%;
        border-radius: 12px;
        background: var(--tg-theme-secondary-bg-color, #f9fafb);
        border: 1px solid var(--tg-theme-secondary-bg-color, #e5e7eb);
        cursor: pointer;
        text-align: left;
    }

    .subs-main {
        flex: 1;
    }

    .subs-name {
        font-size: 15px;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: var(--tg-theme-text-color, #111827);
    }

    .subs-meta {
        font-size: 12px;
        color: var(--tg-theme-hint-color, #6b7280);
        margin-top: 2px;
    }

    .wishlist-arrow {
        width: 16px;
        height: 16px;
        opacity: 0.5;
        margin-left: auto;
        flex-shrink: 0;
    }

</style>