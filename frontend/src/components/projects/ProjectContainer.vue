<template>
<div class="project-container">
  <router-view></router-view>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'ProjectContainer',
  props: ['id'],
  components: {
  },
  computed: {
    ...mapGetters(['project']),
  },
  data () {
    return {
    }
  },
  created () {
    this.$store.dispatch('getProject', this.id);
  }
}
</script>

<style scoped>
.project-container {
    text-align: left;
}

.warning {
    font-weight: bold;
    text-align: center;
    font-size: large;
}
</style>
