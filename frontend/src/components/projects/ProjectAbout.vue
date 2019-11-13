<template>
<div class="project-info">
  <div class="warning" v-if="Object.keys(project).length === 0">
    <span>Unable to retrieve project</span>
  </div>
  <div v-id="project">
    <div class="project-title">{{ project.title }}</div>
    <div class="project-description field" v-html="project.description"></div>
    <div class="project-contact field"><span class="field-header">Contact:</span> {{ project.contact }}</div>
    <div class="project-datasets field">
      <span class="field-header">Datasets:</span>
      <div class="project-dataset" v-for="dataset in project.datasets" :key="dataset">
	<router-link :to="'/dataset/' + dataset + '/about'">{{ dataset }}</router-link>
      </div>
    </div>
  </div>
  <router-link to="edit">Edit</router-link>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'ProjectAbout',
  props: ['id'],
  components: {
  },
  computed: {
    ...mapGetters(['project', 'user']),
  },
  data () {
    return {
    }
  },
  created () {
    this.$store.dispatch('getProject', this.id);
  },

}
</script>

<style scoped>
.project-title {
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
