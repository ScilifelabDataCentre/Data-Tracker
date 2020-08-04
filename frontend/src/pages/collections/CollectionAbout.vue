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
      <q-field label="Contact" stack-label>
        <template v-slot:prepend>
          <q-icon name="contacts" />
        </template>
        <template v-slot:control>
          {{ collection.contact }}
        </template>
      </q-field>

      <q-field
        v-for="field in Object.keys(collection.extra)" :key="field"
        :label="field"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="label" />
        </template>
        <template v-slot:control>
          <span>
            {{ collection.extra[field] }}
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
      <q-field
        v-if="collection.publications.length > 0"
        label="Publications"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="article" />
        </template>

        <template v-slot:control>
          <ul class="">
            <li v-for="(publication, i) in collection.publications" :key="i">
              {{ publication }}
            </li>
          </ul>
        </template>
      </q-field>
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
