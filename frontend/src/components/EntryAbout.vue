<template>
<div v-if="Object.keys(entry).length">
  <div class="text-center q-mb-lg">
    <h1 class="text-h2 q-mb-xs"
        id="entry-about-title-text">
      {{ entry.title }}
    </h1>
    <div class="text-subtitle1 text-italic"
         id="entry-about-title-identifier">
      {{ entry.id }}
    </div>
  </div>
  
  <div class="q-my-md q-mx-sm"
       id="entry-about-properties"
       v-show="Object.keys(entry.properties).length">
    <q-chip square
            color="grey-3"
            v-for="field in Object.keys(entry.properties)"
            :key="field">
      <span class="text-bold text-capitalize text-blue-9 q-mr-sm">{{ field }}</span> {{ entry.properties[field] }}
    </q-chip>
  </div>
  
  <div class="q-my-sm q-mx-sm"
       id="entry-about-tags"
       v-show="entry.tags.length">
    <q-chip square
            color="grey-3"
            v-for="tag in entry.tags"
            :key="tag">
      <q-avatar color="secondary" text-color="white" icon="fas fa-tag" />
      {{ tag }}
    </q-chip>
  </div>
  
  <div class="q-my-md"
       v-show="entry.description.length"
       id="entry-about-description">
    <q-markdown :src="entry.description" />
  </div>
  
  <div class="q-my-md"
       id="entry-about-cross-refs"
       v-if="('related' in entry && entry.related.length) ||
             ('datasets' in entry && entry.datasets.length) ||
             ('order' in entry && Object.keys(entry.order).length)">
    <q-list bordered>
      <div id="entry-about-datasets"
           v-if="'datasets' in entry && entry.datasets.length">
        <list-header title="Datasets"
                     :explanation="'Datasets associated with this ' + dataType" />
        <q-item clickable
                v-for="dataset, i in entry.datasets"
                :key="dataset.id"
                :id="'entry-about-datasets-' + i"
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
      </div>
      <div id="entry-about-order"
           v-if="dataType == 'dataset' && 'order' in entry">
        <list-header title="Order"
                     explanation="The order the dataset originates from" />
        <q-item clickable
                id="entry-about-order"
                @click="$router.push({ 'name': 'Order About', 'params': { 'uuid': entry.order.id } })">
          <q-item-section avatar>
            <q-icon name="fas fa-chart-area" />
          </q-item-section>
          <q-item-section>
            <q-item-label>
              {{ entry.order.title }}
            </q-item-label>
            <q-item-label caption>
              {{ entry.order.id }}
            </q-item-label>
          </q-item-section>
        </q-item>
      </div>
      <div id="entry-about-related"
           v-if="dataType == 'dataset' && entry.related.length > 0">
        <list-header title="Related Datasets"
                     explanation="Other datasets originating from the same order" />
        <q-item clickable
                v-for="dataset, i in entry.related"
                :key="dataset.id"
                :id="'entry-about-related-' + i"
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
      </div>
      <div id="entry-about-collections"
           v-if="dataType == 'dataset' && entry.collections.length > 0">
        <list-header title="Collections"
                     explanation="Collections containg the dataset" />
        <q-item clickable
                v-for="collection, i in entry.collections"
                :key="collection.id"
                :id="'entry-about-collections-' + i"
                @click="$router.push({ 'name': 'Collection About', 'params': { 'uuid': collection.id } })">
          <q-item-section avatar>
            <q-icon name="fas fa-chart-area" />
          </q-item-section>
          <q-item-section>
            <q-item-label>
              {{ collection.title }}
            </q-item-label>
            <q-item-label caption>
              {{ collection.id }}
            </q-item-label>
          </q-item-section>
        </q-item>
      </div>
    </q-list>
  </div>

  <div class="q-my-md">
    <q-list bordered>
      <div v-if="dataType === 'order' || dataType == 'dataset'">
        <div v-if="entry.authors.length"
             id="entry-about-authors">
          <list-header title="Authors"
                       explanation="The ones who provided the sample, e.g. a researcher" />
          <user-entry v-for="author, i in entry.authors"
                      :key="author._id"
                      :id="'entry-about-authors-' + i"
                      v-bind="author" />
        </div>
        <div v-if="entry.generators.length"
             id="entry-about-generators">
          <list-header title="Generators"
                       explanation="The ones who generated the data, e.g. a facility" />
          <user-entry v-for="generator, i in entry.generators"
                      :key="generator._id"
                      :id="'entry-about-generators-' + i"
                      v-bind="generator" />
        </div>
        <div v-if="Object.keys(entry.organisation).length"
             id="entry-about-organisation">
          <list-header title="Organisation"
                       explanation="The data owner, e.g. a university" />
          <user-entry v-bind="entry.organisation"
                      id="entry-about-organisation-entry" />
        </div>
      </div>
      <div v-if="'editors' in entry && entry.editors.length"
           id="entry-about-editors">
        <list-header title="Editors"
                     explanation="Users that may edit this entry" />
        <user-entry v-for="editor, i in entry.editors"
                    :key="editor.id"
                    :id="'entry-about-editors-' + i"
                    v-bind="editor" />
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
