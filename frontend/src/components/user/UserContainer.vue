<template>
<div class="user-container">
  <router-view></router-view>
</div>
</template>

<script>
export default {
  name: 'UserContainer',
  components: {
  },
  data () {
    return {
    }
  },
}
</script>

<style scoped>
.user-container {
    text-align: left;
}
</style>
