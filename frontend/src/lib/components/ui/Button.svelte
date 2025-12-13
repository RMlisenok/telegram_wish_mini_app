<script>
    import { createEventDispatcher } from 'svelte';

    export let kind = 'primary'; // primary | ghost
    export let full = false;
    export let disabled = false;

    const dispatch = createEventDispatcher();

    const handleClick = (event) => {
        if (disabled) return;
        // on renvoie un "click" que les parents peuvent écouter
        dispatch('click', event);
    };
</script>

<button
        type="button"
        class={`ui-button ${kind} ${full ? 'full' : ''}`}
        disabled={disabled}
        on:click={handleClick}
>
    <slot />
</button>

<style>
    .ui-button {
        border-radius: 999px;
        border: none;
        padding: 10px 18px;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        transition: background 120ms ease, transform 80ms ease, box-shadow 80ms ease;
    }

    .ui-button.primary {
        background: #2563eb;
        color: white;
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.35);
    }

    .ui-button.primary:active {
        transform: translateY(1px);
        box-shadow: 0 3px 8px rgba(37, 99, 235, 0.35);
    }

    .ui-button.ghost {
        background: #eff6ff;
        color: #1d4ed8;
    }

    .ui-button.full {
        width: 100%;
    }

    .ui-button:disabled {
        opacity: 0.6;
        cursor: default;
        box-shadow: none;
    }
</style>
