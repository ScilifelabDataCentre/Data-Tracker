<template>
<div class="project-browser">
  <project-list></project-list>
</div>
</template>

<script>
import ProjectList from './ProjectList.vue';

export default {
  name: 'ProjectBrowser',
  data () {
    return {
    }
  },
  components: {
    'project-list': ProjectList
  },
  created () {
    this.$store.dispatch('getProjects');
  }
}
</script>

<style scoped>

</style>
