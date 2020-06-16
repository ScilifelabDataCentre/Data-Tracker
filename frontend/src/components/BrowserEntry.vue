<template>
<div class="browser-entry card">
  <div class="card-content">
    <p class="has-text-weight-bold">
      <router-link :to="'/' + entry_type + '/' + entry._id"> {{ entry.title }}</router-link>
    </p>
    <div>
      {{ entry.description }}
    </div>
  </div>
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
  height: 7em;
  position: relative;
  overflow: hidden;
  margin-bottom: 0.5em;
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
</style>
