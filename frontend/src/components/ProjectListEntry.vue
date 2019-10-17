<template>
<div class="project-list-entry">
  <router-link :to="`/project/${projectData.id}`">
    <span class="project-list-entry-title">{{ projectData.title }}</span>
  </router-link>
</div>
</template>

<script>
export default {
  name: 'ProjectListEntry',
  props: ['projectData'],
  data () {
    return {
    }
  },
}
</script>

<style scoped>

</style>
