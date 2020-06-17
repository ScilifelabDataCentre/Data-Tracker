<template>
<nav class="navbar" role="navigation" aria-label="main navigation">
  <div class="navbar-brand">
    <router-link to="/" class="navbar-item has-text-weight-bold">
      Data Tracker
    </router-link>
    <a role="button"
       class="navbar-burger burger"
       aria-label="menu"
       aria-expanded="false"
       @click="showMenu = !showMenu">
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
    </a>
  </div>

  <div class="navbar-menu" id="navbarMenu" :class="{'navbar-menu': true, 'is-active': showMenu}">
    <div class="navbar-start">
      <router-link  v-if="user.permissions.includes('DATA_MANAGEMENT') || user.permissions.includes('ORDERS_SELF')" to="/order" class="navbar-item">Orders</router-link>
      <router-link to="/dataset" class="navbar-item">Datasets</router-link>
      <router-link to="/project" class="navbar-item">Projects</router-link>
      <router-link to="/search" class="navbar-item">Search</router-link>
      <router-link to="/about" class="navbar-item">About</router-link>
      <div v-if="user.permissions.includes('USER_MANAGEMENT')" class="navbar-item has-dropdown is-hoverable">
        <a class="navbar-link">Admin</a>
        <div class="navbar-dropdown">
          <router-link to="/admin/stats" class="navbar-item">Statistics</router-link>
          <router-link to="/admin/user/list" class="navbar-item">User management</router-link>
        </div>
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
      <div v-else class="navbar-item has-dropdown is-hoverable">
        <a class="navbar-link">Log In</a>
        <div class="navbar-dropdown">
          <a class="navbar-item" href="/api/user/login/">Elixir AAI</a>
          <router-link to="/login/key" class="navbar-item">API key</router-link>
        </div>
      </div>
    </div>
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
      'showMenu': false,
    }
  }
}
</script>

<style scoped>
.icon-home {
    height:1em;
    width:1em;
}
</style>
