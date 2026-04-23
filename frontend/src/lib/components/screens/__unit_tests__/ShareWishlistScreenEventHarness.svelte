<script>
  import ShareWishlistScreen from '../ShareWishlistScreen.svelte';

  export let user;
  export let wishlist;

  let events = [];

  const pushEvent = (payload) => {
    events = [...events, payload];
  };
</script>

<ShareWishlistScreen
  {user}
  {wishlist}
  on:backToWishlist={(event) => pushEvent(`backToWishlist:${event.detail.wishlistId}`)}
/>

<ul data-testid="events-log">
  {#each events as eventName}
    <li>{eventName}</li>
  {/each}
</ul>
