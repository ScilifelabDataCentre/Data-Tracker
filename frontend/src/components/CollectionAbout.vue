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
          v-show="Object.keys(collection.properties).length ||
                  collection.tags.length">
    <q-card-section class="flex q-ma-sm">
      <q-chip square
              color="grey-3"
              v-for="field in Object.keys(collection.properties)"
              :key="field">
        <span class="text-bold text-capitalize text-blue-9 q-mr-sm">{{ field }}</span> {{ collection.properties[field] }}
      </q-chip>
      <q-chip square
              color="grey-3"
              v-for="entry in collection.tags"
              :key="entry">
        <q-avatar color="secondary" text-color="white" icon="fas fa-tag" />
        {{ entry }}
      </q-chip>
    </q-card-section>
  </q-card>

  <q-card class="q-my-md"
          v-show="collection.datasets.length">
    <q-card-section>
      <q-list dense>
        <list-header title="Datasets"
                     explanation="Datasets associated with this collection" />
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

  <q-card class="q-my-md" v-show="'editors' in collection && collection.editors.length">
    <q-card-section>
      <q-list dense>
        <div>
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
  name: 'CollectionAbout',

  components: {
    'user-entry': UserEntry,
    'list-header': ListHeader
  },

  props: {
    isLoading: {
      type: Boolean,
      default: true,
    },
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
