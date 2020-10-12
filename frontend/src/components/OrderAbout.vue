<template>
<div v-if="Object.keys(order).length > 0">
  <div class="text-center q-mb-lg">
    <h1 class="text-h2 q-mb-xs ">{{ order.title }}</h1>
    <div class="text-subtitle1 text-italic">
      {{ order._id }}
    </div>
  </div>

  <q-card class="q-my-md">
    <q-card-section>
      <q-markdown :src="order.description" />
    </q-card-section>
  </q-card>

  <q-card class="q-my-md">
    <q-card-section>
      <div v-show="order.datasets.length > 0">
        <q-list dense>
          <list-header title="Datasets"
                       explanation="Datasets generated from this order" />
          <q-item v-for="dataset in order.datasets" :key="dataset._id">
            <q-item-section avatar>
              <q-btn flat
                     dense
                     round
                     icon="link"
                     :to="{ 'name': 'Dataset About', 'params': { 'uuid': dataset._id } }" />
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
      
      <q-field
        v-for="field in Object.keys(order.tagsUser)" :key="field"
        :label="field"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="label" />
        </template>
        <template v-slot:control>
          <span>
            {{ order.userTags[field] }}
          </span>
        </template>
      </q-field>
    </q-card-section>
  </q-card>

  <q-card class="q-my-md">
    <q-card-section>
      <q-list dense>
        <div v-show="order.authors.length > 0">
          <list-header title="Authors"
                       explanation="The ones who provided the sample, e.g. a researcher" />
          <user-entry v-for="author in order.authors"
                      :key="author._id"
                      v-bind="author" />
        </div>

        <div v-show="order.generators.length > 0">
          <list-header title="Generators"
                       explanation="The ones who generated the data, e.g. a facility" />
          <user-entry v-for="generator in order.generators"
                      :key="generator._id"
                      v-bind="generator" />
        </div>

        <div v-show="order.organisation !== {}">
          <list-header title="Organisation"
                       explanation="The data owner, e.g. a university" />
          <user-entry v-bind="order.organisation" />
        </div>

        <div v-show="order.editors.length > 0">
          <list-header title="Editors"
                       explanation="Users that may edit this order" />
          <user-entry v-for="entry in order.editors"
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
