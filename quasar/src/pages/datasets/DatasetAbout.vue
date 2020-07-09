<template>
<q-page padding>
  <q-inner-loading :showing="loading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>

  <q-page-sticky position="bottom-right"
                 :offset="[24, 24]"
                 v-if="dataset.creator === currentUser.name || 
                       currentUser.permissions.includes('DATA_MANAGEMENT')">
    <q-btn fab icon="edit" color="accent" :to="{ 'name': 'Dataset Edit', params: {'uuid': uuid} }" />
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

  <q-card>
    <q-card-section>
      <q-field label="Creator" stack-label>
        <template v-slot:prepend>
          <q-icon name="person" />
        </template>
        <template v-slot:control>
          {{ dataset.creator }}
        </template>
      </q-field>

      <q-field
        v-for="field in Object.keys(dataset.extra)" :key="field"
        :label="field"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="" />
        </template>
        <template v-slot:control>
          <span>
            {{ dataset.extra[field] }}
          </span>
        </template>
      </q-field>

      <q-field
        v-if="dataset.links.length > 0"
        label="Links"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="link" />
        </template>
        <template v-slot:control>
          <ul class="">
            <li v-for="(location, i) in dataset.links" :key="i">
              <q-btn
                flat
                no-caps
                dense
                :label="location.description"
                type="a"
                :href="location.url" />
            </li>
          </ul>
        </template>
      </q-field>

      <q-field
        v-if="dataset.projects.length > 0"
        label="Collections"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="local_library" />
        </template>
        <template v-slot:control>
          <ul class="">
            <li v-for="collection in dataset.projects" :key="collection._id">
              <q-btn 
                flat
                no-caps
                dense
                :label="collection.title"
                :to="{ 'name': 'Dataset About', 'params': { 'uuid': collection._id } }" />
            </li>
          </ul>
        </template>
      </q-field>

      <q-field
        v-if="dataset.related.length > 0"
        label="Related datasets"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="insights" />
        </template>

        <template v-slot:control>
          <ul class="">
            <li v-for="relDataset in dataset.related" :key="relDataset._id">
              <q-btn 
                flat
                no-caps
                dense
                :label="relDataset.title"
                :to="{ 'name': 'Dataset About', 'params': { 'uuid': relDataset._id } }" />
            </li>
          </ul>
        </template>
      </q-field>

    </q-card-section>
  </q-card>
</q-page>
</template>

<script>
export default {
  name: 'DatasetAbout',

  props: {
    uuid: {
      type: String,
      required: true
    }
  },

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

