<template>
<div>
  <q-table
    flat
  :data="onlySelected ? selected : users"
  :columns="columns"
  row-key="id"
  :loading="isLoadingUsers"
  :filter="filter"
  :selection="selectType"
  :selected.sync="selected"
  :pagination.sync="pagination"
  no-data-label="No entries found"
  :no-results-label="filter + ' does not match any entries'">
  <template v-slot:top-left>
    <div class="row">
      <q-input rounded
               outlined
               dense
               debounce="300"
               v-model="filter"
               type="search"
               placeholder="Search">
        <template v-slot:append>
          <q-icon name="search" />
        </template>
      </q-input>
      <q-toggle left-label
                class="q-mx-sm"
                v-model="onlySelected"
                label="Show selected only"
                color="primary"/>
      <q-btn flat
             no-caps
             icon="fas fa-user-plus"
             color="primary"
             @click="showAddUser = true"
             label="Add User" />
    </div>
  </template>
  <template v-slot:top-right>
    <q-btn round
           flat
           dense
           color="primary"
           icon="cached"
           @click="loadData" />
  </template>
</q-table>
  <user-edit v-model="showAddUser"
             uuid=""
             @user-changed="loadData"/>
</div>
</template>

<script>
import UserEdit from 'components/UserEdit.vue'

export default {
  name: 'UserSelector',

  components: {
    'user-edit': UserEdit,
  },

  computed: {
    selected: {
      get () {
        if (this.isLoading)
          return [];
        let data = this.$store.state.entries.entry[this.fieldDataName];
        if (!Array.isArray(data))
            data = [data];
        return JSON.parse(JSON.stringify(data));
      },
      set (newValue) {
        let data = {};
        data[this.fieldDataName] = newValue;
        this.$store.dispatch('entries/setEntryFields', data);
      }
    },
    
    users: {
      get () {
        return this.$store.state.entries.entryList;
      },
    },

    currentUser: {
      get () {
        return this.$store.state.currentUser.info;
      },
    },
  },
  
  props: {
    fieldTitle: {
      type: String,
      required: true,
    },
    fieldDataName: {
      type: String,
      required: true,
    },
    selectType: {
      type: String,
      default: 'multiple',
    },
    helpText: {
      type: String,
      default: '',
    },
    isLoading: {
      type: Boolean,
      default: true
    },
    isLoadingUsers: {
      type: Boolean,
      default: true
    },
  },

  data () {
    return {
      showAddUser: false,
      onlySelected: false,
      filter: '',
      pagination: {
        rowsPerPage: 10
      },
      columns: [
        {
          name: 'name',
          label: 'Name',
          field: 'name',
          required: true,
          align: 'left',
          sortable: true,
        },
        {
          name: 'affiliation',
          label: 'Affiliation',
          field: 'affiliation',
          required: true,
          align: 'left',
          sortable: true
        },
        {
          name: 'email',
          label: 'Email',
          field: 'email',
          align: 'left',
          required: true,
          sortable: true
        },
        {
          name: 'orcid',
          label: 'Orcid',
          field: 'orcid',
          align: 'left',
          required: true,
          sortable: true
        },
      ]

    }
  },

  methods: {
    showAddUserDialog (event) {
      event.preventDefault();
      this.showAddUser = true;
    },

    updateSelection(event, selectedArray) {
      event.preventDefault();
      this.$emit('input', selectedArray);
    },

    deleteUserTag(event, keyName) {
      event.preventDefault();
      this.$delete(this.newEntry.extra, keyName);
    },

    setField(event, data) {
      event.preventDefault();
      if (this.fieldDataName === 'organisation')
        
        this.$store.dispatch('entries/setEntryFields', data);
    },

    loadData() {
      this.$store.dispatch('entries/resetEntryList')
        .then(() => {
          this.loading = true
          this.$store.dispatch('entries/getEntries', 'user')
            .finally(() => this.loading = false)
        })
    },

  },
}
</script>
