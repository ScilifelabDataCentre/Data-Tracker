<template>
<div class="navigation-bar">
  <router-link to="/" class="navigation-link"><span>Start</span></router-link>
  <router-link to="/projects" class="navigation-link"><span>Projects</span></router-link>
  <router-link to="/project/1" class="navigation-link"><span>Project 1</span></router-link>
</div>
</template>

<script>
export default {
  name: 'NavigationBar',
  data() {
    return {
    }
  }
}
</script>

<style scoped>
.navigation-bar {
    padding: 5px 0px}
.navigation-link {
    padding: 0px 10px;
}
</style>
