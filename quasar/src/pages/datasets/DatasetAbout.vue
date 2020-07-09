<template>
<q-page padding>
  <q-inner-loading :showing="loading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
  <q-page-sticky position="bottom-right"
                 :offset="[24, 24]"
                 v-if="dataset.creator === currentUser.name || 
                       currentUser.permissions.includes('DATA_MANAGEMENT')">
    <q-btn fab icon="edit" color="accent" />
  </q-page-sticky>
      <div class="text-center q-mb-lg">
        <h1 class="text-h2 q-mb-xs ">{{ dataset.title }}</h1>
        <div class="text-subtitle1 text-italic">
          {{ dataset._id }}
        </div>
      </div>
  <q-card class="q-my-lg">
    <q-card-section>
      <q-markdown :src="dataset.description" />
    </q-card-section>
  </q-card>
  <q-card class="q-my-lg">
    <q-card-section>
      <table>
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
              <q-list>
                <q-item v-for="location in dataset.links" :key="location.description">
                  <q-btn flat no-caps :label="location.description" type="a" :href="location.url" />
                </q-item>
              </q-list>
            </td>
          </tr>
          <tr v-for="field in Object.keys(dataset.extra)" :key="field">
            <th class="capitalize" scope="row">{{ field }}</th>
            <td>{{ dataset.extra[field] }}</td>
          </tr>
          <tr v-if="dataset.projects.length > 0">
            <th scope="row">
              Projects
            </th>
            <td>
              <q-list>
                <q-item v-for="project in dataset.projects" :key="project._id">
                  <q-btn flat no-caps :label="project.title" :to="'/project/' + project._id" />
                </q-item>
              </q-list>
            </td>
          </tr>
          <tr v-if="dataset.related.length > 0">
            <th scope="row">
              Related datasets
            </th>
            <td>
              <q-list>
                <q-item v-for="dataset in dataset.related" :key="dataset._id">
                  <q-btn flat no-caps :label="dataset.title" :to="'/dataset/' + dataset._id"></q-btn>
                </q-item>
              </q-list>
            </td>
          </tr>
        </tbody>
      </table>
    </q-card-section>
  </q-card>
</q-page>
</template>

<script>
export default {
  name: 'DatasetAbout',
  props: ['uuid'],

  computed: {
    dataset: {
      get () {
        return this.$store.state.datasets.dataset;
      },
    },
    currentUser: {
      get () {
        return this.$store.state.currentUser.info;
      },
    },
  },

  data () {
    return {
      loading: true,
    }
  },
  
  mounted () {
    this.$store.dispatch('datasets/getDataset', this.uuid)
      .then(() => this.loading = false)
      .catch(() => this.loading = false)
  }
  
}
</script>
