<template>
<div class="dataset-browser">
  <h3 class="subtitle is-3">Datasets</h3>
  <button class="button is-link" v-if="user.role === 'Steward' || user.role === 'Admin'" @click="addDataset">
    Add
  </button>
  <browser-entry v-for="dataset in datasets" :key="dataset.id" :entry="dataset" entry_type="dataset">
  </browser-entry>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import BrowserEntry from '../BrowserEntry.vue';

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
  methods: {
    addDataset(event) {
      event.preventDefault();
      this.$router.push("/dataset/add");
    },
  },

}
</script>

<style scoped>

</style>
