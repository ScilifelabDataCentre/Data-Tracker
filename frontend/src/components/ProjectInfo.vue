<template>
<div class="project-info">
  {{ projectInfo }}
</div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ProjectInfo',
  props: ['id'],
  data () {
    return {
      projectInfo: null,
      errorCode: null,
      errorText: null
    }
  },
  created () {
    axios
      .get('http://localhost:5000/api/dataset/' + this.id)
      .then((response) => (this.projectInfo = response.data))
      .catch(function (err) {this.errorCode = err.status;
                             this.errorText = err.statusText});
  }

}
</script>

<style scoped>

</style>
