<template>
<q-table
  :title="fieldTitle"
  :data="users"
  :columns="columns"
  row-key="_id"
  :filter="filter"
  :selection="selectType"
  :selected.sync="selected"
  :pagination.sync="pagination"
  no-data-label="No entries found"
  :no-results-label="filter + ' does not match any entries'">
  <template v-slot:top-left>
    <div class="q-table__title">
      {{ fieldTitle }}
      <q-btn flat
             round
             dense
             push
             color="primary"
             icon="info"
             v-if="helpText.length > 0">
        <q-popup-proxy>
          <q-banner>
            {{ helpText }}
          </q-banner>
        </q-popup-proxy>
      </q-btn>
    </div>
  </template>
  <template v-slot:top-right>
    <q-input rounded
             outlined
             dense
             debounce="300"
             v-model="filter"
             placeholder="Search">
      <template v-slot:append>
        <q-icon name="search" />
      </template>
    </q-input>
  </template>
</q-table>
</template>

<script>
export default {
  name: 'UserSelector',

  computed: {
    users: {
      get () {
        return this.$store.state.adminUsers.userList;
      },
    },

    fieldEntries: {
      get () {
        return this.$store.state.orders.order[this.fieldDataName];
      }
    },

    orderData: {
      get () {
        return this.$store.state.orders.order;
      }
    },

    currentUser: {
      get () {
        return this.$store.state.currentUser.info;
      },
    },
  },

  watch: {
    selected (newValue, OldValue) {
      let data = {};
      data.[this.fieldDataName] = newValue;
      this.$store.dispatch('orders/setOrderFields', data);
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
  },

  
  data () {
    return {
      filter: '',
      pagination: {
        rowsPerPage: 5
      },
      selected: [],

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
          sortable: true
        },
        {
          name: 'email',
          label: 'Email',
          field: 'email',
          required: true,
          sortable: true
        },
        {
          name: 'orcid',
          label: 'Orcid',
          field: 'orcid',
          required: true,
          sortable: true
        },
      ]

    }
  },

  methods: {
    deleteUserTag(event, keyName) {
      event.preventDefault();
      this.$delete(this.newOrder.extra, keyName);
    },

    setField(event, data) {
      event.preventDefault();
      this.$store.dispatch('orders/setOrderFields', data);
    },
  },

  mounted () {
    this.selected = this.$store.state.orders.order[this.fieldDataName];
    if (typeof this.selected === 'object') {
      this.selected = [this.selected];
    }
  }
}
</script>
