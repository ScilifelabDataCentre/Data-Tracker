<template>
<div class="start-page">
  <section class="section">
    <h1 class="title is-1">SciLifeLab Data Tracker</h1>
    Welcome to the SciLifeLab Data Tracker, a system for tracking datasets generated at SciLifeLab.
  </section>
  <div class="columns">
    <div v-if="random_ds !== undefined" class="column">
      <div>
        <h2 class="title is-3">Random Dataset</h2>
        <browser-entry :entry="random_ds" entry_type="dataset"></browser-entry>
      </div>
    </div>
    <div v-if="random_proj !== undefined" class="column">
      <div>
        <h2 class="title is-3">Random Project</h2>
        <browser-entry :entry="random_proj" entry_type="project"></browser-entry>
      </div>
    </div>

  </div>
</div>
</template>

<script>
import BrowserEntry from '../components/BrowserEntry.vue';
import axios from 'axios';

export default {
  name: 'StartPage',

  data () {
    return {
      random_ds: undefined,
      random_proj: undefined,
    }
  },

  components: {
    'browser-entry': BrowserEntry,
  },

  mounted () {
    axios
      .get('/api/dataset/random/')
      .then((response) => {
        this.random_ds = response.data.datasets[0];
      });
    axios
      .get('/api/project/random/')
      .then((response) => {
        this.random_proj = response.data.projects[0];
      });

  },
}
</script>

<style scoped>

</style>
