<!-- 2002_1_Dass_16.12.2025 -->
 <script>
    import Avatar from '$lib/components/ui/Avatar.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import TextField from '$lib/components/ui/TextField.svelte';

    import { userStore } from '$lib/stores/data';

    let fullName = $userStore?.fullName || '';
    let birthDate = $userStore?.birthDate || '';
    let avatarUrl = $userStore?.avatarUrl || '';
    let tempAvatarUrl = avatarUrl;

    export let onGoBack;
    function goBack() {
        if (onGoBack) {
            onGoBack();
        }
    }

    function getInitials(name) {
        if (!name) return '??';
        const parts = name.trim().split(' ');
        return parts.slice(0, 2).map((p) => p[0]).join('').toUpperCase();
    }

    function uploadPhoto() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                if (file.size > 10 * 1024 * 1024) { 
                    alert('Файл слишком большой. Максимальный размер: 10MB');
                    return;
                }
                const reader = new FileReader();
                reader.onload = (event) => {
                    tempAvatarUrl = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        };
        input.click();
    }

    function removePhoto() {
        tempAvatarUrl = '';
    }

    function saveProfile() {
        
        
        $userStore = {
            ...$userStore,
            fullName: fullName.trim(),
            birthDate,
            avatarUrl: tempAvatarUrl
        };
        
        alert('Изменения успешно сохранены');
        goBack();
    }

</script>

<div class="screen">
    <header class="app-header">
        <button class="back-btn" type="button" on:click={goBack}>
            ←
        </button>
        <div class="h1">Настройки профиля</div>
        <div class="header-placeholder"></div>
    </header>

    <div class="edit-profile-content">
        <section class="section-card">
            <!-- Фотография профиля -->
            <div class="avatar-section">
                <div class="avatar-container">
                    <Avatar 
                        size={152} 
                        src={tempAvatarUrl} 
                        initials={getInitials(fullName)} 
                    />
                </div>
                
                <div class="avatar-actions">
                    <Button kind="ghost" on:click={uploadPhoto}>
                        <img src="/icons/add.png" alt="" class="btn-icon" />
                        <span>Загрузить фото</span>
                    </Button>
                    
                    {#if tempAvatarUrl}
                        <Button kind="ghost" on:click={removePhoto}>
                            <img src="/icons/delete.png" alt="" class="btn-icon" />
                            <span>Удалить</span>
                        </Button>
                    {/if}
                    
                </div>
            </div>
            
            
            <Button kind="primary" full={true} on:click={saveProfile}>
                Сохранить изменения
            </Button>
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

    .edit-profile-content {
        padding: 0;
    }
    
    .section-card {
        background: var(--tg-secondary-bg-color);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 12px;
    }
    
    .avatar-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 30px;
        gap: 16px;
    }
    
    .avatar-container {
        width: 120px;
        height: 120px;
    }
    
    .avatar-actions {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        justify-content: center;
    }

    .btn-icon {
        width: 16px;
        height: 16px;
        margin-right: 6px;
    }

    
</style>
