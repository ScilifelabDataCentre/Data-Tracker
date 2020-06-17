<template>
<div class="user-manager">
  <h1 id="user-table-header" class="title is-1">List of users</h1>
  <router-link class="button is-link" to="add">
    Add
  </router-link>
  <table class="table is-hoverable is-striped" v-if="users.length > 0" aria-describedby="user-table-header">
    <thead>
      <tr>
        <th scope="col">Name</th>
        <th scope="col">Authentication ID</th>
        <th scope="col">Email</th>
        <th scope="col">Affiliation</th>
	<th scope="col">Edit</th>
	<th scope="col">Logs</th>
	<th scope="col">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="user in users" :key="user._id">
        <td>{{user.name}}</td>
        <td>{{user.authId}}</td>
        <td>{{user.email}}</td>
        <td>{{user.affiliation}}</td>
	<td><router-link :to="user._id + '/edit'"><button class="button is-link">E</button></router-link></td>
	<td><router-link :to="user._id + '/log'"><button class="button is-light is-link">L</button></router-link></td>
        <td><router-link :to="user._id + '/actions'"><button class="button is-light is-danger">A</button></router-link></td>
      </tr>
    </tbody>
  </table>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'UserManager',

  data () {
    return {
    }
  },

  computed: {
    ...mapGetters(['user', 'users']),
  },

  created () {
    this.$store.dispatch('getUsers', this.id);
  },
}
</script>
