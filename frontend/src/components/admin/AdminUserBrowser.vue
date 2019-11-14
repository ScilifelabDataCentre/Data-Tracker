<template>
<div class="user-browser">
  <div v-if="user.permission !== 'Admin'">
    You do not have the permissions to view this page.
  </div>
  <div v-if="user.permission === 'Admin'">
    <table class="table" v-if="users.length > 0">
      <thead>
	<tr class="user-table-header">
          <th v-for="header in Object.keys(users[0])" :key="header">
            {{ header }}
          </th>
	</tr>
      </thead>
      <tr class="user-table-entry" v-for="user in users" :key="user.id">
        <td v-for="value in user" :key="value">
          {{value}}
        </td>
      </tr>
    </table>
  </div>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'AdminUserBrowser',
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
