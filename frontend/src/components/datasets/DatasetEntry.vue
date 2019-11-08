<template>
<div class="dataset-entry">
  <div class="dataset-title"><router-link :to="'/dataset/' + dataset.id"> {{ dataset.title }}</router-link></div>
  <div class="dataset-description">{{ dataset.description.substring(0, 100) }}</div>
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
