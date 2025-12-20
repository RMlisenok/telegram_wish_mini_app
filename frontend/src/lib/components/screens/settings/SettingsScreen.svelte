<!-- 2002_Dass_16.12.2025 -->
<script>
    export let onGoBack;
    function goBack() {
        if (onGoBack) {
            onGoBack();
        }
    }
    
    // Навигация по разделам
    // 2002_1_Dass_16.12.2025 -->
    export let onNavigateToEditProfile;
    function navigateToEditProfile() {
        if (onNavigateToEditProfile) {
            onNavigateToEditProfile();
        }
    }
    // 2002_1_Dass_16.12.2025 <--
    
    // 2002_2_Dass_18.12.2025 -->
    export let onNavigateToPrivacySettings;
    function navigateToPrivacySettings() {
        if (onNavigateToPrivacySettings) {
            onNavigateToPrivacySettings();
        }
    }
    // 2002_2_Dass_18.12.2025 <--
    
    // 2002_3_Dass_18.12.2025 -->
    export let onNavigateToInterfaceSettings;
    function navigateToInterfaceSettings() {
        if (onNavigateToInterfaceSettings) {
            onNavigateToInterfaceSettings();
        }
    }
    // 2002_3_Dass_18.12.2025 <--
    
    //2002_4_Dass_20.12.2025 -->
    export let onNavigateToNotificationSettings;
    function navigateToNotificationSettings() {
        if (onNavigateToNotificationSettings) {
            onNavigateToNotificationSettings();
        }
    }
    //2002_4_Dass_20.12.2025 <--

    // 2002_5_Dass_18.12.2025 -->
    export let onNavigateToLegalInformation;
    function navigateToLegalInformation() {
        if (onNavigateToLegalInformation) {
            onNavigateToLegalInformation();
        }
    }
    // 2002_5_Dass_18.12.2025 <--
</script>

<div class="screen">
    <header class="app-header">
        <button class="back-btn" type="button" on:click={goBack}>
            ←
        </button>
        <div class="h1">Настройки</div>
        <div class="header-placeholder"></div>
    </header>

    <div class="settings-content">
        <section class="section-card">
            <button class="settings-item" type="button" on:click={navigateToEditProfile}>
                <div class="item-info">
                    <span class="item-title">Редактировать профиль</span>
                    <span class="item-subtitle">Изменить личную информацию</span>
                </div>
                <div class="item-arrow">›</div>
            </button>

            <button class="settings-item" type="button" on:click={navigateToPrivacySettings}>
                <div class="item-info">
                    <span class="item-title">Настройки приватности</span>
                    <span class="item-subtitle">Управление видимостью профиля и вишлистов</span>
                </div>
                <div class="item-arrow">›</div>
            </button>

            <button class="settings-item" type="button" on:click={navigateToInterfaceSettings}>
                <div class="item-info">
                    <span class="item-title">Настройки интерфейса</span>
                    <span class="item-subtitle">Тема, размер текста</span>
                </div>
                <div class="item-arrow">›</div>
            </button>

            <button class="settings-item" type="button" on:click={navigateToNotificationSettings}>
                <div class="item-info">
                    <span class="item-title">Настройки уведомлений</span>
                    <span class="item-subtitle">Управление push-уведомлениями</span>
                </div>
                <div class="item-arrow">›</div>
            </button>

            <button class="settings-item" type="button" on:click={navigateToLegalInformation}>
                <div class="item-info">
                    <span class="item-title">Юридическая информация</span>
                </div>
                <div class="item-arrow">›</div>
            </button>
        </section>
    </div>
</div>

<style>
    * {
        padding: 0;
        box-sizing: border-box;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }

    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        margin-bottom: 16px;
        position: sticky;
        top: 0;
        background: var(--tg-theme-bg-color, white);
        z-index: 10;
    }

    .back-btn {
        background: none;
        border: none;
        font-size: 24px;
        color: var(--tg-theme-link-color, #007AFF);
        cursor: pointer;
        padding: 8px;
        margin: -8px;
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .back-btn:hover {
        opacity: 0.8;
    }

    .header-placeholder {
        width: 44px;
    }

    .settings-content {
        padding: 0;
    }

    .section-card {
        background: var(--tg-theme-secondary-bg-color, #f8f8f8);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
    }

    .settings-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        cursor: pointer;
        transition: background-color 0.2s;
        border-bottom: 1px solid var(--tg-theme-secondary-bg-color, #f0f0f0);
        border: none;
        background: none;
        width: 100%;
        text-align: left;
        border-radius: 12px;
        margin-bottom: 4px;
    }

    .settings-item:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }

    .settings-item:last-child {
        border-bottom: none;
        margin-bottom: 0;
    }

    .item-info {
        display: flex;
        flex-direction: column;
        gap: 4px;
        flex: 1;
    }

    .h1 {
        font-size: 1.25em; /* 20px при базовом 16px */
        font-weight: 600;
    }

    .item-title {
        font-size: 1em;
        font-weight: 600;
    }

    .item-subtitle {
        font-size: 0.875em;
    }

    .item-arrow {
        font-size: 1.25em;
    }

    /* Адаптивность */
    /* @media (max-width: 480px) {
        .screen {
            padding: 0 12px;
        }
        
        .settings-item {
            padding: 14px;
        }
    } */
</style>