<script>
    import { onMount } from 'svelte';

    import StartScreen from '$lib/components/screens/StartScreen.svelte';
    import MainScreen from '$lib/components/screens/MainScreen.svelte';
    
    //Dass_18.12.2025 -->
    import SettingsScreen from '$lib/components/screens/settings/SettingsScreen.svelte'; 
    import SettingsScreenEditProfile from '$lib/components/screens/settings/SettingsScreen_EditProfile.svelte';
    import SettingsScreenPrivacySettings from '$lib/components/screens/settings/SettingsScreen_PrivacySettings.svelte';
    import SettingsScreenInterfaceSettings from '$lib/components/screens/settings/SettingsScreen_InterfaceSettings.svelte'; //2002_3_Dass_18.12.2025
    import SettingsScreenLegalInformation from '$lib/components/screens/settings/SettingsScreen_LegalInformation.svelte'; //2002_5_Dass_18.12.2025
    import SettingsScreenNotificationSettings from '$lib/components/screens/settings/SettingsScreen_NotificationSettings.svelte'; //2002_4_Dass_18.12.2025
    //Dass_18.12.2025 <--

    import { userStore } from '$lib/stores/data.js';

    let currentScreen = 'start';
    // let viewedProfile = null;

    // user vient du store
    $: user = $userStore;

    function navigate(screen) {
        currentScreen = screen;
    }

    function applyTheme() {
        const theme = $userStore.ui.theme || 'system';
        let effectiveTheme = theme;
        
        if (theme === 'system') {
            effectiveTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        document.documentElement.setAttribute('data-theme', effectiveTheme);
        document.documentElement.setAttribute('theme-preference', theme);
    }

    onMount(() => {
        if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();
        }

        applyTheme();
        
        // Слушаем изменения системной темы
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleSystemThemeChange = () => {
            if ($userStore.ui.theme === 'system') {
                applyTheme();
            }
        };
        mediaQuery.addEventListener('change', handleSystemThemeChange);
        
        // Подписываемся на изменения store для темы
        const unsubscribe = userStore.subscribe(() => {
            applyTheme();
        });
        
        return () => {
            unsubscribe();
            mediaQuery.removeEventListener('change', handleSystemThemeChange);
        };
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
           <!--<div class="app-root {user.ui.theme} {user.ui.textSize}"> -->
            <div class="app-root {$userStore.ui.theme} {$userStore.ui.textSize}">
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
                <!-- Dass_18.12.2025 add SettingsScreen-->
                    {:else if currentScreen === 'settings'}
                    <SettingsScreen
                        onGoBack={() => navigate('main')}
                        onNavigateToEditProfile={() => navigate('editProfile')}
                        onNavigateToPrivacySettings={() => navigate('privacySettings')}
                        onNavigateToInterfaceSettings={() => navigate('interfaceSettings')}
                        onNavigateToLegalInformation={() => navigate('legalInformation')}
                        onNavigateToNotificationSettings={() => navigate('notifficationSettings')} 
                    />
                <!-- Dass_18.12.2025 add EditProfile-->
                    {:else if currentScreen === 'editProfile'}
                    <SettingsScreenEditProfile
                        onGoBack={() => navigate('settings')}
                    />
                <!-- 2002_2_Dass_18.12.2025 add PrivacySettings-->
                    {:else if currentScreen === 'privacySettings'}
                    <SettingsScreenPrivacySettings 
                        onGoBack={() => navigate('settings')}
                    />
                <!-- 2002_3_Dass_18.12.2025 add interfaceSettings-->
                    {:else if currentScreen === 'interfaceSettings'}
                    <SettingsScreenInterfaceSettings
                        onGoBack={() => navigate('settings')}   
                    />
                <!-- 2002_5_Dass_18.12.2025 add legalInformation-->
                    {:else if currentScreen === 'legalInformation'}
                    <SettingsScreenLegalInformation
                        onGoBack={() => navigate('settings')}
                    />
                <!-- 2002_4_Dass_20.12.2025 add notificationSettings-->
                    {:else if currentScreen === 'notifficationSettings'}
                    <SettingsScreenNotificationSettings
                        onGoBack={() => navigate('settings')}
                    />
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

    .app-root.small,
    .app-root.small * {
        font-size: 14px !important;
    }
    
    .app-root.medium,
    .app-root.medium * {
        font-size: 16px !important;
    }
    
    .app-root.large,
    .app-root.large * {
        font-size: 18px !important;
    }
    
    /* элементы, которые не должны масштабироваться */
    .app-root.small img,
    .app-root.medium img,
    .app-root.large img {
        font-size: initial !important;
    }
    
    /* Для иконок и других фиксированных элементов */
    .tab-icon {
        width: 24px !important;
        height: 24px !important;
    }

</style>
