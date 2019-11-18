<template>
<div class="user-about">
  <div v-if="!user.user">
    You need to log in before viewing this page.
  </div>
  <div v-else>
    <table class="table">
      <tr><td class="data-header">Name</td> <td>{{user.user}}</td></tr>
      <tr><td class="data-header">Affiliation</td><td>{{user.affiliation}}</td></tr>
      <tr><td class="data-header">Email</td> <td>{{user.email}}</td></tr>
      <tr><td class="data-header">Country</td> <td>{{user.country}}</td></tr>
      <tr><td class="data-header">User type</td> <td>{{user.permission}}</td></tr>
    </table>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'UserAbout',
  data () {
    return {
    }
  },
  computed: {
    ...mapGetters(['user']),
  },
  created () {
    this.$store.dispatch('getUser', this.id);
  }
}
</script>

<style scoped>
.data-header {
    text-align: right;
    font-weight: bold;
}
</style>
