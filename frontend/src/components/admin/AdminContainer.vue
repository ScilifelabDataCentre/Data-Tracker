<template>
<div class="admin-container">
  <router-view></router-view>
</div>
</template>

<script>
export default {
  name: 'AdminContainer',
  components: {
  },
  data () {
    return {
    }
  },
}
</script>

<style scoped>
.admin-container {
    text-align: left;
}
</style>
