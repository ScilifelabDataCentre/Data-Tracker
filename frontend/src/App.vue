<template>
<div id="app">
  <h1 class="title is-1">SciLifeLab Data Tracker</h1>
  <nav-bar></nav-bar>
  <router-view class="container"></router-view>
  <footer class="footer">
    <img class="logo" :src="require('./assets/img/data-centre-logo.png')" alt="SciLife Data Centre logo"/>
  </footer>
</div>
</template>

<script>
import NavigationBar from './components/NavigationBar.vue';

export default {
  name: 'App',
  components: {
    'nav-bar': NavigationBar
  },
  data() {
    return {
    }
  },
  created () {
    this.$store.dispatch('getUser');
  },
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
img.logo {
    height: 100px;
}
</style>
