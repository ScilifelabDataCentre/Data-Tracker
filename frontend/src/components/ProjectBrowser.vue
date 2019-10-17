<template>
<div class="project-browser">
  <project-list :projects="projects"></project-list>
</div>
</template>

<script>
import axios from 'axios';
import ProjectList from './ProjectList.vue';

export default {
  name: 'ProjectBrowser',
  data () {
    return {
      projects: null,
      errorCode: null,
      errorText: null
    }
  },
  components: {
    'project-list': ProjectList
  },
  created () {
    axios
      .get('http://localhost:5000/api/datasets')
      .then((response) => (this.projects = response.data.datasets))
      .catch(function (err) {this.errorCode = err.status;
                             this.errorText = err.statusText});
  }
}
</script>

<style scoped>

</style>
