<!-- 2008/2_Dass_21.12.2025 -->
<script>
    import TextField from '../ui/TextField.svelte';
    import Button from '../ui/Button.svelte';
    //import { wishlistsStore } from '../../stores/data.js';
    import { wishlistsStore, createWishlist } from '../../../types/wishlists.ts';
    import { uploadFile } from '../../../types/storage3.ts';
    export let token;
    export let onGoBack;
    function goBack() {
        if (onGoBack) {
            onGoBack();
        }
    }
    let title = '';
    let error = '';
    let description = '';
    let photoFile = null;
    let photoPreview = null;

    function handlePhotoUpload(event) {
        const file = event.target.files[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) { 
                alert('Файл слишком большой. Максимальный размер: 5MB');
                return;
            }
            photoFile = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                photoPreview = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }
    let privacy = 'public'; // Значение по умолчанию
    const privacyOptions = [
        { value: 'private', label: 'Приватный', description: 'Виден только владельцу' },
        { value: 'restricted', label: 'Для определенных пользователей', description: 'Виден владельцу и пользователям, которым владелец дал доступ' },
        { value: 'public', label: 'Публичный', description: 'Виден всем' }
    ];
    
    // Удаление фото
    function removePhoto() {
        photoFile = null;
        photoPreview = null;
    }

    function clearError() {
        error = ''; 
    }
    async function saveWishlist() {
        // Валидация
        if (!title.trim()) {
            error = 'Пожалуйста, заполните название вишлиста';
            return;
        }
        
        error = '';
        
        try {
            let photoUrl = '';
            
            if (photoFile) {
                // Загрузка нового файла в S3
                const result = await uploadFile(photoFile, token);
                photoUrl = result.file_url;
            }

            const wishlistData = {
                name: title.trim(),
                description: description.trim(),
                typeprivacy: mapPrivacyToApi(privacy),
                photo: photoUrl
            };
            
            
            await createWishlist(token, wishlistData);
            
            goBack();
        } catch (err) {
            console.error('Ошибка при создании вишлиста:', err);
        }
    }
    function mapPrivacyToApi(privacy) {
        switch (privacy) {
            case 'private':
                return 'private';
            case 'restricted':
                return 'protected';
            case 'public':
            default:
                return 'public';
        }
    }
</script>

