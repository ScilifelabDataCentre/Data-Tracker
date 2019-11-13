<template>
<div class="dataset-browser">
  <h3 class="subtitle is-3">Datasets</h3>
  <router-link v-if="user.permission === 'Steward' || user.permission === 'Admin'" to="add" class="add-entry">Add</router-link>
  <dataset-entry v-for="dataset in datasets" :key="dataset.id" :dataset="dataset">
  </dataset-entry>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import DatasetEntry from './DatasetEntry.vue';

export default {
  name: 'DatasetBrowser',
  data () {
    return {
    }
  },
  computed: {
    ...mapGetters(['datasets', 'user']),
  },
  components: {
    'dataset-entry': DatasetEntry
  },
  created () {
    this.$store.dispatch('getDatasets');
  },
}
</script>

<style scoped>

</style>
