<template>
<q-page padding>
  <h2 class="text-capitalize">Users</h2>
  <q-table
    flat
    :rows="userList"
    :columns="columns"
    row-key="id"
    :pagination="pagination"
    :filter="filter"
    :loading="loading"
    no-data-label="No entries found"
    :no-results-label="filter + ' does not match any entries'">
    <template v-slot:top-left>
      <q-btn color="primary"
             id="user-manager-add"
             icon="add"
             label="Add user"
             @click="activateUserEdit('')" />
    </template>
    <template v-slot:top-right>
      <q-input rounded
               outlined
               dense
               type="search"
               debounce="300"
               v-model="filter"
               placeholder="Search">
        <template v-slot:append>
          <q-icon name="search" />
        </template>
      </q-input>
    </template>
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td v-for="col in props.cols"
              :key="col.name"
              :props="props">
          {{ col.value }}
        </q-td>
        <q-td auto-width
              v-if="currentUser.permissions.includes('USER_MANAGEMENT')">
          <q-btn flat
                 dense
                 round
                 icon="edit"
                 @click="activateUserEdit(props.row.id)"
                 size="sm" />
        </q-td>
      </q-tr>
    </template>
  </q-table>

  <user-edit v-model="showUserEdit"
             :uuid="userId"
             @user-changed="loadData"/>

</q-page>
</template>

<script>
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
      showEntryLog: false,
      userId: 'default',
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
        {
          name: 'contact',
          label: 'Contact',
          field: 'contact',
          sortable: true
        },
        {
          name: 'url',
          label: 'URL',
          field: 'url',
          sortable: true
        },

      ]
    }
  },

  computed: {
    currentUser: {
      get () {
        return this.$store.state.currentUser.info;
      },
    },
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

    loadData () {
    this.$store.dispatch('entries/resetEntryList')
        .then(() => this.loading = true)
        .then(() => {
          this.$store.dispatch('entries/getEntries', 'user')
            .then(() => this.loading = false)
            .catch(() => this.loading = false)
        });
    },
  },

  mounted () {
    this.loadData();
  },
}
</script>
