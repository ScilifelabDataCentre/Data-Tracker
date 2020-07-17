<template>
  <q-page padding>
    <!-- content -->
  </q-page>
</template>

<script>
export default {
  name: 'UserManager',

  data () {
    return {
    }
  },

  computed: {
    dataset: {
      get () {
        return this.$store.state.adminUser.userList;
      },
    },
  },

  created () {
    this.$store.dispatch('adminUser/getUsers');
  },
}
</script>
