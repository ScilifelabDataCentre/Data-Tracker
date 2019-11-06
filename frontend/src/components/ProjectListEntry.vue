<template>
<div class="project-list-entry">
  <div class="project-title"><router-link :to="'/project/' + project.id + '/about'"> {{ project.title }}</router-link></div>
  <div class="project-description">{{ project.description }}</div>
  <div class="project-contact">{{ project.contact }}a</div>
</div>
</template>

<script>
export default {
  name: 'ProjectListEntry',
  props: ['project'],
}
</script>

<style scoped>
.project-title {
    font-weight: bold;
}
.project-list-entry {
    padding: 10px 0px;
}
</style>
