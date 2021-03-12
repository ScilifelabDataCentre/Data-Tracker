<template>
<div>
  <div v-if="isNew && !('order' in dataset)"
       class="q-my-sm">
    <q-table flat
             title="Select an order"
             :data="onlySelected ? selectedOrder : orders"
             :columns="columns"
             row-key="_id"
             :loading="isLoadingOrders"
             :filter="filter"
             selection="single"
             :selected.sync="selectedOrder"
             :pagination.sync="pagination"
             no-data-label="No entries found"
             :no-results-label="filter + ' does not match any entries'">
      <template v-slot:top-right>
        <q-checkbox v-model="onlySelected"
                    label="Only selected"
                    class="q-mx-md"/>
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
    <q-btn class="q-mt-sm"
           label="Confirm selected order"
           color="primary"
           @click="confirmOrder"
           :disable="selectedOrder.length === 0"
           :loading="isLoadingOrderData"/>
  </div>

  <div v-else>
    <div class="q-my-lg">
      <q-field v-if="!isNew"
               class="q-my-sm"
               label="UUID"
	       stack-label
	       filled>
        <template v-slot:prepend>
          <q-icon name="label_important" />
        </template>
        <template v-slot:control>
          {{ dataset._id }}
        </template>
      </q-field>
      <q-field class="q-my-sm"
               v-if="'order' in dataset"
               label="Order UUID"
	       stack-label
	       filled>
        <template v-slot:prepend>
          <q-icon name="label_important" />
        </template>
        <template v-slot:control>
          {{ dataset.order }}
        </template>
      </q-field>
    </div>

    <q-input id="dataset-title"
             class="q-my-md"
             label="Title"
             v-model="title"
             outlined>
      <template v-slot:prepend>
        <q-icon name="title" />
      </template>
    </q-input>
    <q-input id="dataset-description"
             class="q-my-md"
             type="textarea"
             label="Description"
             v-model="description"
             autogrow
             outlined
             bottom-slots>
      <template v-slot:prepend>
        <q-icon name="description" />
      </template>
      <template v-slot:hint>
        Use <a class="std-link"
               href="https://www.markdownguide.org/cheat-sheet/"
               target="_blank">Markdown</a> to format the description.
      </template>
    </q-input>

    <q-list bordered
            class="q-my-lg">
      <q-expansion-item expand-separator
                        icon="fas fa-tags"
                        label="Tags"
                        caption="Set labels (tags)">
        <q-card>
          <q-card-section>
            <tag-editor :isLoading="isLoading"
                        v-model="tags"/>
          </q-card-section>
        </q-card>
      </q-expansion-item>

      <q-expansion-item expand-separator
                        icon="fas fa-tags"
                        label="Properties"
                        caption="Set properties (key: value)">
        <q-card>
          <q-card-section>
            <property-editor fieldTitle="Properties"
                             helpText="Set properties"
                             fieldDataName="properties"
                             :isLoading="isLoading"/>
          </q-card-section>
      </q-card>
    </q-expansion-item>
  </q-list>
  </div>
</div>
</template>

<script>
import PropertyEditor from 'components/PropertyEditor.vue'
import TagEditor from 'components/TagEditor.vue'

export default {
  name: 'DatasetEdit',

  components: {
    'property-editor': PropertyEditor,
    'tag-editor': TagEditor,
  },

  props: {    
    isLoading: {
      type: Boolean,
      default: true
    },
    isNew: {
      type: Boolean,
      default: false,
    }
  },

  computed: {
    dataset: {
      get () {
        return this.$store.state.entries.entry;
      },
    },

    tags: {
      get () {
        return this.$store.state.entries.entry.tags;
      },
      set (newValue) {
        this.$store.dispatch('entries/setEntryFields', {'tags': newValue});
      },
    },

    orders: {
      get () {
        return this.$store.state.entries.entryList;
      },

    },

    title: {
      get () {
        return this.$store.state.entries.entry.title;
      },
      set (newValue) {
        this.$store.dispatch('entries/setEntryFields', {'title': newValue});
      },
    },

    description: {
      get () {
        return this.$store.state.entries.entry.description;
      },
      set (newValue) {
        this.$store.dispatch('entries/setEntryFields', {'description': newValue});
      },
    },

    currentUser: {
      get () {
        return this.$store.state.currentUser.info;
      },
    },
  },

  data () {
    return {
      addDsError: '',
      deleteDsError: '',
      linkDesc: '',
      tagName: '',
      isSending: false,
      selectedOrder: [],
      isLoadingOrders: false,
      isLoadingOrderData: false,
      isLoadingUsers: false,
      onlySelected: false,
      filter: '',
      pagination: {
        rowsPerPage: 5
      },
      columns: [
        {
          name: '_id',
          label: 'UUID',
          field: '_id',
          align: 'left',
          required: true,
          sortable: true
        },
        {
          title: 'title',
          label: 'Title',
          field: 'title',
          required: true,
          align: 'left',
          sortable: true,
        },
      ]
    }
  },

  methods: {
    confirmOrder() {
      this.isLoadingOrderData = true;
      this.$store.dispatch('entries/setEntryFields',
                           {'order': this.selectedOrder[0]._id});
      this.$store.dispatch('entries/getLocalEntry',
                           {'id': this.selectedOrder[0]._id,
                            'dataType': 'order'})
        .then((data) => {
          this.$store.dispatch('entries/setEntryFields',
                               {
                                 'title': data.title,
                                 'description': data.description,
                                 'properties': data.properties,
                                 'tags': data.tags,
                               });
          this.isLoadingOrderData = false;
        })
        .catch(() => this.isLoadingOrders = false);
    }
  },

  mounted () {
    if (this.isNew) {
      this.isLoadingOrders = true;
      this.$store.dispatch('entries/resetEntryList')
        .then(() => {
          this.$store.dispatch('entries/getEntries', 'order')
            .then(() => this.isLoadingOrders = false)
            .catch(() => this.isLoadingOrders = false);
        });
    }
  }
}
</script>
