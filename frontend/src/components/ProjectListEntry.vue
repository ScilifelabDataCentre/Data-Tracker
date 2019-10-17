<template>
<div class="project-list">
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
