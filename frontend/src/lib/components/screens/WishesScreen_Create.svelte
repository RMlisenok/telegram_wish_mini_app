<!-- 2005_Dass_21.12.2025 -->
<script>
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
            <input
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
</style>