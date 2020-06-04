<template>
<div class="user-manager">
  <h1 id="user-table-header" class="title is-1">List of users</h1>
  <router-link to="user/add">
    <img class="icon-add" :src="require('../../assets/open-iconic/svg/plus.svg')" alt="Add" />
  </router-link>
  <table class="table is-hoverable is-striped" v-if="users.length > 0" aria-describedby="user-table-header">
    <thead>
      <tr>
        <th scope="col">Name</th>
        <th scope="col">Authentication ID</th>
        <th scope="col">Email</th>
        <th scope="col">Affiliation</th>
      </tr>
    </thead>
    <tbody>
      <tr v @click="editUser($event, user._id)" v-for="user in users" :key="user._id">
        <td>{{user.name}}</td>
        <td>{{user.authId}}</td>
        <td>{{user.email}}</td>
        <td>{{user.affiliation}}</td>
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

  methods: {
    editUser(event, uuid) {
      event.preventDefault();
      this.$router.push('/admin/user/' + uuid);
    }
  }
}
</script>
