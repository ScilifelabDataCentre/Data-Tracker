<template>
<div v-if="Object.keys(dataset).length">
  <div class="text-center q-mb-lg">
    <h1 class="text-h2 q-mb-xs ">{{ dataset.title }}</h1>
    <div class="text-subtitle1 text-italic">
      {{ dataset._id }}
    </div>
  </div>

  <div class="q-my-md q-mx-sm"
       v-show="Object.keys(dataset.properties).length">
      <q-chip square
              color="grey-3"
              v-for="field in Object.keys(dataset.properties)"
              :key="field">
        <span class="text-bold text-capitalize text-blue-9 q-mr-sm">{{ field }}</span> {{ dataset.properties[field] }}
      </q-chip>
  </div>

  <div class="q-my-sm q-mx-sm"
       v-show="dataset.tags.length">
    <q-chip square
            color="grey-3"
            v-for="entry in dataset.tags"
            :key="entry">
      <q-avatar color="secondary" text-color="white" icon="fas fa-tag" />
      {{ entry }}
    </q-chip>
  </div>

  <div class="q-my-md" v-show="dataset.description.length">
    <q-markdown :src="dataset.description" />
  </div>

  <div class="q-my-md"
       v-show="dataset.related.length">
    <q-list>
      <list-header title="Datasets"
                   explanation="Datasets generated from this order" />
      <q-item clickable
              v-for="related in dataset.related"
              :key="related._id"
              @click="$router.push({ 'name': 'Dataset About', 'params': { 'uuid': related._id } })">
        <q-item-section avatar>
          <q-icon name="fas fa-chart-area" />
        </q-item-section>
        <q-item-section>
          <q-item-label>
            {{ related.title }}
          </q-item-label>
          <q-item-label caption>
            {{ related._id }}
          </q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </div>

  <div class="q-my-md">
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
      <div v-show="dataset.editors.length">
        <list-header title="Editors"
                     explanation="Users that may edit this dataset" />
        <user-entry v-for="entry in dataset.editors"
                    :key="entry._id"
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
  },

  data () {
    return {
    }
  },

}
</script>
