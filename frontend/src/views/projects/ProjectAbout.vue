<template>
<div class="project-info">
  <div v-if="Object.keys(project).length > 0">
    <div class="project-title">{{ project.title }}</div>
    <div class="project-description field" v-html="project.description"></div>
    <table class="table is-hoverable is-striped">
      <tbody>
        <tr>
          <th scope="row">
            Contact 
          </th>
          <td>
            {{ project.contact }}
          </td>
        </tr>
        <tr v-if="project.dmp.length > 0">
          <th scope="row">
            Data management plan
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
            <ul v-for="dataset in project.datasets" :key="dataset">
              <li class="test"><a :href="'/dataset/' + dataset">{{ dataset }}</a></li>
            </ul>
          </td>
        </tr>
        <tr v-for="extraField in project.extras" :key="extraField.key">
          <th scope="row" :rowspan="user.permissions.length">
            {{ extraField.key }}
          </th>
          <td>
            {{ extraField.value }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <router-link v-if="project.owners" to="edit">
    <button class="button is-link">
      Edit
    </button>
  </router-link>
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
