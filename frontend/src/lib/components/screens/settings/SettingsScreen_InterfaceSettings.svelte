<!-- 2002_3_Dass_18.12.2025 -->
<script>
    import { userStore } from '$lib/stores/data';

    export let onGoBack;
    function goBack() {
        if (onGoBack) {
            onGoBack();
        }
    }
    const textSizeOptions = [
        { value: 'small', label: 'Малый', icon: 'М' },
        { value: 'medium', label: 'Средний', icon: 'С', style: 'font-size: 1.2em' },
        { value: 'large', label: 'Большой', icon: 'Б', style: 'font-size: 1.4em' }
    ];

    function setTextSize(size) {
        $userStore.ui.textSize = size;
        applySettings();
    }

    function applyTextSize() {
        // Применяем CSS-переменную ко всему документу
        const fontSizeMap = {
            small: '14px',
            medium: '16px',
            large: '18px'
        };
        const fontSize = fontSizeMap[$userStore.ui.textSize] || '16px';
        // Устанавливаем CSS-переменную на корневом элементе
        document.documentElement.style.setProperty('--app-font-size', fontSize);
        // Также обновляем класс для обратной совместимости
        const appRoot = document.querySelector('.app-root');
        if (appRoot) {
            appRoot.classList.remove('small', 'medium', 'large');
            appRoot.classList.add($userStore.ui.textSize);
        }
        localStorage.setItem('app-font-size', $userStore.ui.textSize);
    }
    

    function getCurrentTextSizeLabel() {
        const option = textSizeOptions.find(opt => opt.value === $userStore.ui.textSize);
        return option ? option.label : 'Средний';
    }

    let activeDropdown = null;
    
    function toggleDropdown(type, event) {
        if (event) {
            event.stopPropagation();
        }
        
        if (activeDropdown === type) {
            activeDropdown = null;
        } else {
            activeDropdown = type;
        }
    }

    function closeDropdowns() {
        activeDropdown = null;
    }

    function handleDropdownKeydown(type, event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            toggleDropdown(type);
        } else if (event.key === 'Escape') {
            closeDropdowns();
        }
    }
    
    function handleOptionKeydown(callback, event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            callback();
            closeDropdowns();
        }
    }

    function applySettings() {
        applyTextSize();
    }

    import { onMount } from 'svelte';
    onMount(() => {
        const savedSize = localStorage.getItem('app-font-size');
        if (savedSize && ['small', 'medium', 'large'].includes(savedSize)) {
            $userStore.ui.textSize = savedSize;
        }
        
        applySettings();
        const handleClickOutside = () => closeDropdowns();
        document.addEventListener('click', handleClickOutside);
        
        return () => {
            document.removeEventListener('click', handleClickOutside);
            
        };
    });
</script>

<div class="screen">
    <header class="app-header">
        <button class="back-btn" type="button" on:click={goBack}>
            ←
        </button>
        <div class="h1">Настройки интерфейса</div>
        <div class="header-placeholder"></div>
    </header>

    <section class="settings-section">
            <h2 class="section-title">Размер текста</h2>
            <div class="dropdown {activeDropdown === 'textSize' ? 'active' : ''}">
                <button 
                    class="dropdown-toggle" 
                    type="button"
                    on:click={(e) => toggleDropdown('textSize', e)}
                    on:keydown={(e) => handleDropdownKeydown('textSize', e)}
                    aria-expanded={activeDropdown === 'textSize'}
                    aria-haspopup="listbox"
                    aria-controls="text-size-dropdown"
                >
                    <span class="dropdown-selected">
                        <span class="selected-icon">{getCurrentTextSizeLabel().charAt(0)}</span>
                        <span class="selected-label">{getCurrentTextSizeLabel()}</span>
                    </span>
                    <span class="dropdown-arrow">▼</span>
                </button>
                
                <div 
                    class="dropdown-menu" 
                    id="text-size-dropdown"
                    role="listbox"
                    aria-label="Выберите размер текста"
                >
                    {#each textSizeOptions as option (option.value)}
                        <button
                            type="button"
                            class="dropdown-item {option.value === $userStore.ui.textSize ? 'selected' : ''}"
                            on:click={() => setTextSize(option.value)}
                            on:keydown={(e) => handleOptionKeydown(() => setTextSize(option.value), e)}
                            role="option"
                            aria-selected={option.value === $userStore.ui.textSize}
                        >
                            <span class="item-icon" style="{option.style || ''}">{option.icon}</span>
                            <span class="item-label">{option.label}</span>
                            {#if option.value === $userStore.ui.textSize}
                                <span class="item-check" aria-hidden="true">✓</span>
                            {/if}
                        </button>
                    {/each}
                </div>
            </div>
        </section>
        
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

    .settings-section {
        margin-bottom: 32px;
    }

    .section-title {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        color: var(--tg-theme-text-color, var(--text-color, #1d1d1f));
    }

    /* Стили для выпадающего списка */
    .dropdown {
        position: relative;
        width: 100%;
    }

    .dropdown-toggle {
        width: 100%;
        padding: 14px 16px;
        background: var(--card-bg, #f2f2f7);
        border: none;
        border-radius: 12px;
        font-size: 16px;
        color: var(--text-color, #1d1d1f);
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background-color 0.2s;
    }

    .dropdown-toggle:hover,
    .dropdown-toggle:focus {
        background: var(--hover-bg, #e5e5e7);
        outline: 2px solid var(--primary-color, #007AFF);
        outline-offset: 2px;
    }

    .dropdown-selected {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .selected-icon {
        font-size: 18px;
        width: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .selected-label {
        font-weight: 500;
    }

    .dropdown-arrow {
        font-size: 12px;
        color: var(--secondary-text, #8e8e93);
        transition: transform 0.3s;
    }

    .dropdown.active .dropdown-arrow {
        transform: rotate(180deg);
    }

    /* Выпадающее меню */
    .dropdown-menu {
        position: absolute;
        top: calc(100% + 4px);
        left: 0;
        right: 0;
        background: var(--bg-color, #ffffff);
        border-radius: 12px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        z-index: 100;
        opacity: 0;
        visibility: hidden;
        transform: translateY(-10px);
        transition: opacity 0.2s, transform 0.2s, visibility 0.2s;
        border: 1px solid var(--border-color, #e5e5e7);
    }

    .dropdown.active .dropdown-menu {
        opacity: 1;
        visibility: visible;
        transform: translateY(0);
    }

    .dropdown-menu button {
        width: 100%;
        text-align: left;
        background: none;
        border: none;
        cursor: pointer;
        padding: 14px 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: background-color 0.2s;
        border-bottom: 1px solid var(--border-color, #e5e5e7);
        color: inherit;
        font: inherit;
    }

    .dropdown-menu button:last-child {
        border-bottom: none;
    }

    .dropdown-menu button:hover,
    .dropdown-menu button:focus {
        background: var(--card-bg, #f2f2f7);
        outline: none;
    }

    .dropdown-menu button.selected {
        background: var(--primary-color, #007AFF);
        color: white;
    }

    .dropdown-menu button.selected .item-icon {
        color: white;
    }

    .dropdown-menu button.selected:focus {
        background: var(--primary-color-dark, #0056cc);
    }

    .item-icon {
        font-size: 18px;
        width: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .item-label {
        flex: 1;
        font-weight: 500;
    }

    .item-check {
        font-size: 18px;
        font-weight: bold;
    }

    /* Фокус для доступности */
    *:focus {
        outline: 2px solid var(--primary-color, #007AFF);
        outline-offset: 2px;
    }
    
</style>