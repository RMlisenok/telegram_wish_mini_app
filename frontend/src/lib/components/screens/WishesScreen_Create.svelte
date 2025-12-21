<!-- 2005_Dass_21.12.2025 -->
<script>
    import TextField from '$lib/components/ui/TextField.svelte';
    export let onGoBack;
    function goBack() {
        if (onGoBack) {
            onGoBack();
        }
    }
    function clearError() {
        error = ''; 
    }
    let error = '';
    let title = '';
    let photoFile = null;
    let photoPreview = null;
    let link = '';

    function handlePhotoUpload(event) {
        const file = event.target.files[0];
        if (file) {
            photoFile = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                photoPreview = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }
    
    // Удаление фото
    function removePhoto() {
        photoFile = null;
        photoPreview = null;
    }
</script>

<div class="screen">
    <header class="app-header">
        <button class="back-btn" type="button" on:click={goBack}>
            ←
        </button>
        <div class="h1">Создать желание</div>
        <div class="header-placeholder"></div>
    </header>
    <div class="form-container">
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
                placeholder="Например, Настольная лампа"
                maxlength="100"
                required
            />
            <div class="char-count">{title.length}/100</div>
        </div>
        <!-- Фото -->
        <div class="form-group">
            <div class="form-label">
                Фотография
            </div>
            <div class="photo-upload-area">
                {#if photoPreview}
                    <div class="photo-preview">
                        <img src={photoPreview} alt="Preview" />
                        <Button type="button" kind="ghost" on:click={removePhoto}>
                        <img src="/icons/delete.png" alt="" class="remove-photo-btn" />
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
                            <img src="/icons/add.png" alt="" class="upload-icon">
                            <div class="upload-text">Добавить фото</div>
                        </div>
                    </label>
                {/if}
            </div>
        </div>
        <!-- Ссылка -->
        <div class="form-group">
            <label for="link" class="form-label">
                Ссылка на товар
            </label>
            <TextField
                id="link"
                type="url"
                bind:value={link}
                placeholder="https://example.com/product"
            />
        </div>
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

    .form-container {
        padding: 0 16px 24px;
    }

    .form-group {
        margin-bottom: 20px;
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
</style>