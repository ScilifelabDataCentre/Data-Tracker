<template>
<div class="dataset-info">
  <div class="warning" v-if="Object.keys(dataset).length === 0">
    <span>Unable to retrieve dataset</span>
  </div>
  <div v-else>
    <h1 class="title is-2">{{ dataset.title }}</h1>
    <div class="dataset-description field" v-html="dataset.description"></div>
    <table class="table is-hoverable">
      <tbody>
        <tr v-if="dataset.creator"><td class="data-header">Creator</td><td>{{ dataset.creator }}</td></tr>
        <tr v-if="dataset.doi"><td class="data-header">DOI</td><td>{{ dataset.doi }}</td></tr>
        <tr v-if="dataset.dmp"><td class="data-header"><abbr title="Data management plan">DMP</abbr></td><td><a :href="dataset.dmp">{{ dataset.dmp }}</a></td></tr>
        <tr v-if="dataset.dataUrls.length > 0">
        <tr class="test" v-for="(location, index) in dataset.dataUrls" :key="location.id">
          <td class="data-header"><span v-if="index === 0">Data locations</span></td>
          <td class="test"><a :href="location.url">{{location.description}}</a></td>
        </tr>
        <tr class="test" v-for="(publication, index) in dataset.publications" :key="publication.id">
          <td class="data-header"><span v-if="index === 0">Publications</span></td>
          <td class="test"><a :href="publication.url">{{publication}}</a></td>
        </tr>
        <tr class="test" v-for="(project, index) in dataset.projects" :key="project.id">
          <td class="data-header"><span v-if="index === 0">Projects</span></td>
          <td class="test"><router-link :to="'/project/' + project.uuid + '/about'">{{project.title}}</router-link></td>
        </tr>
      </tbody>
    </table>
    <span class="timestamp">Last update: {{ dataset.timestamp }}</span>
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
  props: ['uuid'],
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
    this.$store.dispatch('getDataset', this.uuid);
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

.field-header.td {
    font-weight: bold;
}

.field {
    margin: 0.4em 0em;
}

.table td {
    border: 0px;
}
.warning {
    font-weight: bold;
    text-align: center;
    font-size: large;
}
.timestamp {
    font-style: italic;
    font-size: 1em;
}
</style>
