<template>
<q-page padding>
  <q-btn round
         color="accent"
         icon="add"
         :to="{ 'name': 'Collection Add' }" />

  <q-table
    title="Collections"
    :data="collections"
    :columns="columns"
    row-key="id"
    :pagination.sync="pagination"
    :filter="filter"
    grid
    :loading="loading"
    no-data-label="No entries found"
    :no-results-label="filter + ' does not match any entries'"
    >

    <template v-slot:top-right>
      <q-input rounded outlined dense debounce="300" v-model="filter" placeholder="Search">
        <template v-slot:append>
          <q-icon name="search" />
        </template>
      </q-input>
    </template>

    <template v-slot:item="props">
      <div class="q-pa-xs col-xs-12 col-sm-6 col-md-4">
        <q-card>
          <q-card-section class="text-center">
            <div class="text-h6">
              {{ props.row.title }}
            </div>
            <div class="text-caption">
              {{ props.row._id }}
            </div>
          </q-card-section>
          <q-card-section class="flex flex-center">
            <q-btn
              flat
              label="More"
              :to="{ name: 'Collection About', params: { 'uuid': props.row._id } }" />
          </q-card-section>
        </q-card>
      </div>
    </template>
  </q-table>
</q-page>
</template>

<script>
export default {
  name: 'CollectionBrowser',

  computed: {
    collections: {
      get () {
        return this.$store.state.collections.collections;
      },
    }
  },

  data () {
    return {
      filter: '',

      loading: true,
      
      pagination: {
        rowsPerPage: 20
      },

      columns: [
        {
          name: 'id',
          label: 'Identifier (UUID)',
          field: '_id',
          required: true,
          align: 'left',
          sortable: true,
        },
        {
          name: 'title',
          label: 'Collection title',
          field: 'title',
          required: true,
          sortable: true
        }
      ]
    }
  },

  mounted () {
    this.$store.dispatch('collections/getCollections')
      .then(() => this.loading = false)
      .catch(() => this.loading = false)
  }
}
</script>
