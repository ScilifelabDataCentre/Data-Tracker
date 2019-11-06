<template>
<div class="project-container">
</div>
</template>

<script>

export default {
  name: 'ProjectContainer',
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
h1 {
    text-align: center;
}

.project-info {
    text-align: left;
}

.field-header {
    font-weight: bold;
}

.warning {
    font-weight: bold;
    text-align: center;
    font-size: large;
}
</style>
