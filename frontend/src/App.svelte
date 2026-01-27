<script lang="ts">
    import { onMount } from 'svelte';
    import { initializeTelegram, user, telegram } from './lib/telegram';
    import StartScreen from './lib/components/screens/StartScreen.svelte'; // Импортируем стартовый экран

    // Импорты экранов
    import MainScreen from './lib/components/screens/MainScreen.svelte';
    import ShareProfileScreen from './lib/components/screens/ShareProfileScreen.svelte';
    import OtherProfileScreen from './lib/components/screens/OtherProfileScreen.svelte';
    
    import SettingsScreen from './lib/components/screens/settings/SettingsScreen.svelte'; 
    import SettingsScreenEditProfile from './lib/components/screens/settings/SettingsScreen_EditProfile.svelte';
    import SettingsScreenPrivacySettings from './lib/components/screens/settings/SettingsScreen_PrivacySettings.svelte';
    import SettingsScreenInterfaceSettings from './lib/components/screens/settings/SettingsScreen_InterfaceSettings.svelte';
    import SettingsScreenLegalInformation from './lib/components/screens/settings/SettingsScreen_LegalInformation.svelte';
    import SettingsScreenNotificationSettings from './lib/components/screens/settings/SettingsScreen_NotificationSettings.svelte';
    
    import WishesScreenCreate from './lib/components/screens/WishesScreen_Create.svelte';
    import WishlistsScreenCreate from './lib/components/screens/WishlistsScreen_Create.svelte';
    import WishlistsScreenEdit from './lib/components/screens/WishlistsScreen_Edit.svelte';
    import WishesScreenEdit from './lib/components/screens/WishesScreen_Edit.svelte';
    
    import QuestionnaireScreen from './lib/components/screens/QuestionnaireScreen.svelte';
    import WishesScreen from './lib/components/screens/WishesScreen.svelte';
    import WishlistsScreen from './lib/components/screens/WishlistsScreen.svelte';
    import SubscriptionsScreen from './lib/components/screens/SubscriptionsScreen.svelte';
    import SubscribersScreen from './lib/components/screens/SubscribersScreen.svelte';
    import type { User } from './types/user';
    import { writable } from 'svelte/store';

    // Импорты stores (нужно будет создать или импортировать)
    import { otherProfilesMock } from './lib/stores/data';

    let currentScreen = 'start';
    let viewedProfile = null;
    let screenStack = [];
    
    let currentWishlistId = null;
    let selectedWishlistId = null;
    let selectedWishId = null;
    
    let showStartScreen = true; // Состояние для отображения стартового экрана
    let tg = null;
    let token = null; //токен важно!
    //let userStore = null;
    
    onMount(() => {
        tg = initializeTelegram();
        
        if (!tg) {
            console.warn('Приложение запущено вне Telegram');
            // Можно показать заглушку для браузера
        }
    });
    
    // Навигация
    function pushNavigate(screen, params = {}) {
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
            currentWishlistId = null;
        }
    }
    export const userStore = writable<User>({
        id: '',
        fullName: '',
        birthDate: new Date(),
        avatarUrl: '',
        showSubscriptions: true,
        ui: {
            textSize: 'medium',
            theme: 'system'
        }
    });

    // Обработчик начала работы
    const handleStart = async () => {
        showStartScreen = false;
        
        const response = await fetch('/api/v1/auth/telegram', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ initData: tg.initData, user: tg.initDataUnsafe.user })
                });
        const data = await response.json();
        if (data.token) {
            token = data.token;
            console.log('Получен токен:', token);
        }
        const user = data.user;
        if (user.birth_date != null)
        {
            navigate('main');
        }
        else
        {
            navigate('editProfile');
        }
        userStore.set({
            id: token || 'demo-user-1',
            fullName: user.name  || 'Гость',
            birthDate: formatDateToDDMMYYYY(user.birth_date),
            avatarUrl: user.photo || '/default-avatar.png',
            showSubscriptions: user.show_sub ?? true,
            ui: {
                textSize: (user.text_size as 'small' | 'medium' | 'large') || 'medium',
                theme: (user.theme as 'light' | 'dark' | 'system') || 'system'
            }
        });
        console.log(userStore);
    };
    function formatDateToDDMMYYYY(dateString: string): string {
        if (!dateString) return '';
        
        const [year, month, day] = dateString.split('-');
        if (!year || !month || !day) return dateString; 
        
        return `${day}.${month}.${year}`;
    }
