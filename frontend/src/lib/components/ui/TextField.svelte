<script>
  export let label = '';
  export let placeholder = '';
  export let value = '';
  export let type = 'text';
  export let error = '';
  export let maxlength;
  export let required = false;
  export let readonly = false;

  const handleInput = (event) => {
    value = event.target.value;
    const custom = new CustomEvent('change', { detail: value });
    dispatchEvent(custom);
  };
</script>

<label class="field">
  {#if label}
    <div class="field-label">
      <span>{label}</span>
      {#if required}<span class="required">*</span>{/if}
    </div>
  {/if}
  <input
    class:error={!!error}
    bind:value
    type={type}
    placeholder={placeholder}
    {maxlength}
    {readonly}
    on:input={handleInput}
  />
  {#if error}
    <div class="field-error">{error}</div>
  {/if}
</label>

<style>
  .field {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 14px;
  }
  .field-label {
    display: flex;
    align-items: center;
    gap: 4px;
    color: #374151;
  }
  .required {
    color: #ef4444;
  }
  input {
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    padding: 8px 10px;
    font-size: 15px;
    outline: none;
  }
  input:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.35);
  }
  input.error {
    border-color: #ef4444;
  }
  .field-error {
    font-size: 12px;
    color: #b91c1c;
  }
</style>
