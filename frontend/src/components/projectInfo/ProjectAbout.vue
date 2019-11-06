<template>
<div class="project-info">
  <div class="warning" v-if="!project">
    <span>Unable to retrieve project</span>
  </div>
  <div v-id="project">
    <div class="project-title">{{ project.title }}</div>
    <div class="project-description">{{ project.description }}</div>
    <div class="project-contact"><span class="field-header">Contact:</span> {{ project.contact }}</div>
    <div class="project-datasets"><span class="field-header">Datasets:</span> <div class="project-dataset" v-for="dataset in project.datasets" :key="dataset">{{ dataset }}</div></div>
  </div>
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
    ...mapGetters(['project']),
  },

  data () {
    return {
      projectInfo: null,
      errorCode: null,
      errorText: null
    }
  },
  created () {
    this.$store.dispatch('getProject', this.id);
  }
}
</script>

<style scoped>
h1 {
    text-align: center;
}

.project-title {
    font-weight: bold;
}

.field-header {
    font-weight: bold;
}

.warning {
    font-weight: bold;
    text-align: center;
    font-size: large;
}
</style>
