<template>
<div class="dataset-browser">
  <h1 class="title is-1">Datasets</h1>
  <browser-entry v-for="dataset in datasets" :key="dataset.id" :entry="dataset" entry_type="dataset">
  </browser-entry>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import BrowserEntry from '../../components/BrowserEntry.vue';

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
    'browser-entry': BrowserEntry
  },
  created () {
    this.$store.dispatch('getDatasets');
  },
}
</script>
