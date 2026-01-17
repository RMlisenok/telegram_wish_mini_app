<script>
    import { createEventDispatcher } from 'svelte';
    import Avatar from '../ui/Avatar.svelte';
    import Button from '../ui/Button.svelte';

    export let profile;

    const dispatch = createEventDispatcher();

    // IMPORTANT: si "profile" change (quand tu viens de Subscribers/Subscriptions),
    // il faut recalculer isSubscribed.
    $: isSubscribed = !!profile?.isSubscribed;

    $: publicWishlists = profile?.publicWishlists ?? [];
    $: subscriptions = profile?.subscriptions ?? [];

    $: publicWishlistsWithIcon = publicWishlists.filter((wl) => !!wl.iconUrl);

    const goBack = () => dispatch('back');

    const toggleSubscribe = () => {
        dispatch('toggle-subscribe', {
            profileId: profile?.id,
            value: !isSubscribed
        });
    };

    const showAllWishlists = () => {
        dispatch('show-all-wishlists', { profileId: profile?.id });
    };

    const showAllSubscriptions = () => {
        dispatch('show-all-subscriptions', { profileId: profile?.id });
    };

    // Optionnel (si tu veux ouvrir un vishlist depuis ce screen)
    // const openWishlist = (wl) => dispatch('open-wishlist', { wishlistId: wl.id, profileId: profile?.id });
    // const openSubscriptionProfile = (sub) => dispatch('open-profile', { profileId: sub.id });
</script>

<header class="app-header">
    <div class="h1">Профиль</div>
</header>

<section class="section-card profile-card">
    <div class="profile-row">
        <Avatar
                size={152}
                src={profile?.avatarUrl}
                initials={(profile?.fullName ?? '')
        .split(' ')
        .filter(Boolean)
        .map((n) => n[0])
        .join('')
        .toUpperCase()}
        />

        <div class="profile-main">
            <div class="profile-name">{profile?.fullName ?? '—'}</div>
            <div class="profile-birth">{profile?.birthDate ?? '—'}</div>

            <div class="profile-actions">
                <Button kind="ghost" on:click={toggleSubscribe}>
                    <img
                            src={isSubscribed ? '/icons/bell-on.png' : '/icons/bell-off.png'}
                            alt=""
                            class="icon-16"
                            loading="lazy"
                    />
                    <span>{isSubscribed ? 'Вы подписаны' : 'Подписаться'}</span>
                </Button>
            </div>
        </div>
    </div>
</section>

