<template>
<div class="dataset-entry box">
  <div class="dataset-title"><router-link :to="'/dataset/' + dataset.id"> {{ dataset.title }}</router-link></div>
  <div class="dataset-description" v-html="dataset.description"></div>
</div>
</template>

<script>
export default {
  name: 'DatasetEntry',
  props: ['dataset'],
}
</script>

<style scoped>
.dataset-title {
    font-weight: bold;
}
.dataset-entry {
    padding: 0.3em;
    margin: 0.4em;
    border-radius: 5px;
    border-style: solid;
    border-width: 0.5px;
}
</style>
