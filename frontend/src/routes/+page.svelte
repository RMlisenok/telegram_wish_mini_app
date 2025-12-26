<script>
    import { onMount } from 'svelte';

    import StartScreen from '$lib/components/screens/StartScreen.svelte';
    import MainScreen from '$lib/components/screens/MainScreen.svelte';
    import ShareProfileScreen from '$lib/components/screens/ShareProfileScreen.svelte';
    import OtherProfileScreen from '$lib/components/screens/OtherProfileScreen.svelte';


    //Dass_18.12.2025 -->
    import SettingsScreen from '$lib/components/screens/settings/SettingsScreen.svelte'; 
    import SettingsScreenEditProfile from '$lib/components/screens/settings/SettingsScreen_EditProfile.svelte';
    import SettingsScreenPrivacySettings from '$lib/components/screens/settings/SettingsScreen_PrivacySettings.svelte';
    import SettingsScreenInterfaceSettings from '$lib/components/screens/settings/SettingsScreen_InterfaceSettings.svelte'; //2002_3_Dass_18.12.2025
    import SettingsScreenLegalInformation from '$lib/components/screens/settings/SettingsScreen_LegalInformation.svelte'; //2002_5_Dass_18.12.2025
    import SettingsScreenNotificationSettings from '$lib/components/screens/settings/SettingsScreen_NotificationSettings.svelte'; //2002_4_Dass_18.12.2025
    //Dass_18.12.2025 <--

    import WishesScreenCreate from '$lib/components/screens/WishesScreen_Create.svelte'; //2005_Dass_21.12.2025
    import WishlistsScreenCreate from '$lib/components/screens/WishlistsScreen_Create.svelte'; //2008/2_Dass_21.12.2025
    import WishlistsScreenEdit from '$lib/components/screens/WishlistsScreen_Edit.svelte'; //2008/3_Dass_22.12.2025
    import WishesScreenEdit from '$lib/components/screens/WishesScreen_Edit.svelte'; //2006/2_Dass_24.12.2025

    import QuestionnaireScreen from '$lib/components/screens/QuestionnaireScreen.svelte';

    import WishesScreen from '$lib/components/screens/WishesScreen.svelte';
    import WishlistsScreen from '$lib/components/screens/WishlistsScreen.svelte'; //2008/1_locust_21.12.2025
    import SubscriptionsScreen from '$lib/components/screens/SubscriptionsScreen.svelte'; //2010/1-5_locust_24.12.2025
    import SubscribersScreen from '$lib/components/screens/SubscribersScreen.svelte'; //2011/1_locust_25.12.2025

    // Lyse Modifications

    import { userStore,otherProfilesMock } from '$lib/stores/data.js';
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();



    let currentScreen = 'start';

    let viewedProfile = null;
    let screenStack = [];

    // user vient du store
    $: user = $userStore;

    function pushNavigate(screen, params = {}) {
        // sauvegarde l'écran actuel pour permettre "retour"
        screenStack = [...screenStack, currentScreen];
        navigate(screen, params);
    }

    function goBack() {
        const prev = screenStack[screenStack.length - 1];
        screenStack = screenStack.slice(0, -1);
        currentScreen = prev ?? 'main';
    }

    function openOtherProfile(profile) {
        viewedProfile = profile;
        pushNavigate('otherProfile');
    }

    // Option si tes screens envoient seulement un id (profileId)
    // et que tu n'as pas encore de store global de profiles

    function openOtherProfileById(profileId) {
        const key = String(profileId);
        viewedProfile = otherProfilesMock[key] ?? {
            id: profileId,
            fullName: '—',
            birthDate: '—',
            avatarUrl: '',
            publicWishlists: [],
            subscriptions: [],
            isSubscribed: false,
            questionnaire: { interests: [], noGifts: [] }
        };
        pushNavigate('otherProfile');
    }




    function navigate(screen, params = {}) {
        currentScreen = screen;
        if (params.wishlistId) {
            currentWishlistId = params.wishlistId;
        } else {
            currentWishlistId = null; // Сбрасываем при переходе на другие экраны
        }
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

    let currentWishlistId = null;
    
    let selectedWishlistId = null;
    let selectedWishId = null; //2006/2_Dass_24.12.2025




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
                            on:openCreateWishlists={() => navigate('wishlistsCreate')}
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
                    <!--   QuestionnaireScreen    -->

                    {:else if currentScreen === 'questionnaire'}
                        <QuestionnaireScreen {user} on:back={() => navigate('main')} />
                    {:else if currentScreen === 'wishes'}
                        <WishesScreen 
                            wishlistId={currentWishlistId}
                            onNavigateToCreateWishes={() => navigate('wishesCreate')} 
                            on:openEditWishes={(e) => {
                                selectedWishId = e.detail.id;
                                navigate('wishesEdit'); 
                                }}
                        />
                    {:else if currentScreen === 'shareProfile'}
                        <ShareProfileScreen {user} on:back={() => navigate('main') }/>
                    <!-- 2005_Dass_21.12.2025 -->
                    {:else if currentScreen === 'wishesCreate'}
                        <WishesScreenCreate
                            onGoBack={() => navigate('wishes')}
                        />
                    <!-- 2006/2_Dass_24.12.2025 -->
                     {:else if currentScreen === 'wishesEdit'}
                        <WishesScreenEdit
                            wishId={selectedWishId}
                            onGoBack={() => {
                                selectedWishId = null;
                                navigate('wishes');
                            }}
                        />
                    <!-- 2008/2_Dass_21.12.2025 -->
                     {:else if currentScreen === 'wishlistsCreate'}
                        <WishlistsScreenCreate
                            onGoBack={() => navigate('wishlists')}
                        />
                    <!-- 2008/1_locust_21.12.2025 -->
                     {:else if currentScreen === 'wishlists'}
                        <WishlistsScreen
                            on:openCreateWishlists={() => navigate('wishlistsCreate')}
                            on:openMainScreen={() => navigate('main')}
                            on:openWishlistDetail={(e) => navigate('wishes', { wishlistId: e.detail.wishlistId })}
                            on:openEditWishlists={(e) => {
                                selectedWishlistId = e.detail.id;
                                navigate('wishlistsEdit'); 
                                }}
                        />
                    <!-- 2008/3_Dass_24.12.2025 -->
                     {:else if currentScreen === 'wishlistsEdit'}
                        <WishlistsScreenEdit
                            wishlistId={selectedWishlistId}
                            onGoBack={() => {
                                selectedWishlistId = null;
                                navigate('wishlists');
                            }}
                        />
                    <!-- 2010/1-5_locust_24.12.2025/ Lyse Modifications -->
                     {:else if currentScreen === 'subscriptions'}
                        <SubscriptionsScreen

                                on:open-profile={(e) => openOtherProfileById(e.detail.profileId)}
                        />
                    <!-- 2011/1_locust_25.12.2025/ Lyse Modifications -->
                     {:else if currentScreen === 'subscribers'}
                        <SubscribersScreen

                                on:open-profile={(e) => openOtherProfileById(e.detail.profileId)}
                        />


                    <!--    OtherProfileScreen       -->

                {:else if currentScreen === 'otherProfile'}

                    <OtherProfileScreen
                            profile={viewedProfile}
                            on:back={goBack}
                            on:toggle-subscribe={(e) => {
    const { profileId, value } = e.detail;

    // 1) Mettre à jour l'objet affiché (sinon l'UI ne change jamais)
    viewedProfile = { ...viewedProfile, isSubscribed: value };

    // 2) (optionnel) Si tu as un mock global, mets-le à jour aussi
    const key = String(profileId);
    if (otherProfilesMock?.[key]) {
      otherProfilesMock[key] = { ...otherProfilesMock[key], isSubscribed: value };
    }

    // 3) (plus tard) ici tu peux appeler ton API/store si besoin
    // await apiToggleSubscribe(profileId, value);
  }}
                            on:show-all-wishlists={() => pushNavigate('wishlists')}
                            on:show-all-subscriptions={() => pushNavigate('subscriptions')}
                    />


                    <!--                    <OtherProfileScreen-->
<!--                            profile={viewedProfile}-->
<!--                            on:back={goBack}-->
<!--                            on:toggle-subscribe={(e) => {-->
<!--            // tu gardes ta logique actuelle (store / api)-->
<!--            console.log('toggle-subscribe', e.detail);-->
<!--        }}-->
<!--                            on:show-all-wishlists={() => pushNavigate('wishlists')}-->
<!--                            on:show-all-subscriptions={() => pushNavigate('subscriptions')}-->
<!--                    />-->



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



                <button on:click={(e) => dispatch('click', e)}>
                    <slot />
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
