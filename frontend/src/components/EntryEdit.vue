<template>
<div>
  <div v-if="this.newEntry && this.dataType === 'dataset'"
       class="q-my-sm">
    <q-table flat
             title="Parent order for the dataset"
             :data="onlySelectedOrder ? parentOrder : orders"
             :columns="columns"
             row-key="id"
             :loading="isLoadingOrders"
             :filter="filter"
             selection="single"
             :selected.sync="parentOrder"
             :pagination.sync="pagination"
             no-data-label="No entries found"
             :no-results-label="filter + ' does not match any entries'">
      <template v-slot:top-right>
        <q-checkbox v-model="onlySelectedOrder"
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
           label="Load data from order"
           color="primary"
           @click="confirmOrder"
           :disable="parentOrder.length === 0"
           :loading="isLoadingOrderData"/>
  </div>

  <div v-if="dataType !== 'dataset' || entry.order || parentOrder.length">
    <q-field v-if="!newEntry"
             label="UUID"
             class="q-mb-lg"
	     stack-label
	     filled>
      <template v-slot:prepend>
        <q-icon name="label_important" />
      </template>
      <template v-slot:control>
        {{ entry.id }}
      </template>
    </q-field>
    
    <q-input id="entry-title"
             class="q-my-md"
             label="Title"
             v-model="title"
             :rules="[ function (val) { return val.length > 0 || 'Title cannot be empty' }]"
             outlined>
      <template v-slot:prepend>
        <q-icon name="title" />
      </template>
    </q-input>
    
    <div class="q-my-md">
      <q-input id="entry-description"
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
                 rel="noopener"
                 target="_blank">Markdown</a> to format the description.
        </template>
      </q-input>
    </div>
    
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
      
      <q-separator />
      
      <q-expansion-item expand-separator
                        v-if="dataType === 'collection'"
                        icon="fas fa-chart-area"
                        label="Datasets"
                        caption="Datasets to include in the entry">
        <q-table flat
                 :data="onlySelectedDatasets ? selectedDatasets : datasets"
                 :columns="columns"
                 row-key="id"
                 :loading="isLoadingDatasets"
                 :filter="filter"
                 selection="multiple"
                 :selected.sync="selectedDatasets"
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
                       placeholder="Search">
                <template v-slot:append>
                  <q-icon name="search" />
                </template>
              </q-input>
              <q-toggle class="q-mx-sm"
                        left-label
                        v-model="onlySelectedDatasets"
                        label="Show selected only"
                        color="primary"/>
            </div>
          </template>
        </q-table>
      </q-expansion-item>
      <div v-if="dataType === 'order'">
        <q-expansion-item expand-separator
                          icon="far fa-user"
                          label="Authors"
                          caption="The ones who own the sample (e.g. PI)">
          <user-selector fieldTitle="Authors"
                         fieldDataName="authors"
                         class="q-my-sm"
                         helpText="The ones who own the sample (e.g. PI)"
                         :isLoadingUsers="isLoadingUsers"
                         :isLoading="isLoading"/>
        </q-expansion-item>
        
        <q-expansion-item expand-separator
                          icon="far fa-user"
                          label="Generators"
                          caption="The ones who generated the data (e.g. Facility)">
          <user-selector fieldTitle="Generators"
                         fieldDataName="generators"
                         class="q-my-sm"
                         helpText="The ones who generated the data (e.g. Facility)"
                         :isLoadingUsers="isLoadingUsers"
                         :isLoading="isLoading"/>
        </q-expansion-item>
        
        <q-expansion-item expand-separator
                          icon="far fa-user"
                          label="Organisation"
                          caption="The data controller (e.g. university)">
          <user-selector fieldTitle="Organisation"
                         fieldDataName="organisation"
                         selectType="single"
                         class="q-my-sm"
                         helpText="The data controller (e.g. university)"
                         :isLoadingUsers="isLoadingUsers"
                         :isLoading="isLoading"/>
        </q-expansion-item>
      </div>
      <q-expansion-item expand-separator
                        v-if="['collection', 'order'].includes(dataType)"
                        icon="far fa-user"
                        label="Editors"
                        caption="Users who may edit this entry and the associated datasets">
        <user-selector fieldTitle="Editors"
                       fieldDataName="editors"
                       class="q-my-sm"
                       helpText="Users who may edit this entry and the associated datasets"
                       value="entry.editors"
                       :isLoadingUsers="isLoadingUsers"
                       :isLoading="isLoading"/>
      </q-expansion-item>
    </q-list>
  </div>
