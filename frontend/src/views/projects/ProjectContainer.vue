<template>
<div class="project-container">
  <router-view></router-view>
</div>
</template>

<script>
export default {
  name: 'ProjectContainer',
  components: {
  },
  data () {
    return {
    }
  },
}
</script>

<style scoped>
.project-container {
    text-align: left;
}

.warning {
    font-weight: bold;
    text-align: center;
    font-size: large;
}
</style>
