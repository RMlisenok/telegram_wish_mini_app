<!--<script>-->
<!--  export let text;-->
<!--  export let removable = false;-->

<!--  const remove = () => {-->
<!--    const evt = new CustomEvent('remove');-->
<!--    dispatchEvent(evt);-->
<!--  };-->
<!--</script>-->

<!--<div class="tag">-->
<!--  <span>{text}</span>-->
<!--  {#if removable}-->
<!--    <button class="x" type="button" on:click|stopPropagation={remove}>✕</button>-->
<!--  {/if}-->
<!--</div>-->

<!--<style>-->
<!--  .tag {-->
<!--    display: inline-flex;-->
<!--    align-items: center;-->
<!--    gap: 4px;-->
<!--    padding: 4px 10px;-->
<!--    border-radius: 999px;-->
<!--    font-size: 12px;-->
<!--    background: #eff6ff;-->
<!--    color: #1d4ed8;-->
<!--  }-->
<!--  .x {-->
<!--    border: none;-->
<!--    background: transparent;-->
<!--    font-size: 12px;-->
<!--    cursor: pointer;-->
<!--  }-->
<!--</style>-->

<script>
    import { createEventDispatcher } from 'svelte';

    export let text = '';
    export let removable = false;

    const dispatch = createEventDispatcher();

    const handleRemove = () => {
        dispatch('remove', { text });
    };
</script>

<style>
    .tag {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        border-radius: 999px;
        font-size: 12px;
        background: #e5f0ff;
        color: #1f2937;
    }

    .remove-btn {
        border: none;
        background: transparent;
        cursor: pointer;
        font-size: 12px;
        line-height: 1;
        padding: 0;
    }
</style>

<span class="tag">
    <span>{text}</span>
    {#if removable}
        <button
                type="button"
                class="remove-btn"
                aria-label="Удалить тег"
                on:click|stopPropagation={handleRemove}
        >
            ×
        </button>
    {/if}
</span>
