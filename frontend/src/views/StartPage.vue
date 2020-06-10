<template>
<div class="start-page">
  <section class="section">
    <h1 class="title is-1">SciLifeLab Data Tracker</h1>
    Welcome to the SciLifeLab Data Tracker, a system for tracking datasets generated at SciLifeLab.
  </section>
  <div class="columns">
    <div class="column">
      <div v-if="random_proj !== {}">
        <h2 class="title is-4">Random Project</h2>
        <browser-entry :entry="random_proj.projects[0]" entry_type="project"></browser-entry>
      </div>
    </div>
    <div class="column">
      <div v-if="random_ds !== {}">
        <h2 class="title is-4">Random Dataset</h2>
        <browser-entry :entry="random_ds.datasets[0]" entry_type="dataset"></browser-entry>
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
      random_ds: {},
      random_proj: {},
    }
  },

  components: {
    'browser-entry': BrowserEntry,
  },

  mounted () {
    axios
      .get('/api/dataset/random/')
      .then((response) => {            
        this.random_ds = response.data;
      });
    axios
      .get('/api/project/random/')
      .then((response) => {            
        this.random_proj = response.data;
      });

  },
}
</script>

<style scoped>

</style>
