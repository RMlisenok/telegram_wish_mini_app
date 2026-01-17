<!-- 2002_2_Dass_18.12.2025 -->
<script>
    import Button from '../../ui/Button.svelte';
    import { userStore } from '../../../stores/data';
    export let onGoBack;
    function goBack() {
        if (onGoBack) {
            onGoBack();
        }
    }

    let showSubscriptions = $userStore.showSubscriptions;

    function saveSettings() {
        userStore.set({
            showSubscriptions,
        });
        console.log('Сохранение настроек:', { showSubscriptions });
        // Здесь будет запрос к API для сохранения настройки
        goBack();
    }

    function handleSettingKeydown(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            showSubscriptions = !showSubscriptions;
        }
    }
</script>

<div class="screen">
    <header class="app-header">
        <button class="back-btn" type="button" on:click={goBack}>
            ←
        </button>
        <div class="h1">Настройки приватности</div>
        <div class="header-placeholder"></div>
    </header>

    <main class="settings-content">
        <div class="settings-section">
            <button
                type="button"
                class="setting-item"
                on:click={() => showSubscriptions = !showSubscriptions}
                on:keydown={handleSettingKeydown}
                aria-label="Показывать мои подписки"
                aria-pressed={showSubscriptions}
            >
                <div class="setting-info">
                    <div class="setting-title">Показывать мои подписки</div>
                    <div class="setting-description">
                        Видны другим пользователям в вашем публичном профиле
                    </div>
                </div>
                <div class="toggle-switch">
                    <input 
                        type="checkbox" 
                        bind:checked={showSubscriptions}
                        id="showSubscriptions"
                        class="toggle-input"
                        aria-hidden="true"
                    />
                    <span class="toggle-label" aria-hidden="true"></span>
                </div>
            </button>
        </div>
        
        <div class="save-button-container">
            <Button on:click={saveSettings} kind="primary" full={true}>
                Сохранить изменения
            </Button>
        </div>
    </main>

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

    .h1 {
        font-size: 20px;
        font-weight: 600;
        text-align: center;
        flex: 1;
        color: var(--tg-theme-text-color, #1d1d1f);
    }

    .header-placeholder {
        width: 44px;
    }

    .settings-content {
        padding: 0 16px;
    }
    
    .settings-section {
        background: var(--tg-theme-secondary-bg-color, #f8f9fa);
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 24px;
    }
    
    .setting-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
        background: var(--tg-theme-bg-color, white);
        cursor: pointer;
        border: none;
        width: 100%;
        text-align: left;
        font-family: inherit;
        font-size: inherit;
        color: inherit;
        border-bottom: 1px solid var(--tg-theme-hint-color, #e5e7eb);
        transition: background-color 0.2s ease;
    }
    
    .setting-item:hover {
        background-color: var(--tg-theme-secondary-bg-color, #f0f0f0);
    }
    
    .setting-item:focus {
        outline: 2px solid #2563eb;
        outline-offset: -2px;
    }
    
    .setting-item:last-child {
        border-bottom: none;
    }
    
    .setting-info {
        flex: 1;
        margin-right: 12px;
    }
    
    .setting-title {
        font-size: 16px;
        font-weight: 500;
        color: var(--tg-theme-text-color, #1d1d1f);
        margin-bottom: 4px;
    }
    
    .setting-description {
        font-size: 14px;
        color: var(--tg-theme-hint-color, #6b7280);
        line-height: 1.4;
    }
    
    .toggle-switch {
        position: relative;
        flex-shrink: 0;
    }
    
    .toggle-input {
        display: none;
    }
    
    .toggle-label {
        display: block;
        width: 52px;
        height: 32px;
        background: #e5e7eb;
        border-radius: 16px;
        position: relative;
        cursor: pointer;
        transition: background 0.2s ease;
    }
    
    .toggle-label:after {
        content: '';
        position: absolute;
        top: 2px;
        left: 2px;
        width: 28px;
        height: 28px;
        background: white;
        border-radius: 50%;
        transition: transform 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    
    .toggle-input:checked + .toggle-label {
        background: #2563eb;
    }
    
    .toggle-input:checked + .toggle-label:after {
        transform: translateX(20px);
    }
    
    .save-button-container {
        padding: 0 16px;
        margin-top: 24px;
    }
</style>