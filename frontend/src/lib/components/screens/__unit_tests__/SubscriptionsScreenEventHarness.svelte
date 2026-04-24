<script>
  import SubscriptionsScreen from '../SubscriptionsScreen.svelte';

  export let token = '';

  let events = [];

  const pushEvent = (name, detail = null) => {
    events = [...events, detail == null ? name : `${name}:${JSON.stringify(detail)}`];
  };
</script>

<SubscriptionsScreen
  {token}
  on:open-profile={(event) => pushEvent('open-profile', event.detail)}
  on:openWishlistDetail={(event) => pushEvent('openWishlistDetail', event.detail)}
/>

<ul data-testid="events-log">
  {#each events as eventName}
    <li>{eventName}</li>
  {/each}
</ul>
