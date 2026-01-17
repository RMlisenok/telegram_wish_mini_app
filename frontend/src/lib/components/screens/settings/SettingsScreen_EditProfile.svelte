<!-- 2002_1_Dass_16.12.2025 -->
 <script>
    import Avatar from '../../ui/Avatar.svelte';
    import Button from '../../ui/Button.svelte';
    import TextField from '../../ui/TextField.svelte';

    import { userStore } from '../../../stores/data';

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
        if (!validateForm()) {
            return;
        }
        
        $userStore = {
            ...$userStore,
            fullName: fullName.trim(),
            birthDate,
            avatarUrl: tempAvatarUrl
        };
        
        alert('Изменения успешно сохранены');
        goBack();
    }

    function handleFullNameChange(event) {
        fullName = event.detail;
        errors.fullName = '';
    }
    
    function handleBirthDateChange(event) {
        birthDate = event.detail;
        errors.birthDate = '';
    }
    
    let errors = {
        fullName: '',
        birthDate: ''
    };

    function validateForm() {
        errors = { fullName: '', birthDate: '' };
        let isValid = true;
        
        if (!fullName || fullName.trim().length > 40) {
            errors.fullName = 'Поле Имя и фамилия должно содержать от 1 до 40 символов';
            isValid = false;
        }
        
        const dateRegex = /^\d{2}\.\d{2}\.\d{4}$/;
        if (!birthDate) {
            errors.birthDate = 'Дата рождения обязательна';
            isValid = false;
        } else if (!dateRegex.test(birthDate)) {
            errors.birthDate = 'Используйте формат ДД.ММ.ГГГГ';
            isValid = false;
        } else {
            const [day, month, year] = birthDate.split('.').map(Number);
            const inputDate = new Date(year, month - 1, day);
            const minDate = new Date(1900, 0, 1); // 01.01.1900
            if (inputDate < minDate) {
                errors.birthDate = 'Дата рождения не может быть раньше 01.01.1900';
                isValid = false;
            }
        }
        
        return isValid;
    }

</script>

<div class="screen">
    <header class="app-header">
        <button class="back-btn" type="button" on:click={goBack}>
            ←
        </button>
        <div class="h1">Редактировать профиль</div>
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

            <!-- Фамилия и имя-->
             <div class="form-fields">
                <TextField
                    label="Имя и фамилия"
                    placeholder="Введите ваше имя и фамилию"
                    bind:value={fullName}
                    on:change={handleFullNameChange}
                    error={errors.fullName}
                    required={true}
                />
                
                <TextField
                    label="Дата рождения"
                    placeholder="ДД.ММ.ГГГГ"
                    bind:value={birthDate}
                    on:change={handleBirthDateChange}
                    error={errors.birthDate}
                    maxlength="10"
                    required={true}
                />
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
        margin-top: 24px;
    }

    .btn-icon {
        width: 16px;
        height: 16px;
        margin-right: 6px;
    }

    .form-fields {
        margin-bottom: 32px;
        display: flex;
        flex-direction: column;
        gap: 16px;
    }
</style>
