<template>
<div class="dataset-browser">
  <h3 class="subtitle is-3">Datasets</h3>
  <router-link v-if="user.role === 'Steward' || user.role === 'Admin'" to="/dataset/add">
    <img class="icon-add" :src="require('../../assets/open-iconic/svg/plus.svg')" alt="Add" />
  </router-link>
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
}
</script>

<style scoped>
.icon-add {
  width: 1.2em;
  height: 1.2em;
}
</style>
