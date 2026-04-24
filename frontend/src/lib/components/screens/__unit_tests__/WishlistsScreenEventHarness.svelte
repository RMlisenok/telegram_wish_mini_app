<script>
  import WishlistsScreen from '../WishlistsScreen.svelte';

  export let token = '';
  export let isExternalUser = false;
  export let externalProfileId = null;
  export let externalUserWishlists = [];

  let events = [];

  const pushEvent = (name, detail = null) => {
    events = [...events, detail == null ? name : `${name}:${JSON.stringify(detail)}`];
  };
</script>

<WishlistsScreen
  {token}
  {isExternalUser}
  {externalProfileId}
  {externalUserWishlists}
  on:openCreateWishlists={() => pushEvent('openCreateWishlists')}
  on:openEditWishlists={(event) => pushEvent('openEditWishlists', event.detail)}
  on:openMainScreen={() => pushEvent('openMainScreen')}
  on:openOwnerProfile={(event) => pushEvent('openOwnerProfile', event.detail)}
  on:openWishlistDetail={(event) => pushEvent('openWishlistDetail', event.detail)}
/>

<ul data-testid="events-log">
  {#each events as eventName}
    <li>{eventName}</li>
  {/each}
</ul>
