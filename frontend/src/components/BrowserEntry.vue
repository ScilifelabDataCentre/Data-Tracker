<template>
<div class="browser-entry card">
  <div class="card-content">
    <p class="has-text-weight-bold">
      <router-link :to="'/' + entry_type + '/' + entry._id"> {{ entry.title }}</router-link>
    </p>
    <vue-simple-markdown :source="entry.description"></vue-simple-markdown>
  </div>
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
  max-height: 15em;
  position: relative;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 0.5em;
}

.browser-entry:after {
  content: "";
  position: absolute;
  top: 13em;
  left: 0;
  height: 2em;
  width: 100%; 
  background: linear-gradient(rgba(255,255,255,0), #FFF);
}
</style>
