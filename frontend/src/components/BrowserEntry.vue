<template>
<div class="browser-entry box">
  <div class="entry-title"><router-link :to="'/' + entry_type + '/' + entry.uuid"> {{ entry.title }}</router-link></div>
  <div v-html="entry.description"></div>
  <div class="fade-helper"></div>
</div>
</template>

<script>
export default {
  name: 'BrowserEntry',
  props: ['entry', 'entry_type'],
}
</script>

<style scoped>
.browser-entry {
  height: 120px;
  position: relative;
  overflow: hidden;
}
.browser-entry .fade-helper { 
  position: absolute;
  bottom: 0; 
  left: 0;
  width: 100%; 
  margin: 0;
  padding: 1.5em 0;
  background-image: linear-gradient(to bottom, transparent, white);
}

.dataset-title {
    font-weight: bold;
}
</style>
