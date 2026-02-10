<script lang="ts">
    import { onMount } from 'svelte';
    import { initializeTelegram, user, telegram } from './lib/telegram';
    import StartScreen from './lib/components/screens/StartScreen.svelte'; // Импортируем стартовый экран

    // Импорты экранов
    import MainScreen from './lib/components/screens/MainScreen.svelte';
    import ShareProfileScreen from './lib/components/screens/ShareProfileScreen.svelte';
    import ShareWishlistScreen from './lib/components/screens/ShareWishlistScreen.svelte';
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
    import FinishedWishesScreen from './lib/components/screens/FinishedWishesScreen.svelte';
    import WishlistsScreen from './lib/components/screens/WishlistsScreen.svelte';
    import SubscriptionsScreen from './lib/components/screens/SubscriptionsScreen.svelte';
    import SubscribersScreen from './lib/components/screens/SubscribersScreen.svelte';
    import type { User } from './types/user';
    import { writable } from 'svelte/store';

    // Импорты stores (нужно будет создать или импортировать)
    // import { otherProfilesMock } from './lib/stores/data';
    import { parseStartParam } from './lib/stores/data.js';

    let currentScreen = 'start';
    let viewedProfile = null;
    let screenStack = [];
    
    let currentWishlistId = null;
    let currentWishlistIsExternal = false;
    let selectedWishlistId = null;
    let selectedWishId = null;
    let isExternalUser = false;
    let externalProfileId = null;
    
    let showStartScreen = true; // Состояние для отображения стартового экрана
    let tg = null;
    let token = null; //токен важно!
    let startParamData = null;
    //let userStore = null;
    let currentWishlistForShare = null;
    
    onMount(() => {
        tg = initializeTelegram();
        
        if (!tg) {
            console.warn('Приложение запущено вне Telegram');
            return;
        }

        // Проверяем start_param из Telegram
        const initDataUnsafe = tg.initDataUnsafe;
        if (initDataUnsafe?.start_param) {
            const startParam = initDataUnsafe.start_param;
            console.log('Получен start_param:', startParam);
            
            // Парсим параметр
            startParamData = parseStartParam(startParam);
            console.log('Распарсенные данные:', startParamData);
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

    function handleBackToWishlist(event) {
        const { wishlistId } = event.detail;
        navigate('wishes', { 
            wishlistId: wishlistId,
            isExternal: currentWishlistIsExternal 
        });
    }
    
    function openOtherProfile(profile) {
        viewedProfile = profile;
        pushNavigate('otherProfile');
    }

    async function loadUserProfileById(profileId: number) {
        if (!token) {
            console.error('Token не найден для загрузки профиля');
            return null;
        }

        try {
            const response = await fetch(`/api/v1/users/${profileId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Ошибка загрузки профиля: ${response.status}`);
            }
            
            const userData = await response.json();
            
            // Преобразуем данные в формат, ожидаемый OtherProfileScreen
            return {
                id: userData.id,
                fullName: userData.name,
                birthDate: formatDateToDDMMYYYY(userData.birth_date),
                avatarUrl: userData.photo || '',
                isSubscribed: false, // Нужно будет проверить через API
                publicWishlists: [], // Нужно загрузить отдельно
                subscriptions: [], // Нужно загрузить отдельно
                questionnaire: { interests: [], noGifts: [] }, // Нужно загрузить отдельно
                subscriptionsArePrivate: !userData.show_sub
            };
            
        } catch (error) {
            console.error('Ошибка загрузки профиля пользователя:', error);
            return null;
        }
    }

    function isMyOwnProfile(profileId) {
        if (!profileId || !currentUserId) return false;
        return profileId.toString() === currentUserId.toString();
    }
    
    async function openOtherProfileById(profileId) {
        if (isMyOwnProfile(profileId)) {
            navigate('main');
            return;
        }

        viewedProfile = {
            id: profileId,
            fullName: 'Загрузка...',
            birthDate: '—',
            avatarUrl: '',
            isSubscribed: false,
            publicWishlists: [],
            subscriptions: [],
            questionnaire: { interests: [], noGifts: [] },
            subscriptionsArePrivate: false
        };
        
        pushNavigate('otherProfile');
        
        // Загружаем данные профиля
        const profileData = await loadUserProfileById(profileId);
        
        if (profileData) {
            // Загружаем дополнительные данные
            try {
                // Загружаем публичные вишлисты пользователя
                const wishlistsResponse = await fetch(`/api/v1/users/${profileId}/wishlists`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (wishlistsResponse.ok) {
                    const wishlistsData = await wishlistsResponse.json();
                    profileData.publicWishlists = wishlistsData
                        .filter((wl: any) => wl.typeprivacy === 'public')
                        .map((wl: any) => ({
                            id: wl.id,
                            title: wl.name,
                            iconUrl: wl.photo,
                            visibility: wl.typeprivacy,
                            wishesCount: wl.wishes_count
                        }));
                }
                
                // Загружаем подписки пользователя
                const subscriptionsResponse = await fetch(`/api/v1/subscriptions/users/${profileId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (subscriptionsResponse.ok) {
                    const subscriptionsData = await subscriptionsResponse.json();
                    profileData.subscriptions = subscriptionsData.subscriptions
                        .filter((sub: any) => sub.type === 'user')
                        .map((sub: any) => ({
                            id: sub.user_id,
                            fullName: sub.name,
                            avatarUrl: sub.photo,
                            birthDate: formatDateToDDMMYYYY(sub.birth_date)
                        }));
                }
                
                // Загружаем анкету пользователя
                const questionnaireResponse = await fetch(`/api/v1/questionnaire/${profileId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (questionnaireResponse.ok) {
                    const questionnaireData = await questionnaireResponse.json();
                    profileData.questionnaire = {
                        interests: questionnaireData.interests || [],
                        noGifts: questionnaireData.avoid_gifts || []
                    };
                }
                
                // Проверяем подписку текущего пользователя
                const subscriptionCheckResponse = await fetch(`/api/v1/subscriptions/check/user/${profileId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                
                if (subscriptionCheckResponse.ok) {
                    const checkData = await subscriptionCheckResponse.json();
                    profileData.isSubscribed = checkData.is_subscribed;
                }
                
            } catch (error) {
                console.error('Ошибка загрузки дополнительных данных:', error);
            }
            
            viewedProfile = profileData;
        }
    }

    async function showAllWishlistsForUser(profileId: number, isExternalProfile: boolean = true) {
        console.log('showAllWishlistsForUser called with:', { profileId, isExternalProfile });
        if (!token || !profileId) {
            console.error('No token or profileId');
            return;
        }
        
        try {
            // Загружаем вишлисты указанного пользователя
            const response = await fetch(`/api/v1/users/${profileId}/wishlists`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const wishlistsData = await response.json();
                console.log('Loaded wishlists:', wishlistsData);
                
                // Преобразуем данные для отображения
                const userWishlists = wishlistsData
                    .filter((wl: any) => wl.typeprivacy === 'public' || wl.typeprivacy === 'protected')
                    .map((wl: any) => ({
                        id: wl.id.toString(),
                        name: wl.name,
                        title: wl.name,
                        photo: wl.photo,
                        description: wl.description,
                        typeprivacy: wl.typeprivacy,
                        privacy: mapPrivacy(wl.typeprivacy),
                        count: wl.wishes_count || 0,
                        wishesCount: wl.wishes_count || 0,
                        isExternal: isExternalProfile,
                        ownerId: profileId,
                        ownerName: ''
                    }));

                // Загружаем информацию о владельце
                try {
                    const ownerResponse = await fetch(`/api/v1/users/${profileId}`, {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });
                    
                    if (ownerResponse.ok) {
                        const ownerData = await ownerResponse.json();
                        // Обновляем имя владельца во всех вишлистах
                        userWishlists.forEach(wl => {
                            wl.ownerName = ownerData.name || 'Пользователь';
                        });
                    }
                } catch (error) {
                    console.error('Ошибка загрузки информации о владельце:', error);
                }

                console.log('Processed wishlists:', userWishlists);
            
                // Сохраняем загруженные вишлисты
                wishlistsForExternalUser = userWishlists;
                externalProfileId = profileId;
                isExternalUser = true;
            
                // Переходим на экран вишлистов с флагом внешнего пользователя
                navigate('wishlists', { keepExternalState: true });
                
            } else {
                console.error('Не удалось загрузить вишлисты пользователя');
                showNotification('Не удалось загрузить вишлисты пользователя');
            }
        } catch (error) {
            console.error('Ошибка загрузки вишлистов пользователя:', error);
            showNotification('Произошла ошибка при загрузке вишлистов');
        }
    }

    function mapPrivacy(typeprivacy: string): 'public' | 'restricted' | 'private' {
        switch (typeprivacy) {
            case 'public':
                return 'public';
            case 'protected':
                return 'restricted';
            case 'private':
                return 'private';
            default:
                return 'private';
        }
    }

    let wishlistsForExternalUser = [];
    let currentExternalProfileId = null;

    function handleShowAllWishlists(event) {
        const { profileId, isExternalProfile } = event.detail;
        showAllWishlistsForUser(profileId, isExternalProfile);
    }
    
    function navigate(screen, params = {}) {
        // Сброс состояния внешнего пользователя при переходе на вишлисты через таб-бар или главный экран
        if (screen === 'wishlists' && !params.isExternal && !params.keepExternalState) {
            isExternalUser = false;
            externalProfileId = null;
            wishlistsForExternalUser = [];
        }

        currentScreen = screen;
        if (params.wishlistId) {
            currentWishlistId = params.wishlistId;
            if (params.isExternal) {
                currentWishlistIsExternal = true;
            } else {
                currentWishlistIsExternal = false;
            }
            console.log(currentWishlistId);
        } else {
            currentWishlistId = null;
            currentWishlistIsExternal = false;
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

    let currentUserId: string | null = null;

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
        // Сохраняем ID пользователя для проверок текущего пользователя с другими
        currentUserId = user.id.toString();
        if (user.birth_date != null)
        {
            navigate('main');
        }
        else
        {
            navigate('editProfileBirthDate');
        }
        userStore.set({
            id: token || 'demo-user-1',
            user_id: user.id.toString(),
            fullName: user.name  || 'Гость',
            birthDate: formatDateToDDMMYYYY(user.birth_date),
            avatarUrl: user.photo || '',
            showSubscriptions: user.show_sub ?? true,
            ui: {
                textSize: (user.text_size as 'small' | 'medium' | 'large') || 'medium',
                theme: (user.theme as 'light' | 'dark' | 'system') || 'system'
            }
        });
        console.log(userStore);

        // Проверяем, есть ли deep link для открытия
        if (startParamData) {
            // Обрабатываем deep link
            if (startParamData.type === 'profile') {
                if (startParamData.id.toString() === currentUserId) {
                    // Если это профиль текущего пользователя
                    navigate('main');
                } else {
                    // Если это чужой профиль
                    await openOtherProfileById(startParamData.id);
                }
            } else if (startParamData.type === 'wishlist') {
                await openWishlistById(startParamData.id);
            }
        } else {
            // Обычный запуск
            if (user.birth_date != null) {
                navigate('main');
            } else {
                navigate('editProfileBirthDate');
            }
        }
    };

    function openShareWishlist(wishlistData) {
        currentWishlistForShare = wishlistData;
        pushNavigate('shareWishlist');
    }
    
    async function openWishlistById(wishlistId) {
        if (!token || !wishlistId) return;
        
        try {
            // Загружаем информацию о вишлисте
            const response = await fetch(`/api/v1/wishlists/${wishlistId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const wishlistData = await response.json();
                
                // Проверяем, кто владелец вишлиста
                const currentUser = $userStore;
                const isExternalWishlist = wishlistData.user_id.toString() !== currentUser.user_id;
                
                if (isExternalWishlist) {
                    // Если это чужой вишлист, проверяем подписку
                    const subscriptionCheck = await checkWishlistSubscription(token, wishlistId);
                    
                    // Переходим на экран желаний с флагом внешнего вишлиста
                    navigate('wishes', { 
                        wishlistId: wishlistId.toString(),
                        isExternal: true 
                    });
                } else {
                    // Если это наш вишлист
                    navigate('wishes', { 
                        wishlistId: wishlistId.toString(),
                        isExternal: false 
                    });
                }
            } else {
                console.error('Вишлист не найден');
                navigate('main');
            }
        } catch (error) {
            console.error('Ошибка открытия вишлиста:', error);
            navigate('main');
        }
    }

    // Функция проверки подписки на вишлист
    async function checkWishlistSubscription(token, wishlistId) {
        try {
            const response = await fetch(`/api/v1/subscriptions/check/wishlist/${wishlistId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.is_subscribed;
            }
            return false;
        } catch (error) {
            console.error('Ошибка проверки подписки:', error);
            return false;
        }
    }

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
                            on:openWishlists={() => {
                                isExternalUser = false;
                                externalProfileId = null;
                                wishlistsForExternalUser = [];
                                navigate('wishlists');
                            }}
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
                            onUpdateUser={(updatedData) => {
                                userStore.update(current => ({...current, ...updatedData}));
                            }}
                        />
                    
                    {:else if currentScreen === 'privacySettings'}
                        <SettingsScreenPrivacySettings 
                            token={token}
                            userStore={$userStore}
                            onGoBack={() => navigate('settings')}
                            onUpdateUser={(updatedData) => {
                                userStore.update(current => ({...current, ...updatedData}));
                            }}
                        />
                    
                    {:else if currentScreen === 'interfaceSettings'}
                        <SettingsScreenInterfaceSettings
                            token={token}
                            userStore={$userStore}
                            onGoBack={() => navigate('settings')}
                            onUpdateUser={(updatedData) => {
                                userStore.update(current => ({...current, ...updatedData}));
                            }}   
                        />
                    
                    {:else if currentScreen === 'legalInformation'}
                        <SettingsScreenLegalInformation
                            onGoBack={() => navigate('settings')}
                        />
                    
                    {:else if currentScreen === 'notifficationSettings'}
                        <SettingsScreenNotificationSettings
                            token={token}
                            onGoBack={() => navigate('settings')}
                        />
                    
                    {:else if currentScreen === 'questionnaire'}
                        <QuestionnaireScreen 
                            user={$userStore} 
                            token={token}
                            on:back={() => navigate('main')} 
                        />
                    
                    {:else if currentScreen === 'wishes'}
                        <WishesScreen 
                            token={token}
                            wishlistId={currentWishlistId}
                            onMount={() => console.log(currentWishlistId)}
                            isExternalWishlist={currentWishlistIsExternal}
                            currentUserId={currentUserId}
                            onNavigateToCreateWishes={() => navigate('wishesCreate')} 
                            on:openEditWishes={(e) => {
                                selectedWishId = e.detail.id;
                                navigate('wishesEdit'); 
                            }}
                            on:shareWishlist={(e) => {
                                openShareWishlist(e.detail);
                            }}
                            on:openFinishedWishes={() => pushNavigate('finishedWishes')}
                        />
                    {:else if currentScreen === 'finishedWishes'}
                        <FinishedWishesScreen 
                            token={token}
                            on:back={() => navigate('wishes')}
                        />
                    {:else if currentScreen === 'shareProfile'}
                        <ShareProfileScreen 
                            user={$userStore} 
                            otherProfile={viewedProfile}
                            on:back={() => navigate('main')}
                            on:back={() => {
                                viewedProfile = null;
                                navigate('main');
                            }}
                        />

                    {:else if currentScreen === 'shareWishlist'}
                        <ShareWishlistScreen 
                            user={$userStore} 
                            wishlist={currentWishlistForShare}
                            on:backToWishlist={handleBackToWishlist}
                        />
                    
                    {:else if currentScreen === 'wishesCreate'}
                        <WishesScreenCreate
                            token={token}
                            onGoBack={() => navigate('wishes')}
                        />
                    
                    {:else if currentScreen === 'wishesEdit'}
                        <WishesScreenEdit
                            token={token}
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
                            on:openWishlistDetail={(e) => {
                                console.log(e.detail.wishlistId);
                                const isExternal = e.detail.isExternal || isExternalUser || false;
                                navigate('wishes', { 
                                    wishlistId: e.detail.wishlistId,
                                    isExternal: isExternal
                                });
                            }}
                            on:openEditWishlists={(e) => {
                                selectedWishlistId = e.detail.id;
                                navigate('wishlistsEdit'); 
                            }}
                            on:openOwnerProfile={(e) => {
                                const { profileId } = e.detail;
                                if (profileId && profileId !== 'current_user') {
                                    openOtherProfileById(profileId);
                                }
                            }}
                            isExternalUser={isExternalUser}
                            externalProfileId={externalProfileId}
                            externalUserWishlists={wishlistsForExternalUser}
                        />
                    
                    {:else if currentScreen === 'wishlistsEdit'}
                        <WishlistsScreenEdit
                            wishlistId={selectedWishlistId}
                            token={token}
                            onGoBack={() => {
                                selectedWishlistId = null;
                                navigate('wishlists');
                            }}
                        />
                    
                    {:else if currentScreen === 'subscriptions'}
                        <SubscriptionsScreen
                            token={token}
                            on:open-profile={(e) => openOtherProfileById(e.detail.profileId)}
                            on:openWishlistDetail={(e) => 
                                navigate('wishes', { 
                                    wishlistId: e.detail.wishlistId,
                                    isExternal: true 
                                })
                            }
                        />
                    
                    {:else if currentScreen === 'subscribers'}
                        <SubscribersScreen
                            on:open-profile={(e) => openOtherProfileById(e.detail.profileId)}
                        />
                    
                    {:else if currentScreen === 'otherProfile'}
                        <OtherProfileScreen
                            token={token}
                            profile={viewedProfile}
                            on:back={goBack}
                            on:toggle-subscribe={(e) => {
                                const { profileId, value } = e.detail;
                                // Обновляем локальное состояние
                                viewedProfile = { ...viewedProfile, isSubscribed: value };
                            }}
                            on:open-wishlist={(e) => {
                                // Обработка открытия вишлиста
                                navigate('wishes', { 
                                    wishlistId: e.detail.wishlistId,
                                    isExternal: true 
                                });
                            }}
                            on:open-profile={(e) => {
                                // Рекурсивное открытие другого профиля
                                openOtherProfileById(e.detail.profileId);
                            }}
                            on:show-all-wishlists={(e) => handleShowAllWishlists(e)}
                            on:show-all-subscriptions={() => pushNavigate('subscriptions')}
                            on:share-profile={(e) => {
                                const profileId = e.detail.profileId;
                                navigate('shareProfile', { profileData: viewedProfile });
                            }}
                        />
                    {:else if currentScreen === 'editProfileBirthDate'}
                        <SettingsScreenEditProfile
                            token={token}
                            userStore={$userStore}
                            birthDateOnly={true}
                            onGoBack={() => navigate('main')}
                            onUpdateUser={(updatedData) => {
                                userStore.update(current => ({...current, ...updatedData}));
                                navigate('main'); 
                            }}
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
                        on:click={() => {
                            isExternalUser = false;
                            externalProfileId = null;
                            wishlistsForExternalUser = [];
                            navigate('wishlists');
                        }}                        
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