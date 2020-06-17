<template>
<div class="project-browser">
  <h1 class="title is-1">Projects</h1>
  <router-link class="button is-link" to="add">
    Add
  </router-link>
  <browser-entry v-for="project in projects" :key="project.id" :entry="project" entry_type="project">
  </browser-entry>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import BrowserEntry from '../../components/BrowserEntry.vue';

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