</div>
</template>

<script>
import UserSelector from 'components/UserSelector.vue'
import PropertyEditor from 'components/PropertyEditor.vue'
import TagEditor from 'components/TagEditor.vue'

export default {
  name: 'EntryEdit',
  
  components: {
    'user-selector': UserSelector,
    'property-editor': PropertyEditor,
    'tag-editor': TagEditor,
  },
  
  props: {    
    isLoading: {
      type: Boolean,
      default: true
    },
    dataType: {
      type: String,
      required: true,
    },
    newEntry: {
      type: Boolean,
      default: false
    },
  },
  
  computed: {
    entry: {
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

    title: {
      get () {
        return this.$store.state.entries.entry.title;
      },
      set (newValue) {
        this.$store.dispatch('entries/setEntryFields', {'title': newValue});
      },
    },

    parentOrder: {
      get () {
        return this.$store.state.entries.parentOrder.length ? [{id: this.$store.state.entries.parentOrder}] : [];
      },
      set (newValue) {
        this.$store.dispatch('entries/setParentOrder', newValue.length ? newValue[0]['id'] : '');
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

    selectedDatasets: {
      get () {
        if (this.isLoading || this.dataType !== 'collection')
          return [];
        return JSON.parse(JSON.stringify(this.$store.state.entries.entry['datasets']));
      },

      set (newValue) {
        this.$store.dispatch('entries/setEntryFields', {'datasets': newValue});
      }
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
      isLoadingUsers: false,
      isLoadingDatasets: false,
      datasets: [],
      // for new datasets
      isLoadingOrders: false,
      isLoadingOrderData: false,
      orders: [],
      onlySelectedDatasets: false,
      onlySelectedOrder: false,
      filter: '',
      pagination: {
        rowsPerPage: 10
      },
      columns: [
        {
          title: 'title',
          label: 'Title',
          field: 'title',
          required: true,
          align: 'left',
          sortable: true,
        },
        {
          name: 'id',
          label: 'UUID',
          field: 'id',
          align: 'left',
          required: true,
          sortable: true
        },
      ]

    }
  },

  methods: {
    setField(event, data) {
      event.preventDefault();
      this.$store.dispatch('entries/setEntryFields', data);
    },
    confirmOrder() {
      this.isLoadingOrderData = true;
      this.$store.dispatch('entries/getLocalEntry',
                           {'id': this.parentOrder[0].id,
                            'dataType': 'order'})
        .then((data) => {
          this.$store.dispatch('entries/setEntryFields',
                               {
                                 'title': data.title,
                                 'description': data.description,
                                 'properties': data.properties,
                                 'tags': data.tags,
                               });
        })
        .finally(() => this.isLoadingOrderData = false);
    }
  },

  mounted () {
    this.$store.dispatch('entries/resetEntryList');
    if (['order', 'collection'].includes(this.dataType)) {
      this.isLoadingUsers = true;
      this.$store.dispatch('entries/getEntries', 'user')
        .finally(() => this.isLoadingUsers = false);
    }
    if (this.dataType === 'collection') {
      this.isLoadingDatasets = true;
      this.$store.dispatch('entries/getLocalEntries', 'dataset')
        .then((datasets) => this.datasets = datasets)
        .finally(() => this.isLoadingDatasets = false);
    }
    else if (this.newEntry && this.dataType === 'dataset') {
      this.isLoadingOrders = true;
      
      this.$store.dispatch('entries/getLocalEntries', 'order')
        .then((orders) => this.orders = orders)
        .finally(() => this.isLoadingOrders = false);
    }
  }
}
</script>
