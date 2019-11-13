<template>
<div class="project-browser">
  <h3 class="subtitle is-3">Projects</h3>
  <router-link v-if="user.permission === 'Steward' || user.permission === 'Admin'" to="add" class="add-entry">Add</router-link>
  <project-entry v-for="project in projects" :key="project.id" :project="project">
  </project-entry>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import ProjectEntry from './ProjectEntry.vue';

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
    'project-entry': ProjectEntry
  },
  created () {
    this.$store.dispatch('getProjects');
  },
}
</script>

<style scoped>

</style>
