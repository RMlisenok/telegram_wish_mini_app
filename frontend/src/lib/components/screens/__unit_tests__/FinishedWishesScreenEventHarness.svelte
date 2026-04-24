<script>
  import FinishedWishesScreen from '../FinishedWishesScreen.svelte';

  export let token = '';

  let events = [];

  const pushEvent = (eventName) => {
    events = [...events, eventName];
  };
</script>

<FinishedWishesScreen {token} on:back={() => pushEvent('back')} />

<ul data-testid="events-log">
  {#each events as eventName}
    <li>{eventName}</li>
  {/each}
</ul>
