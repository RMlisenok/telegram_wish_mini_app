<script>
  import OtherProfileScreen from '../OtherProfileScreen.svelte';

  export let token = '';
  export let profile;

  let events = [];

  const pushEvent = (name, detail = null) => {
    events = [...events, detail == null ? name : `${name}:${JSON.stringify(detail)}`];
  };
</script>

<OtherProfileScreen
  {token}
  {profile}
  on:show-all-wishlists={(event) => pushEvent('show-all-wishlists', event.detail)}
  on:show-all-subscriptions={(event) => pushEvent('show-all-subscriptions', event.detail)}
  on:open-wishlist={(event) => pushEvent('open-wishlist', event.detail)}
  on:open-profile={(event) => pushEvent('open-profile', event.detail)}
  on:share-profile={(event) => pushEvent('share-profile', event.detail)}
  on:toggle-subscribe={(event) => pushEvent('toggle-subscribe', event.detail)}
  on:back={() => pushEvent('back')}
/>

<ul data-testid="events-log">
  {#each events as eventName}
    <li>{eventName}</li>
  {/each}
</ul>
