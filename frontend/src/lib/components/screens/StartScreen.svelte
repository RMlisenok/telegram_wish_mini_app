<script>
    import { createEventDispatcher } from 'svelte';
    import Button from '../ui/Button.svelte';
    // import StartGiftIcon from '/static/icons/gift.svg';
    const dispatch = createEventDispatcher();

    const handleStart = () => {
        dispatch('start'); // l’événement que +page.svelte écoute
    };
</script>

<div class="start-root">
    <div class="start-content">
        <img src="../../../../static/icons/gift.svg" alt="Подарок" class="gift-img" />
                <!-- <img src={StartGiftIcon} alt="Подарок" class="gift-img" /> -->

        <h1 class="title">Подари мне</h1>
        <p class="subtitle">Делись желаниями и дари подарки друзьям!</p>

        <Button class="start-btn" on:click={handleStart}>Начать</Button>
    </div>
</div>

<style>
    .start-root {
        min-height: 100vh;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        background: #ffffff;
    }

    .start-content {
        width: 100%;
        max-width: 430px;
        text-align: center;
        padding: 24px;
    }

    .gift-img {
        width: 140px;
        height: 140px;
        margin-bottom: 28px;
    }

    .title {
        margin: 0 0 8px;
        font-size: 28px;
        font-weight: 700;
        color: #111827;
    }

    .subtitle {
        margin: 0 0 32px;
        font-size: 15px;
        color: #6b7280;
    }


</style>
