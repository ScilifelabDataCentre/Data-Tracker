<template>
<div class="url">
  {{ urlData.description }} <a :href="urlData.url">Link</a>
</div>
</template>

<script>
export default {
  name: 'ProjectInfoUrl',
  props: ['urlData'],
}
</script>

<style scoped>

</style>
