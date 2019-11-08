<template>
<div class="navigation-bar">
  <router-link to="/" class="navigation-link"><span>Start</span></router-link>
  <router-link to="/project" class="navigation-link"><span>Projects</span></router-link>
  <router-link to="/dataset" class="navigation-link"><span>Datasets</span></router-link>
  <router-link v-if="user.user" to="/user" class="navigation-link"><span>User</span></router-link>
  <router-link v-if="user.permission === 'Admin'" to="/admin" class="navigation-link"><span>Admin</span></router-link>
</div>
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
