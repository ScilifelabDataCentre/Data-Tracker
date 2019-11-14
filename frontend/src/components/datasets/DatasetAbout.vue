<template>
<div class="dataset-info">
  <div class="warning" v-if="Object.keys(dataset).length === 0">
    <span>Unable to retrieve dataset</span>
  </div>
  <div v-else>
    <h1 class="title is-2">{{ dataset.title }}</h1>
    <div class="dataset-description field" v-html="dataset.description"></div>
    <table class="table">
      <tr v-if="dataset.creator"><td class="data-header">Creator</td><td>{{ dataset.creator }}</td></tr>
      <tr v-if="dataset.doi"><td class="data-header">DOI</td><td>{{ dataset.doi }}</td></tr>
      <tr v-if="dataset.dmp"><td class="data-header">DMP</td><td>{{ dataset.dmp }}</td></tr>
    </table>
    
    <div v-if="dataset.dataUrls">
      <h2 class="title is-5">Data locations</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Description</th><th>URL</th>
          </tr>
        </thead>
        <tr v-for="location in dataset.dataUrls" :key="location.id">
          <td>{{location.description}}</td><td>{{location.url}}</td>
        </tr>
      </table>
    </div>
    <div v-if="dataset.publications">
      <h2 class="title is-5">Publications</h2>
      <table class="table">
        <tr v-for="publication in dataset.publications" :key="publication.id">
          <td>{{publication.identifier}}</td>
        </tr>
      </table>
    </div>
    <div v-if="dataset.tags">
      <h2 class="title is-5">Tags</h2>
      <table class="table">
        <tr v-for="tag in dataset.tags" :key="tag.id">
          <td>{{tag.title}}</td>
        </tr>
      </table>
    </div>
    <div v-if="dataset.projects">
      <h2 class="title is-5">Projects</h2>
      <div class="dataset-project" v-for="project in dataset.projects" :key="project">
	<router-link :to="'/project/' + project + '/about'">{{ project }}</router-link>
      </div>
    </div>
  </div>
  <button class="button is-link" @click="editDataset">
    Edit
  </button>
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
  methods: {
    editDataset(event) {
      event.preventDefault();
      this.$router.push("/dataset/" + this.$props.id + "/edit");
    },
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

.data-header {
    text-align: right;
    font-weight: bold;
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
