<template>
<div class="project-browser">
  <h4>Projects</h4>
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
    ...mapGetters(['projects']),
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
