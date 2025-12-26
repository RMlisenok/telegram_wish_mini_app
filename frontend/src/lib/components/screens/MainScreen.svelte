<script>
    import { createEventDispatcher } from 'svelte';
    import Avatar from '$lib/components/ui/Avatar.svelte';
    import Button from '$lib/components/ui/Button.svelte';

    import {
        wishlistsStore,
        wishesStore,
        subscriptionsStore,
        subscribersStore
    } from '$lib/stores/data.js';



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

    const ICON_GIFT = '/icons/maingift.svg';
    const ICON_ARROW_RIGHT = '/icons/arrow-right.png';

    const getInitials = (name) => {
        if (!name) return '??';
        const parts = name.trim().split(' ');
        return parts.slice(0, 2).map((p) => p[0]).join('').toUpperCase();
    };

    $: n_wishes = $wishesStore.length;
    $: n_wishlist = $wishlistsStore.length;
    $: n_sub = $subscriptionsStore.length;
    $: n_subi = $subscribersStore.length;

    const getWishlistCount = (wishlistId) =>
        $wishesStore.filter((w) => (w.wishlistIds || []).includes(wishlistId)).length;

</script>



<div class="screen">
    <header class="app-header">
        <div class="h1">Профиль</div>
        <button class="icon-btn" type="button" on:click={openSettings}>
            <img src="/icons/tab-settings.png" alt="" />
        </button>
    </header>


    <section class="section-card">
        <div class="profile-row">
            <Avatar size={152} src={user.avatarUrl} initials={getInitials(user.fullName)} />
            <div class="profile-main">
                <div class="profile-name">{user.fullName}</div>
                <div class="profile-birth">{user.birthDate}</div>
                <div class="profile-actions">
                    <Button kind="ghost" on:click={openShareProfile}>
                        <img src="/icons/share.png" alt="" class="btn-icon" />
                        <span>Поделиться профилем</span>
                    </Button>

                    <Button kind="ghost" on:click={openQuestionnaire}>
                        <img src="/icons/edit.png" alt="" class="btn-icon" />
                        <span>Посмотреть анкету</span>
                    </Button>
                </div>
            </div>
        </div>
        <button class="ghost-link" type="button" on:click={openWishes}>
            Все ваши желания · {n_wishes}
        </button>
    </section>

    <!-- Вишлисты -->
    <section class="section-card">
        <div class="section-header">
            <div class="h2">Ваши вишлисты · {n_wishlist}</div>
            <button class="tiny-link" type="button" on:click={openWishlists}>
                Показать все
            </button>
        </div>

        {#if $wishlistsStore.length === 0}
            <div class="empty-note">
                Здесь появятся ваши вишлисты. Создайте первый, чтобы друзья знали, что вам подарить.
            </div>
        {:else}
            <div class="wishlist-list">
                {#each $wishlistsStore.slice(0, 3) as wl}
                    <button class="wishlist-row" type="button" on:click={openWishlists}>
                        <div class="wishlist-cover-small">
                            {#if wl.coverUrl}
                                <img src={wl.coverUrl} alt={wl.title} />
                            {:else}
                                <img src={ICON_GIFT} alt="Подарок"/>
                            {/if}
                        </div>

                        <div class="wishlist-main-small">
                            <div class="wishlist-title-small" title={wl.title}>{wl.title}</div>
                            <div class="wishlist-meta-small">
              <span class="privacy-chip">
                <img
                        class="privacy-icon"
                        src={wl.privacy === 'public'
                    ? '/icons/view.png'
                    : '/icons/unview.png'}
                        alt=""
                />
                <span>
                  {wl.privacy === 'public'
                      ? 'Виден всем'
                      : wl.privacy === 'restricted'
                          ? 'Для определённых пользователей'
                          : 'Виден только вам'}
                </span>
              </span>
                                <span> · {getWishlistCount(wl.id)} жел.</span>
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
    {#if user.showSubscriptions}
        <section class="section-card">
            <div class="section-header">
                <div class="h2">Подписки · {n_sub}</div>
                <button class="tiny-link" type="button" on:click={openSubscriptions}>
                    Показать всех
                </button>
            </div>

            {#if $subscriptionsStore.length === 0}
                <div class="empty-note">Вы ещё ни на кого не подписаны.</div>
            {:else}
                <div class="subs-list">
                    {#each $subscriptionsStore.slice(0, 2) as sub}
                        <button
                                type="button"
                                class="subs-row"
                                on:click={openSubscriptions}
                        >
                            <Avatar
                                    size={52}
                                    src={sub.avatarUrl}
                                    initials={getInitials(sub.fullName)}
                            />
                            <div class="subs-main">
                                <div class="subs-name" title={sub.fullName}>{sub.fullName}</div>
                                <div class="subs-meta">
                                    <span>{sub.birthDate}</span>
                                    {#if sub.wishlistTitle}
                                        <span> · {sub.wishlistTitle}</span>
                                    {/if}
                                </div>
                            </div>
                        </button>
                    {/each}
                </div>
            {/if}
        </section>
    {/if}


    <!-- Подписчики -->
    <section class="section-card">
        <div class="section-header">
            <div class="h2">Подписчики · {n_subi}</div>
            <button class="tiny-link" type="button" on:click={openSubscribers}>
                Показать всех
            </button>
        </div>

        {#if $subscribersStore.length === 0}
            <div class="empty-note">У вас пока нет подписчиков.</div>
        {:else}
            <div class="subs-list">
                {#each $subscribersStore.slice(0, 2) as sub}
                    <button
                            type="button"
                            class="subs-row"
                            on:click={openSubscribers}
                    >
                        <Avatar
                                size={52}
                                src={sub.avatarUrl}
                                initials={getInitials(sub.fullName)}
                        />
                        <div class="subs-main">
                            <div class="subs-name" title={sub.fullName}>{sub.fullName}</div>
                            <div class="subs-meta">
                                <span>{sub.birthDate}</span>
                                {#if sub.wishlistTitle}
                                    <span> · {sub.wishlistTitle}</span>
                                {/if}
                            </div>
                        </div>
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
        background: #f3f4f6;
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
    }

    .wishlist-meta-small {
        font-size: 12px;
        color: #6b7280;
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
    }

    .subs-meta {
        font-size: 12px;
        color: #6b7280;
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