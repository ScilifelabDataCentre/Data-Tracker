<template>
<div v-if="Object.keys(collection).length">
  <div class="text-center q-mb-lg">
    <h1 class="text-h2 q-mb-xs ">{{ collection.title }}</h1>
    <div class="text-subtitle1 text-italic">
      {{ collection.id }}
    </div>
  </div>

  <div class="q-my-md q-mx-sm"
       v-show="Object.keys(collection.properties).length">
    <q-chip square
            color="grey-3"
            v-for="field in Object.keys(collection.properties)"
            :key="field">
      <span class="text-bold text-capitalize text-blue-9 q-mr-sm">{{ field }}</span> {{ collection.properties[field] }}
    </q-chip>
  </div>

  <div class="q-my-sm q-mx-sm"
       v-show="collection.tags.length">
    <q-chip square
            color="grey-3"
            v-for="entry in collection.tags"
            :key="entry">
      <q-avatar color="secondary" text-color="white" icon="fas fa-tag" />
      {{ entry }}
    </q-chip>
  </div>

  <div class="q-my-md" v-show="collection.description.length">
    <q-markdown :src="collection.description" />
  </div>

  <div class="q-my-md"
       v-show="collection.datasets.length > 0">
    <q-list>
      <list-header title="Datasets"
                   explanation="Datasets associated with this collection" />
      <q-item clickable
              v-for="dataset in collection.datasets"
              :key="dataset.id"
              @click="$router.push({ 'name': 'Dataset About', 'params': { 'uuid': dataset.id } })">
        <q-item-section avatar>
          <q-icon name="fas fa-chart-area" />
        </q-item-section>
        <q-item-section>
          <q-item-label>
            {{ dataset.title }}
          </q-item-label>
          <q-item-label caption>
            {{ dataset.id }}
          </q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </div>

  <div class="q-my-md" v-show="'editors' in collection && collection.editors.length">
    <q-list>
      <div>
        <list-header title="Editors"
                     explanation="Users that may edit this collection" />
        <user-entry v-for="entry in collection.editors"
                    :key="entry.id"
                    v-bind="entry" />
      </div>
    </q-list>
  </div>
</div>
</template>

<script>
import UserEntry from 'components/UserEntry.vue'
import ListHeader from 'components/ListHeader.vue'

export default {
  name: 'EntryAbout',

  components: {
    'user-entry': UserEntry,
    'list-header': ListHeader
  },

  props: {
    isLoading: {
      type: Boolean,
      default: true,
    },
    entryType: {
      type: String,
      
    }
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
