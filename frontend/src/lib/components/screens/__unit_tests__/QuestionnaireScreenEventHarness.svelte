<script>
  import QuestionnaireScreen from '../QuestionnaireScreen.svelte';

  export let token = '';

  let events = [];

  const pushEvent = (eventName) => {
    events = [...events, eventName];
  };
</script>

<QuestionnaireScreen {token} on:back={() => pushEvent('back')} />

<ul data-testid="events-log">
  {#each events as eventName}
    <li>{eventName}</li>
  {/each}
</ul>
