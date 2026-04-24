<!-- 2002_4_Dass_20.12.2025 -->
<script>
    import { notificationSettingsStore } from '../../../stores/data';
    export let onGoBack;
    function goBack() {
        if (onGoBack) {
            onGoBack();
        }
    }

    // Состояния для переключателей
    let birthdayReminders = $notificationSettingsStore.birthdayReminders;
    let newFollowers = $notificationSettingsStore.newFollowers;
    let postBirthdayNotifications = $notificationSettingsStore.postBirthdayNotifications;
    let wishlistAccessRequests = $notificationSettingsStore.wishlistAccessRequests;
    
    export let token;
    import { onMount } from 'svelte';

    onMount(async () => {
        await fetchNotificationSettings();
    });

    async function fetchNotificationSettings() {
        if (!token) return;
        
        try {
            const response = await fetch('/api/v1/settings/notifications', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Ошибка загрузки настроек');
            }
            
            const data = await response.json();
            
            // Маппинг полей из API
            newFollowers = data.new_followers;
            wishlistAccessRequests = data.access_requests;
            postBirthdayNotifications = data.birt_after;
            birthdayReminders = data.birt_before;
            
            // Обновляем стор
            notificationSettingsStore.set({
                birthdayReminders: data.birt_before,
                newFollowers: data.new_followers,
                postBirthdayNotifications: data.birt_after,
                wishlistAccessRequests: data.access_requests
            });
            
        } catch (err) {
            //error = err.message;
            console.error('Ошибка загрузки настроек:', err);
        }
    }
    
    async function saveSettings() {
        if (!token) return;
        
        try {
            const settingsData = {
                new_followers: newFollowers,
                access_requests: wishlistAccessRequests,
                birt_after: postBirthdayNotifications,
                birt_before: birthdayReminders
            };
            
            const response = await fetch('/api/v1/settings/notifications', {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(settingsData)
            });
            
            if (!response.ok) {
                throw new Error('Ошибка сохранения настроек');
            }
            
            const result = await response.json();
            
            // Обновляем стор с серверными данными
            notificationSettingsStore.set({
                birthdayReminders: result.update_data.birt_before,
                newFollowers: result.update_data.new_followers,
                postBirthdayNotifications: result.update_data.birt_after,
                wishlistAccessRequests: result.update_data.access_requests
            });
            
            goBack();
            
        } catch (err) {
            //error = err.message;
            console.error('Ошибка сохранения настроек:', err);
        }
    }

    function handleSettingKeydown(event, settingName) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            switch(settingName) {
                case 'birthdayReminders':
                    birthdayReminders = !birthdayReminders;
                    break;
                case 'newFollowers':
                    newFollowers = !newFollowers;
                    break;
                case 'postBirthdayNotifications':
                    postBirthdayNotifications = !postBirthdayNotifications;
                    break;
                case 'wishlistAccessRequests':
                    wishlistAccessRequests = !wishlistAccessRequests;
                    break;
            }
        }
    }
</script>

<div class="screen">
    <header class="app-header">
        <button class="back-btn" type="button" on:click={goBack}>
            ←
        </button>
        <div class="h1">Настройки уведомлений</div>
        <div class="header-placeholder"></div>
    </header>

    <main class="settings-content">
        <div class="settings-section">
            <!-- Напоминания о ДР пользователей -->
            <button
                type="button"
                class="setting-item"
                on:click={() => birthdayReminders = !birthdayReminders}
                on:keydown={(e) => handleSettingKeydown(e, 'birthdayReminders')}
                aria-label="Напоминания о ДР пользователей, на которых подписан"
                aria-pressed={birthdayReminders}
            >
                <div class="setting-info">
                    <div class="setting-title">Напоминания о ДР пользователей</div>
                    <div class="setting-description">
                        Получать уведомления о днях рождения пользователей, на которых вы подписаны
                    </div>
                </div>
                <div class="toggle-switch">
                    <input 
                        type="checkbox" 
                        bind:checked={birthdayReminders}
                        id="birthdayReminders"
                        class="toggle-input"
                        aria-hidden="true"
                    />
                    <span class="toggle-label" aria-hidden="true"></span>
                </div>
            </button>
            
            <!-- Новые подписчики -->
            <button
                type="button"
                class="setting-item"
                on:click={() => newFollowers = !newFollowers}
                on:keydown={(e) => handleSettingKeydown(e, 'newFollowers')}
                aria-label="Новые подписчики"
                aria-pressed={newFollowers}
            >
                <div class="setting-info">
                    <div class="setting-title">Новые подписчики</div>
                    <div class="setting-description">
                        Получать уведомления о новых подписчиках
                    </div>
                </div>
                <div class="toggle-switch">
                    <input 
                        type="checkbox" 
                        bind:checked={newFollowers}
                        id="newFollowers"
                        class="toggle-input"
                        aria-hidden="true"
                    />
                    <span class="toggle-label" aria-hidden="true"></span>
                </div>
            </button>

            <!-- Уведомления после собственного ДР -->
            <button
                type="button"
                class="setting-item"
                on:click={() => postBirthdayNotifications = !postBirthdayNotifications}
                on:keydown={(e) => handleSettingKeydown(e, 'postBirthdayNotifications')}
                aria-label="Уведомления после собственного ДР"
                aria-pressed={postBirthdayNotifications}
            >
                <div class="setting-info">
                    <div class="setting-title">Уведомления после собственного ДР</div>
                    <div class="setting-description">
                        Перемещение забронированных подарков в исполненные
                    </div>
                </div>
                <div class="toggle-switch">
                    <input 
                        type="checkbox" 
                        bind:checked={postBirthdayNotifications}
                        id="postBirthdayNotifications"
                        class="toggle-input"
                        aria-hidden="true"
                    />
                    <span class="toggle-label" aria-hidden="true"></span>
                </div>
            </button>

            <!-- Заявки на доступ к вишлистам -->
            <button
                type="button"
                class="setting-item"
                on:click={() => wishlistAccessRequests = !wishlistAccessRequests}
                on:keydown={(e) => handleSettingKeydown(e, 'wishlistAccessRequests')}
                aria-label="Заявки на доступ к вишлистам"
                aria-pressed={wishlistAccessRequests}
            >
                <div class="setting-info">
                    <div class="setting-title">Заявки на доступ к вишлистам</div>
                    <div class="setting-description">
                        Уведомления о запросах доступа к вашим вишлистам
                    </div>
                </div>
                <div class="toggle-switch">
                    <input 
                        type="checkbox" 
                        bind:checked={wishlistAccessRequests}
                        id="wishlistAccessRequests"
                        class="toggle-input"
                        aria-hidden="true"
                    />
                    <span class="toggle-label" aria-hidden="true"></span>
                </div>
            </button>
        </div>
        
        <div class="save-button-container">
            <button class="save-button" on:click={saveSettings}>
                Сохранить изменения
            </button>
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
    
    .save-button {
        width: 100%;
        padding: 16px;
        background: #2563eb;
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }
    
    .save-button:hover {
        background: #1d4ed8;
    }
    
    .save-button:active {
        background: #1e40af;
    }
</style>