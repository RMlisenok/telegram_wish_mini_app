<script>
  import ShareProfileScreen from '../ShareProfileScreen.svelte';

  export let user;
  export let otherProfile = null;

  let events = [];

  const pushEvent = (eventName) => {
    events = [...events, eventName];
  };
</script>

<ShareProfileScreen {user} {otherProfile} on:back={() => pushEvent('back')} />

<ul data-testid="events-log">
  {#each events as eventName}
    <li>{eventName}</li>
  {/each}
</ul>
