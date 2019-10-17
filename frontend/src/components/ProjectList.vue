<template>
<div class="project-list">
  <h3>Projects:</h3>
  <project-entry v-for="project in projects" :key="project.id" :projectData="project">
  </project-entry>
</div>
</template>

<script>
import ProjectListEntry from './ProjectListEntry.vue';

export default {
  name: 'ProjectList',
  props: ['projects'],
  components: {
    'project-entry': ProjectListEntry
  }
}
</script>

<style scoped>

</style>
