<script>
  import StartScreen from '../StartScreen.svelte';

  let events = [];

  const pushEvent = (eventName) => {
    events = [...events, eventName];
  };
</script>

<StartScreen on:start={() => pushEvent('start')} />

<ul data-testid="events-log">
  {#each events as eventName}
    <li>{eventName}</li>
  {/each}
</ul>
