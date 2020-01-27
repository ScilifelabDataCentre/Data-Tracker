<template>
<div class="user-manager">
  <div v-if="user.role !== 'Admin'">
    You do not have the permissions to view this page.
  </div>
  <div v-else>
    <table class="table is-hoverable is-striped" v-if="users.length > 0">
      <thead>
	<tr>
          <th v-for="header in Object.keys(users[0])" :key="header">
            {{ header }}
          </th>
	</tr>
      </thead>
      <tbody>
	<tr v-for="user in users" :key="user.id">
          <td v-for="value in user" :key="value">
            {{value}}
          </td>
	</tr>
      </tbody>
    </table>
  </div>
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
  }
}
</script>

<style scoped>

</style>
