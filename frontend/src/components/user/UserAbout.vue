<template>
<div class="user-about">
  <div v-if="!user.email">
    You need to log in before viewing this page.
  </div>
  <div v-else>
    <table class="table is-hoverable">
      <tbody>
        <tr><td class="data-header">Name</td> <td>{{user.name}}</td></tr>
        <tr><td class="data-header">Affiliation</td><td>{{user.affiliation}}</td></tr>
        <tr><td class="data-header">Email</td> <td>{{user.email}}</td></tr>
        <tr><td class="data-header">Country</td> <td>{{user.country}}</td></tr>
        <tr><td class="data-header">User type</td> <td>{{user.role}}</td></tr>
      </tbody>
    </table>

    <div>
      <table class="table is-hoverable is-striped is-fullwidth">
        <thead>
          <tr><th>Title</th><th>Something else</th></tr>
        </thead>
        <tbody>
          <tr><td>List of datasets received by user (order/receiver)</td><td>Some info</td></tr>
        </tbody>
      </table>
    </div>

    <div>
      <table class="table is-hoverable is-striped is-fullwidth">
        <thead>
          <tr><th>Title</th><th>Something else</th></tr>
        </thead>
        <tbody>
          <tr><td>List of orders owned by user (creator)</td><td>Some info</td></tr>
        </tbody>
      </table>
    </div>

    <div>
      <table class="table is-hoverable is-striped is-fullwidth">
        <thead>
          <tr><th>Title</th><th>Something else</th></tr>
        </thead>
        <tbody>
          <tr><td>List of projects owned by user</td><td>Some info</td></tr>
        </tbody>
      </table>
    </div>

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
