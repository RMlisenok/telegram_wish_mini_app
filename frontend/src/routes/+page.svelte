<script>
    import { onMount } from 'svelte';

    import StartScreen from '$lib/components/screens/StartScreen.svelte';
    import MainScreen from '$lib/components/screens/MainScreen.svelte';
    import QuestionnaireScreen from '$lib/components/screens/QuestionnaireScreen.svelte';
    import ShareProfileScreen from '$lib/components/screens/ShareProfileScreen.svelte';

    import { userStore } from '$lib/stores/data.js';

    let currentScreen = 'start';
    // let viewedProfile = null;

    // user vient du store
    $: user = $userStore;

    function navigate(screen) {
        currentScreen = screen;
    }

    onMount(() => {
        if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();
        }
    });


</script>

{#if !user}
    <!-- Si jamais le user n'est pas encore chargé -->
    <div class="app-root light medium">
        Загрузка...
    </div>
{:else}
    {#if currentScreen === 'start'}
        <div class="app-root {user.ui.theme} {user.ui.textSize}">
            <StartScreen on:start={() => navigate('main')} />
        </div>
    {:else}
           <div class="app-root {user.ui.theme} {user.ui.textSize}">

          <!--  Mainscreen -->

            <div class="app-scroll">
                {#if currentScreen === 'main'}
                    <MainScreen
                            {user}
                            on:openSettings={() => navigate('settings')}
                            on:openQuestionnaire={() => navigate('questionnaire')}
                            on:openWishes={() => navigate('wishes')}
                            on:openWishlists={() => navigate('wishlists')}
                            on:openSubscriptions={() => navigate('subscriptions')}
                            on:openSubscribers={() => navigate('subscribers')}
                            on:openShareProfile={() => navigate('shareProfile')}
                    />

                       <!--   QuestionnaireScreen    -->

                {:else if currentScreen === 'questionnaire'}
                    <QuestionnaireScreen {user} on:back={() => navigate('main')} />

                       <!--   ShareProfileScreen    -->

                {:else if currentScreen === 'shareProfile'}
                    <ShareProfileScreen {user} on:back={() => navigate('main')} />



                    {/if}
                </div>


            <!-- TAB BAR -->
            <nav class="tab-bar">
                <button
                        type="button"
                        class={`tab-item ${currentScreen === 'main' ? 'active' : ''}`}
                        on:click={() => navigate('main')}
                >
                    <img class="tab-icon" src="/icons/tab-home.png" alt="" />
                    <span>Главная</span>
                    <span class="tab-dot"></span>
                </button>

                <button
                        type="button"
                        class={`tab-item ${currentScreen === 'wishes' ? 'active' : ''}`}
                        on:click={() => navigate('wishes')}
                >
                    <img class="tab-icon" src="/icons/tab-gift.png" alt="" />
                    <span>Желания</span>
                    <span class="tab-dot"></span>
                </button>

                <button
                        type="button"
                        class={`tab-item ${currentScreen === 'wishlists' ? 'active' : ''}`}
                        on:click={() => navigate('wishlists')}
                >
                    <img class="tab-icon" src="/icons/tab-list.png" alt="" />
                    <span>Вишлисты</span>
                    <span class="tab-dot"></span>
                </button>

                <button
                        type="button"
                        class={`tab-item ${currentScreen === 'subscriptions' ? 'active' : ''}`}
                        on:click={() => navigate('subscriptions')}
                >
                    <img class="tab-icon" src="/icons/tab-eye.png" alt="" />
                    <span>Подписки</span>
                    <span class="tab-dot"></span>
                </button>

                <button
                        type="button"
                        class={`tab-item ${currentScreen === 'settings' ? 'active' : ''}`}
                        on:click={() => navigate('settings')}
                >
                    <img class="tab-icon" src="/icons/tab-settings.png" alt="" />
                    <span>Настройки</span>
                    <span class="tab-dot"></span>
                </button>
            </nav>
        </div>
    {/if}
{/if}

<style>

</style>
