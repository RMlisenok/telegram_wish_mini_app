<script>
    import {onMount} from 'svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import Avatar from '$lib/components/ui/Avatar.svelte';
    import {createEventDispatcher} from 'svelte';
    import {makeProfileTgUrl, makeProfileShareUrl} from '$lib/stores/data.js';
    import {userStore } from '$lib/stores/data.js';


    let user = $userStore;

    const dispatch = createEventDispatcher();
    const goBack = () => dispatch('back');

    let tg = null;

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

    const copyLink = async () => {
        const url = makeProfileTgUrl(user.id); // lien carte
        const ok = await copyText(url);
        notify(ok ? 'Ссылка на профиль скопирована' : 'Не удалось скопировать ссылку');
    };

    const shareInTelegram = () => {
        const shareUrl = makeProfileShareUrl(user.id, user.fullName); // share wrapper

        if (tg?.openTelegramLink) tg.openTelegramLink(shareUrl);
        else if (tg?.openLink) tg.openLink(shareUrl);
        else window.open(shareUrl, '_blank');
    };


    const shareOtherWays = async () => {
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


</script>

<header class="app-header">
    <div class="h1">Поделиться профилем</div>
</header>

<section class="section-card">
    <div class="share-header">
        <Avatar
                size={56}
                src={user.avatarUrl}
                initials={user.fullName.split(' ').map((n) => n[0]).join('').toUpperCase()}
        />
        <div class="share-main">
            <div class="share-name">{user.fullName}</div>
            <div class="share-id">ID: {user.id}</div>
        </div>
    </div>

    <p class="share-text">
        Отправьте ссылку на свой профиль, чтобы друзья могли видеть ваши желания и вишлисты.
    </p>


    <div style="height:8px;"></div>

    <Button full kind="ghost" on:click={shareInTelegram}>
        Поделиться в Telegram
    </Button>

    <div style="height:8px;"></div>

    <Button full kind="ghost" on:click={copyLink}>
        Скопировать ссылку
    </Button>

    <div style="height:8px;"></div>

    <Button full kind="ghost" on:click={shareOtherWays}>
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
</style>
