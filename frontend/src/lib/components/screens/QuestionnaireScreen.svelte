<script>
    import { onMount } from 'svelte';
    import Tag from '$lib/components/ui/Tag.svelte';
    import TextField from '$lib/components/ui/TextField.svelte';
    import Button from '$lib/components/ui/Button.svelte';
    import { questionnaireStore } from '$lib/stores/data.js';

    const predefinedInterests = [
        'кино','театр','аниме','мультфильмы','фэнтези','музыка','музыкальные инструменты',
        'коллекционирование','лего','фотография','книги','научпоп','саморазвитие',
        'иностранные языки','компьютерные игры','настольные игры','рукоделие',
        'сад и огород','домашний декор','спорт','танцы','технологии и наука',
        '3Д-моделирование и графика','робототехника','программирование','активный образ жизни',
        'путешествия','кулинария и выпечка','сладости','сувениры','цветы','подарочные сертификаты',
        'алкоголь','украшения','косметика и парфюмерия','-'
    ];

    const predefinedNoGifts = [
        'сладости','косметика и парфюмерия','сувениры','цветы','алкоголь',
        'мягкие игрушки','домашний декор','книги','подарочные сертификаты','-'
    ];

    let interests = [];
    let noGifts = [];
    let customInterest = '';
    let customNoGift = '';

    let errors = {
        interests: '',
        noGifts: ''
    };

    // Charger depuis le store à l’ouverture de la page
    onMount(() => {
        const current = $questionnaireStore;
        interests = current.interests || [];
        noGifts = current.noGifts || [];
    });

    const addInterest = (tag) => {
        if (interests.length >= 20) {
            errors.interests = 'Можно добавить не более 20 интересов.';
            return;
        }
        if (!interests.includes(tag)) {
            interests = [...interests, tag];
            errors.interests = '';
        }
    };

    const addCustomInterest = () => {
        const t = customInterest.trim();
        if (!t) return;
        if (t.length > 20) {
            errors.interests = 'Максимум 20 символов для кастомного тега.';
            return;
        }
        addInterest(t);
        customInterest = '';
    };

    const addNoGift = (tag) => {
        if (noGifts.length >= 10) {
            errors.noGifts = 'Можно указать не более 10 вариантов.';
            return;
        }
        if (!noGifts.includes(tag)) {
            noGifts = [...noGifts, tag];
            errors.noGifts = '';
        }
    };

    const addCustomNoGift = () => {
        const t = customNoGift.trim();
        if (!t) return;
        if (t.length > 20) {
            errors.noGifts = 'Максимум 20 символов для кастомного тега.';
            return;
        }
        addNoGift(t);
        customNoGift = '';
    };

    const removeInterest = (tag) => {
        interests = interests.filter((t) => t !== tag);
    };

    const removeNoGift = (tag) => {
        noGifts = noGifts.filter((t) => t !== tag);
    };

    const save = () => {
        // plus de minimum obligatoire : on peut tout laisser vide
        errors.interests = '';
        errors.noGifts = '';

        questionnaireStore.set({
            interests,
            noGifts
        });

        alert('Анкета сохранена!');
    };
</script>

<header class="app-header">
    <div class="h1">Анкета</div>
</header>

<section class="section-card">
    <div class="h2">Интересы</div>
    <p class="hint">
        Выберите интересы, которые вам нравятся. Можно добавить до 20 тегов.
    </p>

    <div class="chips">
        {#each predefinedInterests as tag}
            <button
                    class="chip-btn"
                    type="button"
                    on:click={() => addInterest(tag)}
            >
                {tag}
            </button>
        {/each}
    </div>

    <div class={`chips-selected ${errors.interests ? 'error' : ''}`}>
        {#if interests.length === 0}
            <span class="placeholder">Пока ничего не выбрано.</span>
        {/if}

        {#each interests as tag}
            <Tag
                    text={tag}
                    removable
                    on:remove={(e) => removeInterest(e.detail.text)}
            />
        {/each}
    </div>

    {#if errors.interests}
        <div class="field-error">{errors.interests}</div>
    {/if}

    <div style="margin-top:8px;">
        <TextField
                bind:value={customInterest}
                label="Свой интерес"
                placeholder="Например, джазовые концерты"
                maxlength={20}
        />
        <div style="height:6px;"></div>
        <Button kind="ghost" full on:click={addCustomInterest}>
            Добавить свой тег
        </Button>
    </div>
</section>

<section class="section-card">
    <div class="h2">Что вам не дарить?</div>
    <p class="hint">
        Выберите или добавьте пометки о подарках, которые не подойдут.
    </p>

    <div class="chips">
        {#each predefinedNoGifts as tag}
            <button
                    class="chip-btn"
                    type="button"
                    on:click={() => addNoGift(tag)}
            >
                {tag}
            </button>
        {/each}
    </div>

    <div class={`chips-selected ${errors.noGifts ? 'error' : ''}`}>
        {#if noGifts.length === 0}
            <span class="placeholder">Пока ничего не выбрано.</span>
        {/if}

        {#each noGifts as tag}
            <Tag
                    text={tag}
                    removable
                    on:remove={(e) => removeNoGift(e.detail.text)}
            />
        {/each}
    </div>

    {#if errors.noGifts}
        <div class="field-error">{errors.noGifts}</div>
    {/if}

    <div style="margin-top:8px;">
        <TextField
                bind:value={customNoGift}
                label="Своя пометка"
                placeholder="Например, ничего для кухни"
                maxlength={20}
        />
        <div style="height:6px;"></div>
        <Button kind="ghost" full on:click={addCustomNoGift}>
            Добавить свой тег
        </Button>
    </div>
</section>

<div style="padding:0 16px 12px;">
    <Button full on:click={save}>
        Сохранить анкету
    </Button>
</div>

<style>
    .hint {
        font-size: 12px;
        color: #6b7280;
        margin: 0 0 6px;
    }

    .chips {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 8px;
    }

    .chip-btn {
        border-radius: 999px;
        border: 1px solid #e5e7eb;
        padding: 4px 10px;
        font-size: 12px;
        background: #ffffff;
        cursor: pointer;
    }

    .chips-selected {
        min-height: 34px;
        border-radius: 12px;
        border: 1px solid transparent;
        padding: 6px;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        background: #f9fafb;
    }

    .chips-selected.error {
        border-color: #ef4444;
    }

    .placeholder {
        font-size: 12px;
        color: #9ca3af;
    }

    .field-error {
        margin-top: 4px;
        font-size: 12px;
        color: #b91c1c;
    }
</style>


