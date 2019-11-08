<template>
<div class="project-entry">
  <div class="project-title"><router-link :to="'/project/' + project.id"> {{ project.title }}</router-link></div>
  <div class="project-description">{{ project.description.substring(0, 100) }}</div>
  <div class="project-contact">{{ project.contact }}a</div>
</div>
</template>

<script>
export default {
  name: 'ProjectEntry',
  props: ['project'],
}
</script>

<style scoped>
.project-title {
    font-weight: bold;
}
.project-entry {
    padding: 0.3em;
    margin: 0.4em;
    border-radius: 5px;
    border-style: solid;
    border-width: 0.5px;
}
</style>
