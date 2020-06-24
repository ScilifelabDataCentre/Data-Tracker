<template>
<div class="dataset-info">
  <div v-if="Object.keys(dataset).length > 0">
    <h1 class="title is-2">{{ dataset.title }}</h1>
    <section class="section">
      <div class="content">
	<vue-simple-markdown :source="dataset.description"></vue-simple-markdown>
      </div>
    </section>
    <section class="section">
      <table class="info-list table is-hoverable is-striped">
	<tbody>
          <tr v-if="dataset.creator.length > 0">
            <th scope="row">
              Creator
            </th>
            <td>
              {{ dataset.creator }}
            </td>
          </tr>
          <tr v-if="dataset.links.length > 0">
            <th scope="row">
              Links
            </th>
            <td>
              <ul v-for="location in dataset.links" :key="location.url">
		<li class="test"><a :href="location.url">{{location.description}}</a></li>
              </ul>
            </td>
          </tr>
          <tr v-for="field in Object.keys(dataset.extra)" :key="field">
            <th scope="row">{{ field | capitalize }}</th>
            <td>{{ dataset.extra[field] }}</td>
          </tr>
          <tr v-if="dataset.projects.length > 0">
            <th scope="row">
              Projects
            </th>
            <td>
              <ul v-for="project in dataset.projects" :key="project._id">
		<li class="test"><a :href="'/project/' + project._id">{{project.title}}</a></li>
              </ul>
            </td>
          </tr>
          <tr v-if="dataset.related.length > 0">
            <th scope="row">
              Related datasets
            </th>
            <td>
              <ul v-for="dataset in dataset.related" :key="dataset._id">
		<li class="test"><a :href="'/dataset/' + dataset._id">{{dataset.title}}</a></li>
              </ul>
            </td>
          </tr>
	</tbody>
      </table>
    </section>
  </div>

    <div v-if="dataset.creator === user.name || user.permissions.includes('DATA_MANAGEMENT')" class="field is-grouped">
    <div class="control">
      <router-link to="edit">
        <button class="button is-link">
          Edit
        </button>
      </router-link>
    </div>
    <div class="control">
      <router-link to="log">
        <button class="button is-light">
          Logs
        </button>
      </router-link>
    </div>
  </div>
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
    ...mapGetters(['dataset', 'user']),
  },
  data () {
    return {
    }
  },
  mounted () {
    this.$store.dispatch('getDataset', this.uuid);
  },
}
</script>

<style scoped>
.info-list th {
  text-align: right;
}
</style>
