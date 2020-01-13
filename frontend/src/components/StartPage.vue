<template>
<div class="start-page">
  <section class="section">
    Welcome to the SciLifeLab Data Tracker, a system for tracking datasets generated at SciLifeLab.
  </section>
    <section class="section" v-if="random_ds">
      <h4 class="title is-4">
        Random Dataset
      </h4>
      <ds_entry :dataset="random_ds.dataset[0]"></ds_entry>
    </section>
</div>
</template>

<script>
import DatasetEntry from './datasets/DatasetEntry.vue';
import axios from 'axios';

export default {
  name: 'StartPage',

  data () {
    return {
      random_ds: null,
    }
  },

  components: {
    'ds_entry': DatasetEntry,
  },

  mounted () {
    axios
      .get('/api/dataset/random')
      .then((response) => {            
        this.random_ds = response.data;
      })
  },
}
</script>

<style scoped>

</style>
