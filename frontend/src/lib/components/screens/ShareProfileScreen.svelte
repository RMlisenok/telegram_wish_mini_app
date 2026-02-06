<script>
    import {onMount} from 'svelte';
    import Button from '../ui/Button.svelte';
    import Avatar from '../ui/Avatar.svelte';
    import {createEventDispatcher} from 'svelte';
    import {
        makeProfileTgUrl, 
        makeProfileShareUrl,
        makeWishlistTgUrl,
        makeWishlistShareUrl
    } from '../../stores/data.js';
    import {userStore } from '../../stores/data.js';


    let user = $userStore;

    const dispatch = createEventDispatcher();
    const goBack = () => dispatch('back');

    let tg = null;
    let currentWishlistId = null; // Для копирования ссылки на вишлист
    let currentWishlistName = null;

    onMount(() => {
        if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
            tg = window.Telegram.WebApp;
        }
    });

    const notify = (message) => {
        if (tg?.showPopup) {
            tg.showPopup({
                title: 'Поделиться профилем',
                message,
                buttons: [{type: 'ok', text: 'OK'}]
            });
            return;
        }
        if (tg?.showAlert) {
            tg.showAlert(message);
            return;
        }
        alert(message);
    };

    const copyText = async (text) => {
        try {
            if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(text);
            } else {
                const input = document.createElement('input');
                input.value = text;
                document.body.appendChild(input);
                input.select();
                document.execCommand('copy');
                document.body.removeChild(input);
            }
            return true;
        } catch {
            return false;
        }
    };

    // Копировать ссылку на профиль
    const copyProfileLink = async () => {
        const url = makeProfileTgUrl(user.user_id || user.id);
        const ok = await copyText(url);
        notify(ok ? 'Ссылка на профиль скопирована' : 'Не удалось скопировать ссылку');
    };

    // Копировать ссылку на вишлист
    const copyWishlistLink = async () => {
        if (!currentWishlistId) {
            notify('Выберите вишлист для копирования ссылки');
            return;
        }
        const url = makeWishlistTgUrl(currentWishlistId);
        const ok = await copyText(url);
        const wishlistName = currentWishlistName || 'вишлист';
        notify(ok ? `Ссылка на ${wishlistName} скопирована` : 'Не удалось скопировать ссылку');
    };

    // Поделиться профилем в Telegram
    const shareProfileInTelegram = () => {
        const shareUrl = makeProfileShareUrl(user.user_id || user.id, user.fullName); // share wrapper

        if (tg?.openTelegramLink) tg.openTelegramLink(shareUrl);
        else if (tg?.openLink) tg.openLink(shareUrl);
        else window.open(shareUrl, '_blank');
    };

    // Поделиться вишлистом в Telegram
    const shareWishlistInTelegram = () => {
        if (!currentWishlistId) {
            notify('Выберите вишлист для отправки');
            return;
        }
        const shareUrl = makeWishlistShareUrl(currentWishlistId, currentWishlistName || '');
        if (tg?.openTelegramLink) tg.openTelegramLink(shareUrl);
        else if (tg?.openLink) tg.openLink(shareUrl);
        else window.open(shareUrl, '_blank');
    };

    const shareProfileOtherWays = async () => {
        const url = makeProfileTgUrl(user.id);
        const title = 'Подари мне — профиль';
        const text = `Профиль: ${user.fullName}`;

        if (navigator.share) {
            try {
                await navigator.share({title, text, url});
                notify('Готово');
                return;
            } catch {
                return;
            }
        }
        await copyLink();
    };

    const shareWishlistOtherWays = async () => {
        if (!currentWishlistId) {
            notify('Выберите вишлист');
            return;
        }
        
        const url = makeWishlistTgUrl(currentWishlistId);
        const title = 'Подари мне — вишлист';
        const text = `Вишлист: ${currentWishlistName || ''}`;

        if (navigator.share) {
            try {
                await navigator.share({title, text, url});
                notify('Готово');
                return;
            } catch {
                return;
            }
        }
        await copyWishlistLink();
    };

    export function selectWishlist(wishlistId, wishlistName) {
        currentWishlistId = wishlistId;
        currentWishlistName = wishlistName;
    };

</script>

<header class="app-header">
    <div class="h1">Поделиться профилем</div>
</header>

<section class="section-card">
    <!-- Выбор типа для публикации -->
    <div class="share-type-selector">
        <button class="share-type-btn active">Профиль</button>
        <button class="share-type-btn">Вишлист</button>
    </div>

    <div class="share-header">
        <Avatar
            size={56}
            src={user.avatarUrl}
            initials={user.fullName.split(' ').map((n) => n[0]).join('').toUpperCase()}
        />
        <div class="share-main">
            <div class="share-name">{user.fullName}</div>
            <div class="share-id">ID: {user.user_id || user.id}</div>
        </div>
    </div>

    <!-- Выбор вишлиста (только если выбрана опция вишлиста) -->
    <div class="wishlist-selector" style="display: none;">
        <select class="wishlist-select">
            <option value="">Выберите вишлист</option>
            <!-- Здесь будут загружаться вишлисты пользователя -->
        </select>
    </div>

    <p class="share-text">
        Отправьте ссылку, чтобы друзья могли видеть ваши желания и вишлисты.
    </p>

    <div style="height:8px;"></div>

    <Button full kind="ghost" on:click={shareProfileInTelegram}>
        Поделиться в Telegram
    </Button>

    <div style="height:8px;"></div>

    <Button full kind="ghost" on:click={copyProfileLink}>
        Скопировать ссылку
    </Button>

    <div style="height:8px;"></div>

    <Button full kind="ghost" on:click={shareProfileOtherWays}>
        Другие способы
    </Button>

    <div style="height:8px;"></div>

    <Button kind="primary" full on:click={goBack}>
        Вернуться в профиль
    </Button>
</section>

<style>
    .share-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
    }

    .share-main {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .share-name {
        font-size: 16px;
        font-weight: 600;
    }

    .share-id {
        font-size: 12px;
        color: #6b7280;
    }

    .share-text {
        font-size: 14px;
        color: #4b5563;
        margin-bottom: 16px;
    }

    .share-type-selector {
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
    }

    .share-type-btn {
        flex: 1;
        padding: 8px 16px;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        background: white;
        font-size: 14px;
        cursor: pointer;
    }

    .share-type-btn.active {
        background: #3b82f6;
        color: white;
        border-color: #3b82f6;
    }

    .wishlist-selector {
        margin-bottom: 16px;
    }

    .wishlist-select {
        width: 100%;
        padding: 8px 12px;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        font-size: 14px;
    }
</style>
