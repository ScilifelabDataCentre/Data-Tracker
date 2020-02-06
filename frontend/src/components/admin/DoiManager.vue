<template>
<div class="user-browser">
  <div>

    Requested DOIs
    <table class="table is-hoverable is-striped">
      <thead>
        <tr>
          <th scope="col">Data type</th>
          <th scope="col">Internal ID</th>
        </tr>
      </thead>
      <tbody>
      <tr>
        <td>Dataset</td>
        <td>ade661ed-0b0e-4489-a879-233eb44c8bf1</td>
      </tr>
      </tbody>
    </table>

    
    DOIs
    <table class="table is-hoverable is-striped">
      <thead>
        <tr>
          <th scope="col">DOI</th>
          <th scope="col">Data type</th>
          <th scope="col">Internal ID</th>
        </tr>
      </thead>
      <tbody>
      <tr>
        <td>DOI identifier</td>
        <td>Dataset</td>
        <td>ade661ed-0b0e-4489-a879-233eb44c8bf1</td>
      </tr>
      </tbody>
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
