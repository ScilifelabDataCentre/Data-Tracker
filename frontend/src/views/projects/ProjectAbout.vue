<template>
<div class="project-info">
  <div v-if="Object.keys(project).length > 0">
    <h1 class="title is-2">{{ project.title }}</h1>
    <div class="project-description field" v-html="project.description"></div>
    <table class="table is-hoverable is-striped">
      <tbody>
        <tr v-if="project.contact.length > 0">
          <th scope="row">
            Contact
          </th>
          <td>
            {{ project.contact }}
          </td>
        </tr>
        <tr v-if="project.dmp.length > 0">
          <th scope="row">
            Data Management Plan
          </th>
          <td>
            {{ project.dmp }}
          </td>
        </tr>
        <tr v-if="project.datasets.length > 0">
          <th scope="row">
            Datasets
          </th>
          <td>
            <ul v-for="dataset in project.datasets" :key="dataset._id">
              <li><a :href="'/dataset/' + dataset._id">{{ dataset.title }}</a></li>
            </ul>
          </td>
        </tr>
        <tr v-for="field in Object.keys(project.extra)" :key="field">
          <th scope="row">{{ field }}</th>
          <td>{{ project.extra[field] }}</td>
        </tr>
        <tr v-if="project.publications.length > 0">
          <th scope="row">
            Publications
          </th>
          <td>
            <ul v-for="publication in project.publications" :key="publication">
              <li>{{ publication }}</li>
            </ul>
          </td>
        </tr>

      </tbody>
    </table>
  </div>

  <div v-if="project.owners" class="field is-grouped">
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
  name: 'ProjectAbout',
  props: ['uuid'],
  components: {
  },
  computed: {
    ...mapGetters(['project', 'user']),
  },
  data () {
    return {
    }
  },
  mounted () {
    this.$store.dispatch('getProject', this.uuid);
  },

}
</script>
