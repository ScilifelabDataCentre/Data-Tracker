xc<template>
<q-page padding>
  <h2 class="text-capitalize">Users</h2>
  <q-card>
    <q-card-section>
      <q-table
        :data="userList"
        :columns="columns"
        row-key="id"
        :pagination.sync="pagination"
        :filter="filter"
        :loading="loading"
        no-data-label="No entries found"
        :no-results-label="filter + ' does not match any entries'">
        <template v-slot:top-left>
          <q-btn round
                 color="primary"
                 icon="add"
                 @click="activateUserEdit('')" />
        </template>
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
                     @click="activateUserEdit(props.row._id)"
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
    </q-card-section>
  </q-card>
  <user-edit v-model="showUserEdit" :uuid="userId" />
</q-page>
</template>

<script>
import LogViewer from 'components/LogViewer.vue'
import UserEdit from 'components/UserEdit.vue'

export default {
  name: 'UserManager',

  components: {
    'user-edit': UserEdit,
  },
  
  data () {
    return {
      filter: '',
      loading: true,
      showUserEdit: false,
      userId: '',
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
        return this.$store.state.entries.entryList;
      },
    },
  },

  methods: {
    activateUserEdit (uuid) {
      this.userId = uuid;
      this.showUserEdit = true;
    },
  },

  mounted () {
    this.$store.dispatch('entries/resetEntryList')
      .then(() => this.loading = true)
      .then(() => {
        this.$store.dispatch('entries/getEntries', 'user')
          .then(() => this.loading = false)
          .catch(() => this.loading = false)
      });
  },
}
</script>
