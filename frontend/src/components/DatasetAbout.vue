<template>
<div v-if="Object.keys(dataset).length">
  <div class="text-center q-mb-lg">
    <h1 class="text-h2 q-mb-xs ">{{ dataset.title }}</h1>
    <div class="text-subtitle1 text-italic">
      {{ dataset._id }}
    </div>
  </div>

  <q-card class="q-my-md" v-show="dataset.description.length">
    <q-card-section>
      <q-markdown :src="dataset.description" />
    </q-card-section>
  </q-card>

  <q-card class="q-my-md"
          v-show="Object.keys(dataset.properties).length ||
                  dataset.tags.length">
    <q-card-section class="flex q-ma-sm">
      <q-chip square
              color="grey-3"
              v-for="field in Object.keys(dataset.properties)"
              :key="field">
        <span class="text-bold text-capitalize text-blue-9 q-mr-sm">{{ field }}</span> {{ dataset.properties[field] }}
      </q-chip>
      <q-chip square
              color="grey-3"
              v-for="entry in dataset.tags"
              :key="entry">
        <q-avatar color="secondary" text-color="white" icon="fas fa-tag"></q-avatar>
        {{ entry }}
      </q-chip>
    </q-card-section>
  </q-card>

  <q-card class="q-my-md"
          v-show="related.length">
    <q-card-section>
      <q-list dense>
        <list-header title="Related Datasets"
                     explanation="Other datasets generated from the same order" />
        <q-item v-for="dataset in related" :key="dataset._id">
          <q-item-section avatar>
            <q-btn flat
                   dense
                   round
                   icon="link"
                   :to="{ 'name': 'Dataset About', 
                          'params': { 'uuid': dataset._id } }" />
          </q-item-section>
          <q-item-section>
            <q-item-label>
              {{ dataset.title }}
            </q-item-label>
            <q-item-label caption>
              {{ dataset._id }}
            </q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-card-section>
  </q-card>

  <q-card class="q-my-md">
    <q-card-section>
      <q-list dense>
        <div v-show="dataset.authors.length">
          <list-header title="Authors"
                       explanation="The ones who provided the sample, e.g. a researcher" />
          <user-entry v-for="author in dataset.authors"
                      :key="author._id"
                      v-bind="author" />
        </div>

        <div v-show="dataset.generators.length">
          <list-header title="Generators"
                       explanation="The ones who generated the data, e.g. a facility" />
          <user-entry v-for="generator in dataset.generators"
                      :key="generator._id"
                      v-bind="generator" />
        </div>

        <div v-if="Object.keys(dataset.organisation).length">
          <list-header title="Organisation"
                       explanation="The data owner, e.g. a university" />
          <user-entry v-bind="dataset.organisation" />
        </div>

        <div v-show="'editors' in dataset && dataset.editors.length">
          <list-header title="Editors"
                       explanation="Users that may edit this dataset" />
          <user-entry v-for="entry in dataset.editors"
                      :key="entry._id"
                      v-bind="entry" />
        </div>
      </q-list>
    </q-card-section>
  </q-card>
</div>
</template>

<script>
import UserEntry from 'components/UserEntry.vue'
import ListHeader from 'components/ListHeader.vue'

export default {
  name: 'DatasetAbout',

  components: {
    'user-entry': UserEntry,
    'list-header': ListHeader
  },

  computed: {
    dataset: {
      get () {
        return this.$store.state.entries.entry;
      },
    },

    related: {
      get () {
        if ('related' in this.dataset)
          return this.dataset.related.filter((entry) => entry._id !== this.dataset._id);
        return []
      },
    }
  },

  data () {
    return {
    }
  },

}
</script>
