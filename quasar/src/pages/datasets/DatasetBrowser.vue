<template>
<q-page padding>
  <q-table
    title="Datasets"
    :data="datasets"
    :columns="columns"
    row-key="id"
    :pagination.sync="pagination"
    /></q-page>
</template>

<script>
export default {
  name: 'DatasetBrowser',
  
  computed: {
    datasets: {
      get () {
        return this.$store.state.datasets.datasets;
      },
    }
  },

  data () {
    return {
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

          // style: 'width: 500px',
          // classes: 'my-special-class',
          // headerStyle: 'width: 500px',
          // headerClasses: 'my-special-class'
        },
        { name: 'title',
          label: 'Dataset title',
          field: 'title',
          required: true,
          sortable: true
        }
      ]
    }
  },

  mounted () {
    this.$store.dispatch('datasets/getDatasets');
  }
}
</script>
