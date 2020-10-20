<template>
<div v-if="Object.keys(collection).length">
  <div class="text-center q-mb-lg">
    <h1 class="text-h2 q-mb-xs ">{{ collection.title }}</h1>
    <div class="text-subtitle1 text-italic">
      {{ collection._id }}
    </div>
  </div>

  <q-card class="q-my-md" v-show="collection.description.length">
    <q-card-section>
      <q-markdown :src="collection.description" />
    </q-card-section>
  </q-card>

  <q-card class="q-my-md"
          v-show="Object.keys(collection.tagsStandard).length ||
                  Object.keys(collection.tagsUser).length">
    <q-card-section class="flex q-ma-sm">
      <q-chip square
              color="grey-3"
              v-for="field in Object.keys(collection.tagsStandard)"
              :key="field">
        <span class="text-bold text-capitalize text-blue-9 q-mr-sm">{{ field }}</span> {{ collection.tagsStandard[field] }}
      </q-chip>
      <q-chip square
              color="grey-3"
              v-for="field in Object.keys(collection.tagsUser)"
              :key="field">
        <span class="text-bold text-capitalize text-secondary q-mr-sm">{{ field }}</span> {{ collection.tagsUser[field] }}
      </q-chip>
    </q-card-section>
  </q-card>

  <q-card class="q-my-md"
          v-show="collection.datasets.length > 0">
    <q-card-section>
      <q-list dense>
        <list-header title="Datasets"
                     explanation="Datasets generated from this collection" />
        <q-item v-for="dataset in collection.datasets" :key="dataset._id">
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
        <div v-show="collection.authors.length">
          <list-header title="Authors"
                       explanation="The ones who provided the sample, e.g. a researcher" />
          <user-entry v-for="author in collection.authors"
                      :key="author._id"
                      v-bind="author" />
        </div>

        <div v-show="collection.generators.length">
          <list-header title="Generators"
                       explanation="The ones who generated the data, e.g. a facility" />
          <user-entry v-for="generator in collection.generators"
                      :key="generator._id"
                      v-bind="generator" />
        </div>

        <div v-if="Object.keys(collection.organisation).length">
          <list-header title="Organisation"
                       explanation="The data owner, e.g. a university" />
          <user-entry v-bind="collection.organisation" />
        </div>

        <div v-show="collection.editors.length">
          <list-header title="Editors"
                       explanation="Users that may edit this collection" />
          <user-entry v-for="entry in collection.editors"
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
  name: 'OrderAbout',

  components: {
    'user-entry': UserEntry,
    'list-header': ListHeader
  },

  computed: {
    collection: {
      get () {
        return this.$store.state.entries.entry;
      },
    },
  },

  data () {
    return {
    }
  },

}
</script>