<div class="screen">
    <header class="app-header">
        <button class="back-btn" type="button" on:click={goBack}>
            ←
        </button>
        <div class="h1">Создать вишлист</div>
        <div class="header-placeholder"></div>
    </header>
    <!-- Обязательное поле: Название -->
    <div class="form-group">
        <label for="title" class="form-label">
            Название <span class="required">*</span>
        </label>
        <TextField
            id="title"
            type="text"
            bind:value={title}
            on:input={clearError}
            {error}
            placeholder="Например, День рождения"
            maxlength="50"
            required
        />
        <div class="char-count">{title.length}/50</div>
    </div>

    <!-- Описание -->
    <div class="form-group">
        <label for="description" class="form-label">
            Описание
        </label>
        <textarea
            id="description"
            bind:value={description}
            class="form-textarea"
            placeholder="Расскажите подробнее о вашем вишлисте..."
            rows="4"
            maxlength="250"
        ></textarea>
        <div class="char-count">{description.length}/250</div>
    </div>

    <!-- Обложка -->
    <div class="form-group">
        <div class="form-label">
            Фотография
        </div>
        <div class="photo-upload-area">
            {#if photoPreview}
                <div class="photo-preview">
                    <img src={photoPreview} alt="Preview" />
                    <Button type="button" kind="ghost" on:click={removePhoto}>
                    <img src="../../../../static/icons/delete.png" alt="" class="remove-photo-btn" />
                    <span>Удалить</span>
                    </Button>
                </div>
            {:else}
                <label class="photo-upload-label">
                    <input
                        type="file"
                        accept="image/*"
                        on:change={handlePhotoUpload}
                        class="photo-upload-input"
                    />
                    <div class="photo-upload-placeholder">
                        <img src="../../../../static/icons/add.png" alt="" class="upload-icon">
                        <div class="upload-text">Добавить фото</div>
                    </div>
                </label>
            {/if}
        </div>
    </div>

    <!-- Приватность -->
    <div class="form-group">
        <div class="form-label">
            Приватность
        </div>
        <div class="privacy-options">
            {#each privacyOptions as option}
                <label class="privacy-option">
                    <input
                        type="radio"
                        name="privacy"
                        value={option.value}
                        bind:group={privacy}
                        class="privacy-input"
                    />
                    <div class="privacy-content">
                        <div class="privacy-title">{option.label}</div>
                        <div class="privacy-description">{option.description}</div>
                    </div>
                    <div class="radio-indicator">
                        {#if privacy === option.value}
                            <div class="radio-dot"></div>
                        {/if}
                    </div>
                </label>
            {/each}
        </div>
    </div>

    <!-- Кнопки действий -->
    <div class="form-actions">
        <Button kind="primary" full on:click={goBack}>
            Отменить
        </Button>
        <Button 
            type="button" 
            kind="primary" 
            full
            on:click={saveWishlist}
        >
            Сохранить
        </Button>
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

    .form-label {
        display: block;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 6px;
        color: var(--tg-theme-text-color, #1d1d1f);
    }
    .required {
        color: #ff3b30;
    }
    .char-count {
        text-align: right;
        font-size: 12px;
        color: var(--tg-theme-hint-color, #8e8e93);
        margin-top: 4px;
    }

    .photo-upload-area {
        border: 2px dashed var(--tg-theme-hint-color, #d1d1d6);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: border-color 0.2s;
    }

    .photo-upload-area:hover {
        border-color: var(--tg-theme-link-color, #007AFF);
    }

    .photo-upload-label {
        display: block;
        cursor: pointer;
    }

    .photo-upload-input {
        display: none;
    }

    .photo-upload-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        color: var(--tg-theme-hint-color, #8e8e93);
    }

    .upload-icon {
        font-size: 32px;
        width: 60px;
        height: 60px;
        border-radius: 30px;
        background: var(--tg-theme-secondary-bg-color, #f2f2f7);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--tg-theme-link-color, #007AFF);
    }

    .upload-text {
        font-size: 14px;
    }

    .photo-preview {
        position: relative;
        max-width: 200px;
        margin: 0 auto;
    }

    .photo-preview img {
        width: 100%;
        height: auto;
        border-radius: 8px;
    }

    .form-textarea {
        width: 100%;
        padding: 12px 16px;
        border: 1px solid var(--tg-theme-hint-color, #d1d1d6);
        border-radius: 12px;
        font-size: 16px;
        background: var(--tg-theme-secondary-bg-color, #ffffff);
        color: var(--tg-theme-text-color, #1d1d1f);
        transition: border-color 0.2s;
    }

    .form-actions {
        display: flex;
        gap: 12px;
        margin-top: 32px;
        padding-top: 20px;
        border-top: 1px solid var(--tg-theme-secondary-bg-color, #f0f0f0);
    } 

    .privacy-options {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-top: 8px;
    }

    .privacy-option {
        display: flex;
        align-items: center;
        padding: 16px;
        border: 1px solid var(--tg-theme-hint-color, #d1d1d6);
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;
        background: var(--tg-theme-secondary-bg-color, #f9f9f9);
    }

    .privacy-option:hover {
        border-color: var(--tg-theme-link-color, #007AFF);
        background: var(--tg-theme-secondary-bg-color, #f0f0f5);
    }

    .privacy-input {
        display: none;
    }

    .privacy-content {
        flex: 1;
        margin-right: 12px;
    }

    .privacy-title {
        font-weight: 600;
        font-size: 16px;
        color: var(--tg-theme-text-color, #1d1d1f);
        margin-bottom: 4px;
    }

    .privacy-description {
        font-size: 14px;
        color: var(--tg-theme-hint-color, #8e8e93);
        line-height: 1.4;
    }

    .radio-indicator {
        width: 20px;
        height: 20px;
        border: 2px solid var(--tg-theme-hint-color, #8e8e93);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .privacy-option input:checked + .privacy-content ~ .radio-indicator {
        border-color: var(--tg-theme-link-color, #007AFF);
    }

    .radio-dot {
        width: 10px;
        height: 10px;
        background: var(--tg-theme-link-color, #007AFF);
        border-radius: 50%;
    }
</style>