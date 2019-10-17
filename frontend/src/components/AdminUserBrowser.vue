<template>
<div class="user-browser">
  <table class="user-table" v-if="users.length > 0">
    <tr class="user-table-header">
      <th v-for="header in Object.keys(users[0])" :key="header">
        {{ header }}
      </th>
    </tr>
    <tr class="user-table-entry" v-for="user in users" :key="user.id">
      <td v-for="value in user" :key="value">
        {{value}}
      </td>
    </tr>
  </table>
</div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'AdminUserBrowser',
  data () {
    return {
      users: [],
      errorCode: null,
      errorText: null
    }
  },
  created () {
    axios
      .get('http://localhost:5000/api/users')
      .then((response) => (this.users = response.data.users))
      .catch(function (err) {this.errorCode = err.status;
                             this.errorText = err.statusText});
  }
}
</script>

<style scoped>

</style>
