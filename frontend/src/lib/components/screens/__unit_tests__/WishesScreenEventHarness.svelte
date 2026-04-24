<script>
  import WishesScreen from '../WishesScreen.svelte';

  export let token = '';
  export let wishlistId = null;
  export let isExternalWishlist = false;
  export let currentUserId = null;
  export let onNavigateToCreateWishes = () => {};

  let events = [];

  const pushEvent = (name, detail = null) => {
    events = [...events, detail == null ? name : `${name}:${JSON.stringify(detail)}`];
  };
</script>

<WishesScreen
  {token}
  {wishlistId}
  {isExternalWishlist}
  {currentUserId}
  {onNavigateToCreateWishes}
  on:openFinishedWishes={() => pushEvent('openFinishedWishes')}
  on:openEditWishes={(event) => pushEvent('openEditWishes', event.detail)}
  on:shareWishlist={(event) => pushEvent('shareWishlist', event.detail)}
/>

<ul data-testid="events-log">
  {#each events as eventName}
    <li>{eventName}</li>
  {/each}
</ul>
