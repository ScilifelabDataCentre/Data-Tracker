<template>
<div class="project-list">
  <h3>Projects:</h3>
  <project-entry v-for="project in projects" :key="project.id" :project="project">
  </project-entry>
</div>
</template>

<script>
import ProjectListEntry from './ProjectListEntry.vue';
import {mapGetters} from 'vuex';

export default {
  name: 'ProjectList',
  computed: {
    ...mapGetters(['projects']),
  },
  components: {
    'project-entry': ProjectListEntry
  }
}
</script>

<style scoped>

</style>
