<template>
<div class="user-browser">
  <div>

    <h2 id="doi-request-title" class="title is-2">Requested DOIs</h2>
    <table class="table is-hoverable is-striped" aria-describedby="doi-request-title">
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

    
    <h2 id="doi-title" class="title is-2">DOIs</h2>
    <table class="table is-hoverable is-striped" aria-describedby="doi-request-title">
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
