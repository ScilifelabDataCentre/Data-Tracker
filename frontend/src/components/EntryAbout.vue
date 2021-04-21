<template>
<div v-if="Object.keys(entry).length">
  <div class="text-center q-mb-lg">
    <h1 class="text-h2 q-mb-xs ">{{ entry.title }}</h1>
    <div class="text-subtitle1 text-italic">
      {{ entry.id }}
    </div>
  </div>

  <div class="q-my-md q-mx-sm"
       v-show="Object.keys(entry.properties).length">
    <q-chip square
            color="grey-3"
            v-for="field in Object.keys(entry.properties)"
            :key="field">
      <span class="text-bold text-capitalize text-blue-9 q-mr-sm">{{ field }}</span> {{ entry.properties[field] }}
    </q-chip>
  </div>

  <div class="q-my-sm q-mx-sm"
       v-show="entry.tags.length">
    <q-chip square
            color="grey-3"
            v-for="entry in entry.tags"
            :key="entry">
      <q-avatar color="secondary" text-color="white" icon="fas fa-tag" />
      {{ entry }}
    </q-chip>
  </div>

  <div class="q-my-md" v-show="entry.description.length">
    <q-markdown :src="entry.description" />
  </div>

  <div class="q-my-md"
       v-show="entry.datasets.length > 0">
    <q-list>
      <list-header title="Datasets"
                   :explanation="'Datasets associated with this ' + dataType" />
      <q-item clickable
              v-for="dataset in entry.datasets"
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

  <div class="q-my-md" v-show="'editors' in entry && entry.editors.length">
    <q-list>
      <div>
        <list-header title="Editors"
                     :explanation="'Users that may edit this ' + dataType" />
        <user-entry v-for="entry in entry.editors"
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
    dataType: {
      type: String,
      required: true,  
    }
  },

  computed: {
    entry: {
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
