<template>
<div v-if="Object.keys(order).length">
  <div class="text-center q-mb-lg">
    <h1 class="text-h2 q-mb-xs ">{{ order.title }}</h1>
    <div class="text-subtitle1 text-italic">
      {{ order._id }}
    </div>
  </div>

  <div class="q-my-sm q-mx-sm"
       v-show="order.tags.length">
    <q-chip square
            color="grey-3"
            v-for="entry in order.tags"
            :key="entry">
      <q-avatar color="secondary" text-color="white" icon="fas fa-tag" />
      {{ entry }}
    </q-chip>
  </div>
  
  <div class="q-my-md q-mx-sm"
       v-show="Object.keys(order.properties).length">
      <q-chip square
              color="grey-3"
              v-for="field in Object.keys(order.properties)"
              :key="field">
        <span class="text-bold text-capitalize text-blue-9 q-mr-sm">{{ field }}</span> {{ order.properties[field] }}
      </q-chip>
  </div>

  <div class="q-my-md" v-show="order.description.length">
    <q-markdown :src="order.description" />
  </div>

  <div class="q-my-md"
       v-show="order.datasets.length > 0">
    <q-list>
      <list-header title="Datasets"
                   explanation="Datasets generated from this order" />
      <q-item clickable
              v-for="dataset in order.datasets"
              :key="dataset._id"
              @click="$router.push({ 'name': 'Dataset About', 'params': { 'uuid': dataset._id } })">
        <q-item-section avatar>
          <q-icon name="fas fa-chart-area" />
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
  </div>

  <div class="q-my-md">
      <q-list dense>
        <div v-show="order.authors.length">
          <list-header title="Authors"
                       explanation="The ones who provided the sample, e.g. a researcher" />
          <user-entry v-for="author in order.authors"
                      :key="author._id"
                      v-bind="author" />
        </div>

        <div v-show="order.generators.length">
          <list-header title="Generators"
                       explanation="The ones who generated the data, e.g. a facility" />
          <user-entry v-for="generator in order.generators"
                      :key="generator._id"
                      v-bind="generator" />
        </div>

        <div v-if="Object.keys(order.organisation).length">
          <list-header title="Organisation"
                       explanation="The data owner, e.g. a university" />
          <user-entry v-bind="order.organisation" />
        </div>

        <div v-show="order.editors.length">
          <list-header title="Editors"
                       explanation="Users that may edit this order" />
          <user-entry v-for="entry in order.editors"
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
  name: 'OrderAbout',

  components: {
    'user-entry': UserEntry,
    'list-header': ListHeader
  },

  computed: {
    order: {
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
