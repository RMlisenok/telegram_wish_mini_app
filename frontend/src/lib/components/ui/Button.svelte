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

