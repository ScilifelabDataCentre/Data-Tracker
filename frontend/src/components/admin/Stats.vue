<template>
<div class="stats">
  List some stats, auto-generated figures, etc.
  Should also make an api where the figures can be requested.
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'Stats',
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
