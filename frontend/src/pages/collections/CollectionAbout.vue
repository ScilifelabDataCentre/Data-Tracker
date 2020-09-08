<template>
<q-page padding>
  <div class="text-center q-mb-lg">
    <h1 class="text-h2 q-mb-xs ">{{ collection.title }}</h1>
    <div class="text-subtitle1 text-italic">
      {{ collection._id }}
    </div>
  </div>

  <q-card class="q-my-lg">
    <q-card-section>
      <q-markdown :src="collection.description" />
    </q-card-section>
  </q-card>

  <q-card>
    <q-card-section>

      <q-field
        v-for="entry in collection.tagsStandard" :key="entry.key"
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
        v-for="entry in collection.tagsUser" :key="entry.key"
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
    </q-card-section>

    <q-card-section>
      <q-field
        v-if="collection.datasets.length > 0"
        label="Datasets"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="insights" />
        </template>

        <template v-slot:control>
          <ul class="">
            <li v-for="ds in collection.datasets" :key="ds._id">
              <q-btn 
                flat
                no-caps
                dense
                :label="ds.title"
                :to="{ 'name': 'Dataset About', 'params': { 'uuid': ds._id } }" />
            </li>
          </ul>
        </template>
      </q-field>
    </q-card-section>

    <q-card-section>
    </q-card-section>
  </q-card>

  <q-page-sticky position="bottom-right"
                 :offset="[24, 24]">
    <q-btn fab
           icon="edit"
           color="accent"
           :to="{ 'name': 'Collection Edit', params: {'uuid': uuid} }" />
  </q-page-sticky>

  <q-inner-loading :showing="loading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
</q-page>
</template>

<script>
export default {
  name: 'CollectionAbout',

  props: {
    uuid: {
      type: String,
      required: true
    }
  },

  computed: {
    collection: {
      get () {
        return this.$store.state.collections.collection;
      },
    },
  },

  data () {
    return {
      loading: true,
    }
  },
  
  mounted () {
    this.$store.dispatch('collections/getCollection', this.uuid)
      .then(() => this.loading = false)
      .catch(() => {
        this.loading = false
      });
  }

}
</script>
