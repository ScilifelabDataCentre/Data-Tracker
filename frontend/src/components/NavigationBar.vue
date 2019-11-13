<template>
<nav class="navbar" role="navigation" aria-label="main navigation">
  <router-link to="/" class="navbar-item"><span>Home</span></router-link>
  <router-link to="/project" class="navbar-item"><span>Projects</span></router-link>
  <router-link to="/dataset" class="navbar-item"><span>Datasets</span></router-link>
  <router-link to="/about" class="navbar-item"><span>About</span></router-link>
  <router-link v-if="user.permission === 'Admin'" to="/admin" class="navbar-item"><span>Admin</span></router-link>
  <div class="navbar-end">
    <div v-if="user.user" class="navbar-item has-dropdown is-hoverable">
      <a class="navbar-link">
        <span>{{ user.user }}</span>
      </a>
      <div class="navbar-dropdown">
        <router-link v-if="user.user" to="/user" class="navbar-item">Info</router-link>
        <a v-if="user.user" href="/logout" class="navbar-item">Logout</a>
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
.navigation-bar {
    padding: 5px 0px}
.navigation-link {
    padding: 0px 10px;
}
</style>
