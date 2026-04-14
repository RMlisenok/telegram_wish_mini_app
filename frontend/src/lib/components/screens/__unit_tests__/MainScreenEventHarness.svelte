<script>
  import MainScreen from '../MainScreen.svelte';

  export let token = '';
  export let user;

  let events = [];

  const pushEvent = (eventName) => {
    events = [...events, eventName];
  };
</script>

<MainScreen
  {token}
  {user}
  on:openSettings={() => pushEvent('openSettings')}
  on:openQuestionnaire={() => pushEvent('openQuestionnaire')}
  on:openWishes={() => pushEvent('openWishes')}
  on:openWishlists={() => pushEvent('openWishlists')}
  on:openSubscriptions={() => pushEvent('openSubscriptions')}
  on:openSubscribers={() => pushEvent('openSubscribers')}
  on:openShareProfile={() => pushEvent('openShareProfile')}
  on:openCreateWishlists={() => pushEvent('openCreateWishlists')}
/>

<ul data-testid="events-log">
  {#each events as eventName}
    <li>{eventName}</li>
  {/each}
</ul>
