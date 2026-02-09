<script>
  export let size = 52;
  export let src = '';
  export let initials = '??';
</script>

<div
  class="avatar"
  style={`width:${size}px;height:${size}px;font-size:${size / 2.5}px;`}
>
  {#if src}
    <img src={src} alt="avatar" />
  {:else}
    <span>{initials}</span>
  {/if}
</div>

<style>
  .avatar {
    border-radius: 999px;
    background: linear-gradient(135deg, #fee2e2, #dbeafe);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #111827;
    overflow: hidden;
    flex-shrink: 0;
  }
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
</style>
