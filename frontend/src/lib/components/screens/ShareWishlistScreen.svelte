<script>
    import { onMount } from 'svelte';
    import Button from '../ui/Button.svelte';
    import Avatar from '../ui/Avatar.svelte';
    import { createEventDispatcher } from 'svelte';
    import { makeWishlistTgUrl, makeWishlistShareUrl } from '../../stores/data.js';

    export let wishlist;
    export let user;

    const dispatch = createEventDispatcher();
    
    const goBack = () => {
        dispatch('back');
    };

    let tg = null;

    onMount(() => {
        if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
            tg = window.Telegram.WebApp;
        }
    });

    const notify = (message) => {
        if (tg?.showPopup) {
            tg.showPopup({
                title: 'Поделиться вишлистом',
                message,
                buttons: [{ type: 'ok', text: 'OK' }]
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

    const copyLink = async () => {
        const url = makeWishlistTgUrl(wishlist.id);
        const ok = await copyText(url);
        notify(ok ? 'Ссылка на вишлист скопирована' : 'Не удалось скопировать ссылку');
    };

    const shareInTelegram = () => {
        const shareUrl = makeWishlistShareUrl(wishlist.id, wishlist.title);
        if (tg?.openTelegramLink) tg.openTelegramLink(shareUrl);
        else if (tg?.openLink) tg.openLink(shareUrl);
        else window.open(shareUrl, '_blank');
    };

    const shareOtherWays = async () => {
        const url = makeWishlistTgUrl(wishlist.id);
        const title = 'Подари мне — вишлист';
        const text = `Вишлист: ${wishlist.title}`;

        if (navigator.share) {
            try {
                await navigator.share({ title, text, url });
                notify('Готово');
                return;
            } catch {
                return;
            }
        }
        await copyLink();
    };

    // Функция для получения инициалов владельца
    function getOwnerInitials() {
        if (wishlist.ownerName) {
            return wishlist.ownerName.split(' ').map((n) => n[0]).join('').toUpperCase();
        }
        if (user?.fullName) {
            return user.fullName.split(' ').map((n) => n[0]).join('').toUpperCase();
        }
        return '?';
    }

    // Функция для получения URL аватара владельца
    function getOwnerAvatarUrl() {
        if (wishlist.ownerAvatar) {
            return wishlist.ownerAvatar;
        }
        if (user?.avatarUrl) {
            return user.avatarUrl;
        }
        return '';
    }

    // Функция для получения имени владельца
    function getOwnerName() {
        if (wishlist.ownerName) {
            return wishlist.ownerName;
        }
        if (user?.fullName) {
            return user.fullName;
        }
        return 'Владелец';
    }

    // Функция для определения типа вишлиста
    function getWishlistTypeText() {
        switch (wishlist.typeprivacy) {
            case 'public':
                return 'Публичный';
            case 'restricted':
                return 'Ограниченный';
            case 'private':
                return 'Приватный';
            default:
                return 'Приватный';
        }
    }

    // Функция для определения, чей это вишлист
    function getWishlistOwnerText() {
        if (wishlist.isExternalWishlist && !wishlist.isCurrentUserOwner) {
            return `Вишлист ${getOwnerName()}`;
        } else {
            return 'Ваш вишлист';
        }
    }
</script>

<header class="app-header">
    <div class="h1">Поделиться вишлистом</div>
</header>

<section class="section-card">
    <div class="share-header">
        {#if wishlist.photo}
            <div class="wishlist-icon-container">
                <img 
                    src={wishlist.photo} 
                    alt={wishlist.title}
                    class="wishlist-icon"
                />
            </div>
        {:else}
            <div class="wishlist-placeholder">
                {(wishlist.title?.[0]?.toUpperCase() || 'W')}
            </div>
        {/if}
        
        <div class="share-main">
            <div class="share-name">{wishlist.title}</div>
            
            <div class="share-owner">
                <Avatar
                    size={20}
                    src={getOwnerAvatarUrl()}
                    initials={getOwnerInitials()}
                    style="margin-right: 6px; display: inline-block; vertical-align: middle;"
                />
                <span style="vertical-align: middle; font-size: 14px; color: #6b7280;">
                    {getWishlistOwnerText()}
                </span>
            </div>
            
            <div class="share-info">
                {#if wishlist.wishesCount !== undefined || wishlist.count !== undefined}
                    <span class="share-count">
                        Желаний: {wishlist.wishesCount || wishlist.count || 0}
                    </span>
                    <span style="margin: 0 4px; color: #d1d5db;">•</span>
                {/if}
                <span class="share-type">
                    {getWishlistTypeText()}
                </span>
            </div>
        </div>
    </div>

    <p class="share-text">
        {#if wishlist.isExternalWishlist && !wishlist.isCurrentUserOwner}
            Отправьте ссылку на этот вишлист, чтобы другие могли видеть желания и выбирать подарки.
        {:else}
            Отправьте ссылку на этот вишлист, чтобы друзья могли видеть ваши желания и выбирать подарки.
        {/if}
    </p>

    <div style="height: 8px;"></div>

    <Button full kind="ghost" on:click={shareInTelegram}>
        Поделиться в Telegram
    </Button>

    <div style="height: 8px;"></div>

    <Button full kind="ghost" on:click={copyLink}>
        Скопировать ссылку
    </Button>

    <div style="height: 8px;"></div>

    <Button full kind="ghost" on:click={shareOtherWays}>
        Другие способы
    </Button>

    <div style="height: 8px;"></div>

    <Button kind="primary" full on:click={goBack}>
        Вернуться к вишлисту
    </Button>
</section>

<style>
    .share-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    }

    .share-main {
        display: flex;
        flex-direction: column;
        gap: 4px;
        flex: 1;
    }

    .share-name {
        font-size: 18px;
        font-weight: 600;
        line-height: 1.3;
        word-break: break-word;
    }

    .share-owner {
        display: flex;
        align-items: center;
        font-size: 14px;
        color: #6b7280;
    }

    .share-info {
        display: flex;
        align-items: center;
        font-size: 13px;
        color: #9ca3af;
        flex-wrap: wrap;
    }

    .share-count {
        font-size: 13px;
        color: #9ca3af;
    }

    .share-type {
        font-size: 13px;
        color: #9ca3af;
    }

    .share-text {
        font-size: 14px;
        color: #4b5563;
        line-height: 1.5;
        margin-bottom: 20px;
    }

    .wishlist-icon {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        object-fit: cover;
        background-color: #f3f4f6;
    }

    .wishlist-placeholder {
        width: 56px;
        height: 56px;
        min-width: 56px;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 20px;
    }

    .app-header {
        position: sticky;
        top: 0;
        z-index: 100;
        background: white;
        padding: 16px;
        border-bottom: 1px solid #e5e7eb;
    }

    .h1 {
        font-size: 20px;
        font-weight: 600;
        line-height: 1.2;
    }
</style>