</script>

<main>
    {#if showStartScreen}
        <!-- Показываем стартовый экран -->
        <StartScreen on:start={handleStart} />
    {:else if $user && !showStartScreen}
        <div class="app-root {$userStore.ui?.theme || 'light'} {$userStore.ui?.textSize || 'medium'}">
            {#if currentScreen === 'start'}
                <div class="app-scroll">
                    <StartScreen on:start={handleStart} />
                </div>
            {:else}
                <div class="app-scroll">
                    {#if currentScreen === 'main'}
                        <MainScreen
                            token={token}
                            user={$userStore}
                            on:openSettings={() => navigate('settings')}
                            on:openQuestionnaire={() => navigate('questionnaire')}
                            on:openWishes={() => navigate('wishes')}
                            on:openWishlists={() => navigate('wishlists')}
                            on:openSubscriptions={() => navigate('subscriptions')}
                            on:openSubscribers={() => navigate('subscribers')}
                            on:openShareProfile={() => navigate('shareProfile')}
                            on:openCreateWishlists={() => navigate('wishlistsCreate')}
                        />
                    
                    {:else if currentScreen === 'settings'}
                        <SettingsScreen
                            onGoBack={() => navigate('main')}
                            onNavigateToEditProfile={() => navigate('editProfile')}
                            onNavigateToPrivacySettings={() => navigate('privacySettings')}
                            onNavigateToInterfaceSettings={() => navigate('interfaceSettings')}
                            onNavigateToLegalInformation={() => navigate('legalInformation')}
                            onNavigateToNotificationSettings={() => navigate('notifficationSettings')} 
                        />
                    
                    {:else if currentScreen === 'editProfile'}
                        <SettingsScreenEditProfile
                            token={token}
                            userStore={$userStore}
                            onGoBack={() => navigate('settings')}
                            on:profileUpdated={(e) => {
                                userStore.update(current => ({
                                    ...current,
                                    ...e.detail
                                }));
                            }}
                        />
                    
                    {:else if currentScreen === 'privacySettings'}
                        <SettingsScreenPrivacySettings 
                            onGoBack={() => navigate('settings')}
                        />
                    
                    {:else if currentScreen === 'interfaceSettings'}
                        <SettingsScreenInterfaceSettings
                            onGoBack={() => navigate('settings')}   
                        />
                    
                    {:else if currentScreen === 'legalInformation'}
                        <SettingsScreenLegalInformation
                            onGoBack={() => navigate('settings')}
                        />
                    
                    {:else if currentScreen === 'notifficationSettings'}
                        <SettingsScreenNotificationSettings
                            onGoBack={() => navigate('settings')}
                        />
                    
                    {:else if currentScreen === 'questionnaire'}
                        <QuestionnaireScreen 
                            user={$userStore} 
                            on:back={() => navigate('main')} 
                        />
                    
                    {:else if currentScreen === 'wishes'}
                        <WishesScreen 
                            token={token}
                            wishlistId={currentWishlistId}
                            onNavigateToCreateWishes={() => navigate('wishesCreate')} 
                            on:openEditWishes={(e) => {
                                selectedWishId = e.detail.id;
                                navigate('wishesEdit'); 
                            }}
                        />
                    
                    {:else if currentScreen === 'shareProfile'}
                        <ShareProfileScreen 
                            user={$userStore} 
                            on:back={() => navigate('main')}
                        />
                    
                    {:else if currentScreen === 'wishesCreate'}
                        <WishesScreenCreate
                            onGoBack={() => navigate('wishes')}
                        />
                    
                    {:else if currentScreen === 'wishesEdit'}
                        <WishesScreenEdit
                            wishId={selectedWishId}
                            onGoBack={() => {
                                selectedWishId = null;
                                navigate('wishes');
                            }}
                        />
                    
                    {:else if currentScreen === 'wishlistsCreate'}
                        <WishlistsScreenCreate
                            token={token}
                            onGoBack={() => navigate('wishlists')}
                        />
                    
                    {:else if currentScreen === 'wishlists'}
                        <WishlistsScreen
                            token={token}
                            on:openCreateWishlists={() => navigate('wishlistsCreate')}
                            on:openMainScreen={() => navigate('main')}
                            on:openWishlistDetail={(e) => navigate('wishes', { wishlistId: e.detail.wishlistId })}
                            on:openEditWishlists={(e) => {
                                selectedWishlistId = e.detail.id;
                                navigate('wishlistsEdit'); 
                            }}
                        />
                    
                    {:else if currentScreen === 'wishlistsEdit'}
                        <WishlistsScreenEdit
                            wishlistId={selectedWishlistId}
                            onGoBack={() => {
                                selectedWishlistId = null;
                                navigate('wishlists');
                            }}
                        />
                    
                    {:else if currentScreen === 'subscriptions'}
                        <SubscriptionsScreen
                            on:open-profile={(e) => openOtherProfileById(e.detail.profileId)}
                        />
                    
                    {:else if currentScreen === 'subscribers'}
                        <SubscribersScreen
                            on:open-profile={(e) => openOtherProfileById(e.detail.profileId)}
                        />
                    
                    {:else if currentScreen === 'otherProfile'}
                        <OtherProfileScreen
                            profile={viewedProfile}
                            on:back={goBack}
                            on:toggle-subscribe={(e) => {
                                const { profileId, value } = e.detail;
                                viewedProfile = { ...viewedProfile, isSubscribed: value };
                                const key = String(profileId);
                                if (otherProfilesMock?.[key]) {
                                    otherProfilesMock[key] = { ...otherProfilesMock[key], isSubscribed: value };
                                }
                            }}
                            on:show-all-wishlists={() => pushNavigate('wishlists')}
                            on:show-all-subscriptions={() => pushNavigate('subscriptions')}
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
                        <img class="tab-icon" src="../../../../static/icons/tab-home.png" alt="" />
                        <span>Главная</span>
                        <span class="tab-dot"></span>
                    </button>
                    
                    <button
                        type="button"
                        class={`tab-item ${currentScreen === 'wishes' ? 'active' : ''}`}
                        on:click={() => navigate('wishes')}
                    >
                        <img class="tab-icon" src="../../../../static/icons/tab-gift.png" alt="" />
                        <span>Желания</span>
                        <span class="tab-dot"></span>
                    </button>
                    
                    <button
                        type="button"
                        class={`tab-item ${currentScreen === 'wishlists' ? 'active' : ''}`}
                        on:click={() => navigate('wishlists')}
                    >
                        <img class="tab-icon" src="../../../../static/icons/tab-list.png" alt="" />
                        <span>Вишлисты</span>
                        <span class="tab-dot"></span>
                    </button>
                    
                    <button
                        type="button"
                        class={`tab-item ${currentScreen === 'subscriptions' ? 'active' : ''}`}
                        on:click={() => navigate('subscriptions')}
                    >
                        <img class="tab-icon" src="../../../../static/icons/tab-eye.png" alt="" />
                        <span>Подписки</span>
                        <span class="tab-dot"></span>
                    </button>
                    
                    <button
                        type="button"
                        class={`tab-item ${currentScreen === 'settings' ? 'active' : ''}`}
                        on:click={() => navigate('settings')}
                    >
                        <img class="tab-icon" src="../../../../static/icons/tab-settings.png" alt="" />
                        <span>Настройки</span>
                        <span class="tab-dot"></span>
                    </button>
                </nav>
            {/if}
        </div>
    {:else}
        <!-- Предупреждение о запуске вне Telegram -->
        <div class="warning">
            <p>Откройте приложение в Telegram</p>
            <p>Или включите режим разработки</p>
        </div>
    {/if}
</main>

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