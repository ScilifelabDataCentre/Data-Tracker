<template>
<div class="project-browser">
  <h3 class="subtitle is-3">Projects</h3>
  <router-link v-if="user.permission === 'Steward' || user.permission === 'Admin'" to="add" class="add-entry">Add</router-link>
  <browser-entry v-for="project in projects" :key="project.id" :entry="project" entry_type="project">
  </browser-entry>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import BrowserEntry from '../BrowserEntry.vue';

export default {
  name: 'ProjectBrowser',
  data () {
    return {
    }
  },
  computed: {
    ...mapGetters(['projects', 'user']),
  },
  components: {
    'browser-entry': BrowserEntry
  },
  created () {
    this.$store.dispatch('getProjects');
  },
}
</script>

<style scoped>

</style>
