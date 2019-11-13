<template>
<div class="user-about">
  <div v-if="!user.user">
    You need to log in before viewing this page.
  </div>
  <div v-if="user.user">
    <div>Name: {{user.user}}</div>
    <div>Affiliation: {{user.affiliation}}</div>
    <div>Email: {{user.email}}</div>
    <div>Country: {{user.country}}</div>
    <div>User type: {{user.permission}}</div>
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

</style>
