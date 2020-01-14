<template>
<div class="start-page">
  <section class="section">
    Welcome to the SciLifeLab Data Tracker, a system for tracking datasets generated at SciLifeLab.
  </section>
  <div class="columns">
    <div class = "column" v-if="random_proj">
      <h4 class="title is-4">
        Random Project
      </h4>
      <proj_entry :project="random_proj.projects[0]"></proj_entry>
    </div>
    <div class = "column" v-if="random_ds">
      <h4 class="title is-4">
        Random Dataset
      </h4>
      <ds_entry :dataset="random_ds.datasets[0]"></ds_entry>
    </div>
  </div>
</div>
</template>

<script>
import DatasetEntry from './datasets/DatasetEntry.vue';
import ProjectEntry from './projects/ProjectEntry.vue';
import axios from 'axios';

export default {
  name: 'StartPage',

  data () {
    return {
      random_ds: null,
      random_proj: null,
    }
  },

  components: {
    'ds_entry': DatasetEntry,
    'proj_entry': ProjectEntry,
  },

  mounted () {
    axios
      .get('/api/dataset/random')
      .then((response) => {            
        this.random_ds = response.data;
      });
    axios
      .get('/api/project/random')
      .then((response) => {            
        this.random_proj = response.data;
      });

  },
}
</script>

<style scoped>

</style>
