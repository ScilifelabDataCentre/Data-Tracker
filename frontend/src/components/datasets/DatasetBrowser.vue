<template>
<div class="dataset-browser">
  <h4>Datasets</h4>
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
    ...mapGetters(['datasets']),
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
