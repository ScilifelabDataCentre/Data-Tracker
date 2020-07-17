xc<template>
<q-page padding>
  <q-table
    title="Users"
    :data="userList"
    :columns="columns"
    row-key="id"
    :pagination.sync="pagination"
    :filter="filter"
    :loading="loading"
    no-data-label="No entries found"
    :no-results-label="filter + ' does not match any entries'">
    <template v-slot:top-right>
      <q-input rounded outlined dense debounce="300" v-model="filter" placeholder="Search">
        <template v-slot:append>
          <q-icon name="search" />
        </template>
      </q-input>
    </template>
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td
          v-for="col in props.cols"
          :key="col.name"
          :props="props"
          >
          {{ col.value }}
        </q-td>
        <q-td auto-width>
          <q-btn flat
                 dense
                 round
                 icon="edit"
                 :to="{ 'name': 'Admin User Edit',
                        'params': { 'uuid' : props.row._id } }"
                 size="sm" />
          <q-btn flat
                 dense
                 round
                 icon="pending_actions"
                 size="sm" />
          <q-btn flat
                 dense
                 round
                 icon="assessment"
                 size="sm" />
        </q-td>
      </q-tr>
    </template>
  </q-table>
  </q-page>
</template>

<script>
export default {
  name: 'UserManager',

  data () {
    return {
      filter: '',

      loading: true,
      
      pagination: {
        rowsPerPage: 20
      },

      columns: [
        {
          name: 'name',
          label: 'Name',
          field: 'name',
          align: 'left',
          sortable: true,
        },
        {
          name: 'authId',
          label: 'Authentication IDs',
          field: 'authIds',
          sortable: true
        },
        {
          name: 'email',
          label: 'Email',
          field: 'email',
          sortable: true
        },
        {
          name: 'affiliation',
          label: 'Affiliation',
          field: 'affiliation',
          sortable: true
        },
      ]
    }
  },

  computed: {
    userList: {
      get () {
        return this.$store.state.adminUser.userList;
      },
    },
  },

  created () {
    this.$store.dispatch('adminUser/getUsers')
      .then(() => this.loading = false)
      .catch(() => this.loading = false);
    
  },
}
</script>
