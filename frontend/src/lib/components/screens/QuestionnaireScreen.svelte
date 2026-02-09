<script lang="ts">
    import {onMount} from 'svelte';
    import Tag from '../ui/Tag.svelte';
    import TextField from '../ui/TextField.svelte';
    import Button from '../ui/Button.svelte';
    //import {questionnaireStore} from '../../stores/data.js';
    import { createEventDispatcher } from 'svelte';
    import { loadAvailableTags, loadQuestionnaire, questionnaireStore, TagItem, QuestionnaireData, saveQuestionnaire } from '../../../types/questionnaire.ts';

    const dispatch = createEventDispatcher();

    const goBack = () => {
        dispatch('back');
    };


    const predefinedInterests = [
        'кино', 'театр', 'аниме', 'мультфильмы', 'фэнтези', 'музыка', 'музыкальные инструменты',
        'коллекционирование', 'лего', 'фотография', 'книги', 'научпоп', 'саморазвитие',
        'иностранные языки', 'компьютерные игры', 'настольные игры', 'рукоделие',
        'сад и огород', 'домашний декор', 'спорт', 'танцы', 'технологии и наука',
        '3Д-моделирование и графика', 'робототехника', 'программирование', 'активный образ жизни',
        'путешествия', 'кулинария и выпечка', 'сладости', 'сувениры', 'цветы', 'подарочные сертификаты',
        'алкоголь', 'украшения', 'косметика и парфюмерия', '-'
    ];

    const predefinedNoGifts = [
        'сладости', 'косметика и парфюмерия', 'сувениры', 'цветы', 'алкоголь',
        'мягкие игрушки', 'домашний декор', 'книги', 'подарочные сертификаты', '-'
    ];

    let interests: TagItem[] = [];
    let noGifts: TagItem[] = [];
    let customInterest = '';
    let customNoGift = '';
    let availableInterests: string[] = [];
    let availableNoGifts: string[] = [];

    let errors = {
        interests: '',
        noGifts: ''
    };

    export let token;

    // Charger depuis le store à l’ouverture de la page
    onMount(async () => {
        if (!token) {
            console.error("Токен не найден для загрузки анкеты.");
        }
        try {
            availableInterests = await loadAvailableTags(token, true);
            availableNoGifts = await loadAvailableTags(token, false);

            const data = await loadQuestionnaire(token);
            interests = data.interests;
            noGifts = data.avoid_gifts;

            questionnaireStore.set({ interests, avoid_gifts: noGifts });
        } catch (err) {
            console.error('Ошибка загрузки анкеты или тегов:', err);
        }
    });

    const addInterest = (tag: string) => {
        interests = addTag(interests, tag, 20, 'interests');
        errors = { ...errors, interests: '' };
    };
    
    const addTag = (arr: TagItem[], tagValue: string, maxCount: number, errorKey: keyof typeof errors): TagItem[] => {
        if (arr.length >= maxCount) {
            errors = { ...errors, [errorKey]: `Можно добавить не более ${maxCount} тегов.` };
            return arr;
        }
        if (!arr.some(item => item.tag === tagValue)) {
            const existingTag = [...interests, ...noGifts].find(item => item.tag === tagValue);
            const newTag: TagItem = { 
                tag: tagValue, 
                details: existingTag?.details || ''
            };
            return [...arr, newTag];
        }
        return arr;
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

    const addNoGift = (tag: string) => {
        noGifts = addTag(noGifts, tag, 10, 'noGifts'); // Переименовано
        errors = { ...errors, noGifts: '' };
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

    const removeTag = (arr: TagItem[], tagValue: string): TagItem[] => {
        return arr.filter(t => t.tag !== tagValue);
    };

    const removeInterest = (tag: string) => {
        interests = removeTag(interests, tag);
    };

    const removeNoGift = (tag: string) => {
        noGifts = removeTag(noGifts, tag);
    };

    // Функция для обновления деталей тега
    const updateTagDetails = (arr: TagItem[], tagValue: string, newDetails: string): TagItem[] => {
        return arr.map(item => {
            if (item.tag === tagValue) {
                return { ...item, details: newDetails.substring(0, 100) };
            }
            return item;
        });
    };

    const updateInterestDetails = (tag: string, details: string) => {
        interests = updateTagDetails(interests, tag, details);
    };

    const updateNoGiftDetails = (tag: string, details: string) => {
        noGifts = updateTagDetails(noGifts, tag, details);
    };

    $: isValidInterests = interests.some(item => item.tag === '-') || interests.length >= 3; // FS-5.3
    $: isValidNoGifts = noGifts.some(item => item.tag === '-') || noGifts.length >= 1; // FS-5.3
    $: isValid = isValidInterests && isValidNoGifts;


    const save = async () => {
        errors = {interests: '', noGifts: ''};

        if (!isValidInterests) {
            errors = {...errors, interests: 'Для сохранения анкеты необходимо выбрать минимум 3 интереса.'};
        }
        if (!isValidNoGifts) {
            errors = {...errors, noGifts: 'Для сохранения анкеты необходимо выбрать минимум 1 тег'};
        }
        if (errors.interests || errors.noGifts) return;

        const validatedInterests = interests.map(item => ({
            tag: item.tag,
            details: item.details || ''
        }));
        
        const validatedNoGifts = noGifts.map(item => ({
            tag: item.tag,
            details: item.details || ''
        }));

        questionnaireStore.set({
            interests: validatedInterests, 
            avoid_gifts: validatedNoGifts 
        });

        try {
            if (!token) throw new Error('Токен авторизации отсутствует.');

            const questionnaireData: QuestionnaireData = {
                interests: validatedInterests,
                avoid_gifts: validatedNoGifts
            };
            console.log('Sending data:', questionnaireData);
            await saveQuestionnaire(token, questionnaireData);

            alert('Анкета успешно сохранена! Теперь друзья смогут видеть ваши интересы.'); // FS-5.6
        } catch (err) {
            console.error('Ошибка сохранения анкеты:', err);
        }
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

    <!-- <div class="chips">
        {#each predefinedInterests as tag}
            <button
                    class="chip-btn"
                    type="button"
                    on:click={() => addInterest(tag)}
            >
                {tag}
            </button>
        {/each}
    </div> -->
    <div class="chips">
        {#each availableInterests as tag}
            {#if !interests.some(i => i.tag === tag)} <!-- Показываем только не выбранные -->
                <button type="button" class="chip-btn" on:click={() => addInterest(tag)}>
                    {tag}
                </button>
            {/if}
        {/each}
    </div>


    <!-- <div class={`chips-selected ${errors.interests ? 'error' : ''}`}>
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
    </div> -->
    <!-- Выбранные интересы с полями для деталей -->
    <div class={`chips-selected ${errors.interests ? 'error' : ''}`}>
        {#if interests.length > 0}
            {#each interests as item}
                <div class="selected-chip-with-details">
                    <Tag text={item.tag} removable={true} on:remove={() => removeInterest(item.tag)} />
                    <TextField
                        label="Детали"
                        placeholder="Уточните..."
                        value={item.details || ''}
                        maxlength={100}
                        on:change={(e) => updateInterestDetails(item.tag, e.detail || '')}
                    />
                </div>
            {/each}
        {:else}
            <span class="placeholder">Пока ничего не выбрано.</span>
        {/if}
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

    <!-- <div class="chips">
        {#each predefinedNoGifts as tag}
            <button
                    class="chip-btn"
                    type="button"
                    on:click={() => addNoGift(tag)}
            >
                {tag}
            </button>
        {/each}
    </div> -->
    <div class="chips">
        {#each availableNoGifts as tag}
            {#if !noGifts.some(n => n.tag === tag)}
                <button type="button" class="chip-btn" on:click={() => addNoGift(tag)}>
                    {tag}
                </button>
            {/if}
        {/each}
    </div>

    <div class={`chips-selected ${errors.noGifts ? 'error' : ''}`}> 
        {#if noGifts.length > 0} 
            {#each noGifts as item} 
                <div class="selected-chip-with-details">
                    <Tag text={item.tag} removable={true} on:remove={() => removeNoGift(item.tag)} />
                    <TextField
                        label="Детали"
                        placeholder="Уточните..."
                        value={item.details || ''}
                        maxlength={100}
                        on:change={(e) => updateNoGiftDetails(item.tag, e.detail || '')}
                    />
                </div>
            {/each}
        {:else}
            <span class="placeholder">Пока ничего не выбрано.</span>
        {/if}
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
    <Button
            full
            kind="ghost"
            inactive={!isValid}
            on:click={save}
    >
        Сохранить анкету
    </Button>
</div>

<div style="padding:0 16px 12px;">
    <Button kind="primary" full on:click={goBack}>
        Вернуться в профиль
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
        background: #fff7f7;
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