<!-- ВИШЛИСТЫ -->
<section class="section-card">
    <div class="section-header">
        <div class="section-title-with-icon">
            <img src="/icons/gift-check.png" alt="" class="section-icon" loading="lazy" />
            <div class="section-title-main">
                <span>ВИШЛИСТЫ · {publicWishlists.length}</span>

                {#if publicWishlistsWithIcon.length}
                    <div class="mini-icons" aria-label="Иконки вишлистов">
                        {#each publicWishlistsWithIcon.slice(0, 5) as wl (wl.id ?? wl.title)}
<!--                            <div class="mini-icon">-->
<!--                                <img src={wl.iconUrl} alt={wl.title} loading="lazy" />-->
<!--                            </div>-->
                        {/each}
                    </div>
                {/if}
            </div>
        </div>

        <button type="button" class="link-btn" on:click={showAllWishlists}>
            Показать все
        </button>
    </div>

    {#if publicWishlists.length === 0}
        <p class="empty-note">Здесь пока нет публичных вишлистов.</p>
    {:else}
        <div class="wishlists-list">
            {#each publicWishlists as wl (wl.id ?? wl.title)}
                <!-- Si tu veux rendre chaque ligne cliquable: remplace <article> par <button> et dispatch open-wishlist -->
                <article class="wishlist-row">
                    <div class="wishlist-icon">
                        <img
                                src={wl.iconUrl ?? '/icons/gift-check.png'}
                                alt={wl.title}
                                loading="lazy"
                        />
                    </div>
                    <div class="wishlist-main">
                        <div class="wishlist-title">{wl.title}</div>
                        <div class="wishlist-meta">
                            {wl.visibility === 'public' ? 'Виден всем' : 'Доступ ограничен'}
                            {#if typeof wl.wishesCount === 'number'}
                                · {wl.wishesCount} жел.
                            {/if}
                        </div>
                    </div>
                </article>
            {/each}
        </div>
    {/if}
</section>

<!-- ПОДПИСКИ -->
<section class="section-card">
    <div class="section-header">
        <div class="section-title-with-icon">
            <img src="/icons/follow.png" alt="" class="section-icon" loading="lazy" />
            <div class="section-title-main">
                <span>ПОДПИСКИ · {subscriptions.length}</span>

                {#if subscriptions.length}
                    <div class="mini-icons" aria-label="Иконки подписок">
                        {#each subscriptions.slice(0, 5) as sub (sub.id ?? sub.fullName)}
<!--                            <div class="mini-icon">-->
<!--                                <Avatar-->
<!--                                        size={24}-->
<!--                                        src={sub.avatarUrl}-->
<!--                                        initials={(sub.fullName ?? '')-->
<!--                    .split(' ')-->
<!--                    .filter(Boolean)-->
<!--                    .map((n) => n[0])-->
<!--                    .join('')-->
<!--                    .toUpperCase()}-->
<!--                                />-->
<!--                            </div>-->
                        {/each}
                    </div>
                {/if}
            </div>
        </div>

        <button type="button" class="link-btn" on:click={showAllSubscriptions}>
            Показать всех
        </button>
    </div>

    {#if subscriptions.length === 0}
        <p class="empty-note">Этот пользователь пока ни на кого не подписан.</p>
    {:else}
        <div class="subs-list">
            {#each subscriptions as sub (sub.id ?? sub.fullName)}
                <article class="sub-row">
                    <Avatar
                            size={52}
                            src={sub.avatarUrl}
                            initials={(sub.fullName ?? '')
              .split(' ')
              .filter(Boolean)
              .map((n) => n[0])
              .join('')
              .toUpperCase()}
                    />
                    <div class="sub-main">
                        <div class="sub-name">{sub.fullName}</div>
                        <div class="sub-meta">
                            {sub.birthDate ?? '—'}
                            {#if sub.wishlistTitle}
                                · {sub.wishlistTitle}
                            {/if}
                        </div>
                    </div>
                </article>
            {/each}
        </div>
    {/if}
</section>

<!-- ИНТЕРЕСЫ И ЗАПРЕТЫ -->
<section class="section-card">
    <div class="section-header">
        <div class="h2">Интересы и запреты</div>
    </div>

    {#if profile?.questionnaire &&
    ((profile.questionnaire.interests && profile.questionnaire.interests.length) ||
        (profile.questionnaire.noGifts && profile.questionnaire.noGifts.length))}
        {#if profile.questionnaire.interests?.length}
            <div class="q-block">
                <div class="q-label">Что дарить?</div>
                <div class="q-pills">
                    {#each profile.questionnaire.interests as item (item)}
                        <span class="q-pill q-pill--ok">{item}</span>
                    {/each}
                </div>
            </div>
        {/if}

        {#if profile.questionnaire.noGifts?.length}
            <div class="q-block">
                <div class="q-label">Что вам не дарить?</div>
                <div class="q-pills">
                    {#each profile.questionnaire.noGifts as item (item)}
                        <span class="q-pill q-pill--no">{item}</span>
                    {/each}
                </div>
            </div>
        {/if}
    {:else}
        <p class="empty-note">Пользователь ещё не заполнил анкету.</p>
    {/if}
</section>

<div class="footer-actions">
    <Button kind="ghost" full on:click={goBack}>Назад</Button>
</div>

<style>
    .profile-card { margin-bottom: 8px; }

    .profile-row { display: flex; gap: 12px; align-items: center; }
    .profile-main { flex: 1; }
    .profile-name { font-size: 18px; font-weight: 600; }
    .profile-birth { font-size: 13px; color: #6b7280; margin-top: 2px; margin-bottom: 8px; }

    .profile-actions { display: flex; flex-wrap: wrap; gap: 6px; }
    .icon-16 { width: 16px; height: 16px; margin-right: 4px; }

    .section-header { display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 6px; }
    .section-title-with-icon { display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 600; text-transform: uppercase; }
    .section-title-main { display: flex; flex-direction: column; gap: 4px; }
    .section-icon { width: 18px; height: 18px; }

    .link-btn {
        min-width: 44px;
        min-height: 44px;
        padding: 10px 12px;
        border: none;
        background: transparent;
        color: #1d4ed8;
        font-size: 13px;
        cursor: pointer;
    }

    .wishlists-list, .subs-list { display: flex; flex-direction: column; gap: 6px; }

    .wishlist-row, .sub-row {
        display: flex;
        gap: 8px;
        align-items: center;
        padding: 6px 8px;
        border-radius: 12px;
        background: #f9fafb;
        min-height: 44px;
    }

    .wishlist-icon {
        width: 40px; height: 40px;
        border-radius: 14px;
        background: #f3f4f6;
        display: flex; align-items: center; justify-content: center;
        overflow: hidden; flex-shrink: 0;
    }
    .wishlist-icon img { width: 100%; height: 100%; object-fit: contain; }

    .wishlist-main, .sub-main { flex: 1; }
    .wishlist-title, .sub-name { font-size: 14px; font-weight: 500; }
    .wishlist-meta, .sub-meta { font-size: 12px; color: #6b7280; }

    .q-block { margin-bottom: 8px; }
    .q-label { font-size: 13px; font-weight: 600; margin-bottom: 4px; }
    .q-pills { display: flex; flex-wrap: wrap; gap: 6px; }
    .q-pill { font-size: 13px; padding: 4px 8px; border-radius: 999px; background: #f3f4f6; }
    .q-pill--ok { background: #e0f2fe; color: #0369a1; }
    .q-pill--no { background: #fee2e2; color: #b91c1c; }

    .empty-note { color: #6b7280; font-size: 14px; margin: 8px 0; }

    .footer-actions { padding: 0 16px 12px; }
</style>
