<script>
    import Avatar from '$lib/components/ui/Avatar.svelte';
    import { subscribersStore } from '$lib/stores/data.js';

    const ICON_ARROW = '/icons/arrow-right.png';

    // Получение инициалов для аватара
    const getInitials = (name) => {
        if (!name) return '??';
        const parts = name.trim().split(' ');
        return parts.slice(0, 2).map(p => p[0]).join('').toUpperCase();
    };

    // Обработчик открытия профиля подписчика
    const handleOpenProfile = (subscriber) => {
        console.log('Открытие профиля подписчика:', subscriber.user_id);
        // TODO: Реализовать переход к профилю подписчика
    };

    // Форматирование даты для отображения
    const formatBirthDate = (dateStr) => {
        if (!dateStr) return 'не указана';
        return dateStr;
    };

</script>

<header class="app-header">
    <div class="h1">Все ваши подписчики</div>
</header>

<section class="section-card">
    {#if $subscribersStore.length === 0}
        <p class="empty-note">
            У вас пока нет подписчиков.
        </p>
    {:else}
        <div class="subscribers-list">
            {#each $subscribersStore as subscriber (subscriber.id)}
                <div 
                    class="subscriber-card"
                    on:click={() => handleOpenProfile(subscriber)}
                    role="button"
                    tabindex="0"
                    on:keydown={(e) => e.key === 'Enter' && handleOpenProfile(subscriber)}
                >
                    <!-- Аватар и основная информация -->
                    <div class="subscriber-content">
                        <Avatar 
                            size={60}
                            src={subscriber.photo}
                            initials={getInitials(subscriber.name)}
                            style={subscriber.is_blocked ? 'opacity: 0.5; filter: grayscale(100%);' : ''}
                        />
                        
                        <div class="subscriber-info">
                            <div class="subscriber-name" title={subscriber.name}>
                                {subscriber.name}
                            </div>
                            
                            <div class="subscriber-meta">
                                <span>Дата рождения: {formatBirthDate(subscriber.birth_date)}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Кнопки управления -->
                    <div class="subscriber-controls">
                        <!-- Стрелка для перехода -->
                        <button
                            class="control-button arrow-button"
                            on:click|stopPropagation={() => handleOpenProfile(subscriber)}
                            aria-label="Открыть профиль"
                        >
                            <img src={ICON_ARROW} alt=">" />
                        </button>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</section>

<style>
    .subscribers-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 0 16px;
    }

    .subscriber-card {
        display: flex;
        gap: 12px;
        align-items: center;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        cursor: pointer;
    }

    .subscriber-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .subscriber-card:focus-visible {
        outline: 2px solid #3b82f6;
        outline-offset: 2px;
    }

    .subscriber-content {
        display: flex;
        gap: 12px;
        align-items: center;
        flex: 1;
    }

    .subscriber-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 4px;
        min-width: 0;
    }

    .subscriber-name {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
        line-height: 1.3;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .subscriber-meta {
        font-size: 13px;
        color: #6b7280;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 4px;
    }

    /* Управление подписчиками */
    .subscriber-controls {
        display: flex;
        gap: 8px;
        align-items: center;
    }

    .control-button {
        border: none;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .arrow-button {
        width: 36px;
        height: 36px;
        background: transparent;
        border-radius: 50%;
        padding: 8px;
    }

    .arrow-button:hover {
        background: #f3f4f6;
    }

    .arrow-button img {
        width: 20px;
        height: 20px;
        object-fit: contain;
    }

    .empty-note {
        text-align: center;
        padding: 40px 16px;
        color: #6b7280;
        font-size: 16px;
    }

    /* Адаптивность */
    @media (max-width: 768px) {
        .subscriber-controls {
            flex-direction: column;
            align-items: stretch;
        }
    }

    @media (max-width: 480px) {
        .subscriber-card {
            flex-direction: column;
            align-items: stretch;
            gap: 16px;
        }
        
        .subscriber-content {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
        }
        
        .subscriber-name {
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;
        }

        .subscriber-controls {
            flex-direction: row;
            justify-content: flex-end;
            width: 100%;
            margin-top: 12px;
            border-top: 1px solid #e5e7eb;
            padding-top: 12px;
        }
    }
</style>