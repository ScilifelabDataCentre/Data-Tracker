<template>
<q-page padding>
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
      <q-field v-if="dataset.hasOwnProperty('editors')" label="Editors" stack-label>
        <template v-slot:prepend>
          <q-icon name="person" />
        </template>
        <template v-slot:control>
          <user-info :entries="dataset.editors" />
        </template>
      </q-field>
      <q-field v-if="dataset.authors.length > 0" label="Authors" stack-label>
        <template v-slot:prepend>
          <q-icon name="person" />
        </template>
        <template v-slot:control>
          <user-info :entries="dataset.authors" />
        </template>
      </q-field>
      <q-field v-if="dataset.generators.length > 0" label="Generators" stack-label>
        <template v-slot:prepend>
          <q-icon name="person" />
        </template>
        <template v-slot:control>
          <user-info :entries="dataset.generators" />
        </template>
      </q-field>
      <q-field v-if="dataset.organisation.name.length > 0" label="Organisation" stack-label>
        <template v-slot:prepend>
          <q-icon name="person" />
        </template>
        <template v-slot:control>
          <user-info :entries="[dataset.organisation]" />
        </template>
      </q-field>
    </q-card-section>
    <q-card-section>
      <q-field
        v-for="entry in dataset.tagsStandard" :key="entry.key"
        :label="entry.key"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="label" />
        </template>
        <template v-slot:control>
          <span>
            {{ entry.value }}
          </span>
        </template>
      </q-field>

      <q-field
        v-for="entry in dataset.tagsUser" :key="entry.key"
        :label="entry.key"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="label" />
        </template>
        <template v-slot:control>
          <span>
            {{ entry.value }}
          </span>
        </template>
      </q-field>

      <q-field
        v-if="dataset.collections.length > 0"
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

  <q-page-sticky position="bottom-right"
                 :offset="[24, 24]"
                 v-if="dataset.creator === currentUser.name ||
                       currentUser.permissions.includes('DATA_MANAGEMENT')">
    <q-btn fab icon="edit" color="accent" :to="{ 'name': 'Dataset Edit', params: {'uuid': uuid} }" />
  </q-page-sticky>

  <q-inner-loading :showing="loading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
</q-page>
</template>

<script>
import UserInfo from 'components/UserInfo.vue'

export default {
  name: 'DatasetAbout',

 components: {'user-info': UserInfo},
  
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

