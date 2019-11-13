<template>
<div class="dataset-info">
  <div class="warning" v-if="Object.keys(dataset).length === 0">
    <span>Unable to retrieve dataset</span>
  </div>
  <div v-if="Object.keys(dataset).length > 0">
    <div class="dataset-title">{{ dataset.title }}</div>
    <div class="dataset-description field">{{ dataset.description }}</div>
    <div class="dataset-creator field"><span class="field-header">Creator:</span> {{ dataset.creator }}</div>
    <div>
      <span class="field-header">Projects:</span>
      <div class="dataset-project" v-for="project in dataset.projects" :key="project">
	<router-link :to="'/project/' + project + '/about'">{{ project }}</router-link>
      </div>
    </div>
  </div>
  <router-link to="edit">Edit</router-link>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'DatasetAbout',
  props: ['id'],
  components: {
  },
  computed: {
    ...mapGetters(['dataset']),
  },
  data () {
    return {
    }
  },
  created () {
    this.$store.dispatch('getDataset', this.id);
  },

}
</script>

<style scoped>
.dataset-title {
    font-weight: bold;
    font-size: 2em;
    text-align: center;
    margin: 0em 0em 0.4em 0em;
}

.field-header {
    font-weight: bold;
}

.field {
    margin: 0.4em 0em;
}

.warning {
    font-weight: bold;
    text-align: center;
    font-size: large;
}
</style>
