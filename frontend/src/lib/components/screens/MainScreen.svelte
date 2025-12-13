<script>
    import Avatar from '$lib/components/ui/Avatar.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import { createEventDispatcher } from 'svelte';



    export let user;

    const dispatch = createEventDispatcher();

    const openSettings = () => dispatch('openSettings');
    const openQuestionnaire = () => dispatch('openQuestionnaire');
    const openWishes = () => dispatch('openWishes');
    const openShareProfile = () => dispatch('openShareProfile');


    const getInitials = (name) => {
        if (!name) return '??';
        const parts = name.trim().split(' ');
        return parts.slice(0, 2).map((p) => p[0]).join('').toUpperCase();
    };


    $: n_wishes = 0;



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
        <Avatar size={72} src={user.avatarUrl} initials={getInitials(user.fullName)} />
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

</div>


<style>


.icon-btn {
    border: none;
    background: transparent;
    cursor: pointer;
    padding: 4px;
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

    .wishlist-cover-small img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }



</style>