<template>
<div class="project-list-entry">
  {{ projectData.title }}
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
