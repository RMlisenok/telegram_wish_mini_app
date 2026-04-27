<!-- 2005_Dass_21.12.2025 -->
<script>
    import TextField from '../ui/TextField.svelte';
    import Button from '../ui/Button.svelte';
    import { onMount } from 'svelte';
    import { uploadFile } from '../../../types/storage3.ts';
    //import { wishesStore, wishlistsStore } from '../../stores/data.js';

    import { wishlistsStore, loadWishlists } from '../../../types/wishlists.ts';
    import { createWish } from '../../../types/wishes.ts';
    export let onGoBack;
    export let token;
    let removePhotoFlag = false;

    onMount(async () => {
        if (!token) {
            console.error('Токен не найден');
            return;
        }
        
        try {
            await loadWishlists(token);
        } catch (error) {
            console.error('Ошибка загрузки данных MainScreen:', error);
        }
    });

    function goBack() {
        if (onGoBack) {
            onGoBack();
        }
    }
    function clearError() {
        error = ''; 
    }
    let error = '';
    let linkError = '';
    let title = '';
    let photoFile = null;
    let photoPreview = null;
    let link = '';
    let price = '';
    let currency = '';
    let description = '';
    let selectedWishlists = [];

    const currencies = [
        { value: 'RUB', label: '₽' },
        { value: 'BYN', label: 'Br' },
        { value: 'USD', label: '$' },
        { value: 'EUR', label: '€' },
        { value: 'UAH', label: '₴' },
        { value: 'KZT', label: '₸' }
    ];

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
        removePhotoFlag = true;
    }

    // Сохранение желания
    async function saveWish() {
        // Валидация
        if (!title.trim()) {
            error = 'Пожалуйста, заполните название желания';
            return;
        }

        if (link.trim() && !/^https?:\/\//i.test(link.trim())) {
            linkError = 'Ссылка должна начинаться с http:// или https://';
            return;
        }
        
        error = '';   
        linkError = '';

        

        try {
            let photoUrl = '';
            
            if (photoFile) {
                // Загрузка нового файла в S3
                const result = await uploadFile(photoFile, token);
                photoUrl = result.file_url;
            }
            // Создание объекта желания
            const wishData = {
                name: title.trim(),
                description: description.trim(),
                price: price ? parseFloat(price) : null,
                currency: currency || null,
                url_gift: link.trim(),
                photo: photoUrl
            };
            if (currency && currency.trim() !== '') {
                wishData.currency = currency;
            }

            const newWish = await createWish(token, wishData);
            console.log('Создано новое желание:', newWish);

            if (selectedWishlists.length > 0 && newWish.id) {
                for (const wishlistId of selectedWishlists) {
                    try {
                        await connectWishToWishlist(token, newWish.id, parseInt(wishlistId));
                    } catch (connectError) {
                        console.warn(`Не удалось привязать к вишлисту ${wishlistId}:`, connectError);
                    }
                }
            }
            
            // Возвращаемся назад
            goBack();
        } catch (error) {
            console.error('Ошибка создания желания:', error);
            error = 'Не удалось создать желание. Пожалуйста, попробуйте еще раз.';
        }
    }
    async function connectWishToWishlist(token, wishId, wishlistId) {
        const connectData = {
            "is_pinned": false,
            "order_position": 1,
            "wish_id": wishId,
            "wishlist_id": wishlistId
        };

        try {
            const response = await fetch(`/api/v1/wishlists/${wishlistId}/wishes`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(connectData)
            });

            if (!response.ok) {
                throw new Error(`Ошибка привязки к вишлисту: ${response.status}`);
            }

            const result = await response.json();
            console.log('Желание привязано к вишлисту:', result);
            return result;
        } catch (error) {
            console.error('Ошибка привязки желания к вишлисту:', error);
            throw error;
        }
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
                error={linkError}
            />
        </div>

        <!-- Цена и Валюта -->
        <div class="form-row">
            <div class="form-group half">
                <label for="price" class="form-label">
                    Цена
                </label>
                <input
                    id="price"
                    type="number"
                    bind:value={price}
                    class="form-input"
                    placeholder="0.00"
                    min="0"
                    step="0.01"
                />
            </div>
            
            <div class="form-group half">
                <label for="currency" class="form-label">
                    Валюта
                </label>
                <select
                    id="currency"
                    bind:value={currency}
                    class="form-select"
                >
                    <option value="">Выберите валюту</option>
                    {#each currencies as currencyOption}
                        <option value={currencyOption.value}>
                            {currencyOption.label}
                        </option>
                    {/each}
                </select>
            </div>
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
                placeholder="Расскажите подробнее о вашем желании..."
                rows="4"
                maxlength="500"
            ></textarea>
            <div class="char-count">{description.length}/500</div>
        </div>
        <!-- Выбор вишлистов -->
        <div class="form-group">
            <div class="form-label">
                Вишлисты для привязки
            </div>
            
            {#if $wishlistsStore.length === 0}
                <div class="empty-state">
                    У вас пока нет вишлистов. Это желание будет сохранено в общий список.
                </div>
            {:else}
                <div class="wishlists-selector">
                    {#each $wishlistsStore as wishlist}
                        <label class="wishlist-option">
                            <input
                                type="checkbox"
                                value={wishlist.id}
                                bind:group={selectedWishlists}
                                class="wishlist-checkbox"
                            />
                            <div class="wishlist-option-content">
                                <div class="wishlist-option-title">
                                    {wishlist.title}
                                </div>
                                <div class="wishlist-option-meta">
                                    {wishlist.privacy === 'public' 
                                        ? 'Виден всем' 
                                        : wishlist.privacy === 'private' 
                                            ? 'Только мне' 
                                            : 'Для выбранных'}
                                    · {wishlist.count || 0} жел.
                                </div>
                            </div>
                            <div class="wishlist-checkmark">
                                {#if selectedWishlists.includes(wishlist.id.toString())}
                                    ✓
                                {/if}
                            </div>
                        </label>
                    {/each}
                </div>
                
                <div class="selected-count">
                    Выбрано: {selectedWishlists.length} из {$wishlistsStore.length}
                </div>
            {/if}
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
                on:click={saveWish}
            >
                Сохранить
            </Button>
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

    .form-input,
    .form-select,
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

    .form-row {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
    }
    .form-group.half {
        flex: 1;
    }
    .form-input:focus,
    .form-select:focus,
    .form-textarea:focus {
        outline: none;
        border-color: var(--tg-theme-link-color, #007AFF);
    }

    .form-textarea {
        resize: vertical;
        min-height: 100px;
        font-family: inherit;
    }

    .form-actions {
        display: flex;
        gap: 12px;
        margin-top: 32px;
        padding-top: 20px;
        border-top: 1px solid var(--tg-theme-secondary-bg-color, #f0f0f0);
    } 

    .wishlists-selector {
        border: 1px solid var(--tg-theme-hint-color, #d1d1d6);
        border-radius: 12px;
        overflow: hidden;
        max-height: 300px;
        overflow-y: auto;
    }

    .wishlist-option {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        border-bottom: 1px solid var(--tg-theme-secondary-bg-color, #f0f0f0);
        cursor: pointer;
        transition: background-color 0.2s;
        background: var(--tg-theme-secondary-bg-color, #ffffff);
    }

    .wishlist-option:last-child {
        border-bottom: none;
    }

    .wishlist-option:hover {
        background: var(--tg-theme-hint-color, #f5f5f7);
    }

    .wishlist-checkbox {
        display: none;
    }

    .wishlist-option-content {
        flex: 1;
        margin-right: 12px;
    }

    .wishlist-option-title {
        font-weight: 500;
        color: var(--tg-theme-text-color, #1d1d1f);
        margin-bottom: 2px;
    }

    .wishlist-option-meta {
        font-size: 12px;
        color: var(--tg-theme-hint-color, #8e8e93);
    }

    .wishlist-checkmark {
        width: 24px;
        height: 24px;
        border-radius: 12px;
        border: 2px solid var(--tg-theme-hint-color, #d1d1d6);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: bold;
        color: transparent;
        transition: all 0.2s;
    }

    .wishlist-option input:checked + .wishlist-option-content + .wishlist-checkmark {
        background: var(--tg-theme-link-color, #007AFF);
        border-color: var(--tg-theme-link-color, #007AFF);
        color: white;
    }

    .selected-count {
        text-align: right;
        font-size: 13px;
        color: var(--tg-theme-hint-color, #8e8e93);
        margin-top: 8px;
    }

    .empty-state {
        padding: 16px;
        text-align: center;
        color: var(--tg-theme-hint-color, #8e8e93);
        font-size: 14px;
        border: 1px dashed var(--tg-theme-hint-color, #d1d1d6);
        border-radius: 12px;
        background: var(--tg-theme-secondary-bg-color, #f9f9f9);
    }
</style>
