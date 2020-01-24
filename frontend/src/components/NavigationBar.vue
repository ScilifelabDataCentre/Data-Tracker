<template>
<nav class="navbar" role="navigation" aria-label="main navigation">
  <div class="navbar-start">
    <div class="navbar-item">
      SciLifeLab Data Tracker
    </div>
  </div>
  <router-link to="/" class="navbar-item"><img id="home-icon" :src="require('../assets/open-iconic/svg/home.svg')" alt="home"></router-link>
  <router-link to="/project" class="navbar-item">Projects</router-link>
  <router-link to="/dataset" class="navbar-item">Datasets</router-link>
  <router-link to="/about" class="navbar-item">About us</router-link>
  <div v-if="user.role === 'Admin'" class="navbar-item has-dropdown is-hoverable">
    <a class="navbar-link">Admin</a>
    <div class="navbar-dropdown">
      <router-link to="/admin/users" class="navbar-item">User management</router-link>
      <router-link to="/admin/stats" class="navbar-item">Statistics</router-link>
    </div>
  </div>
  <div class="navbar-end">
    <div v-if="user.name" class="navbar-item has-dropdown is-hoverable">
      <a class="navbar-link">{{ user.name }}</a>
      <div class="navbar-dropdown">
        <router-link to="/user" class="navbar-item">Info</router-link>
        <a href="/api/user/logout" class="navbar-item">Logout</a>
      </div>
    </div>
    <a v-else href="/elixir/login" class="navbar-item">Log in</a>
  </div>
</nav>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'NavigationBar',
  computed: {
    ...mapGetters(['user']),
  },
  data() {
    return {
    }
  }
}
</script>

<style scoped>
#home-icon {
    height:12px;
    width:12px;
}
</style>
