<template>
<div>
  <q-field v-if="collection._id !== ''"
           label="UUID"
           class="q-mb-lg"
	   stack-label
	   filled>
    <template v-slot:prepend>
      <q-icon name="label_important" />
    </template>
    <template v-slot:control>
      {{ collection._id }}
    </template>
  </q-field>

  <q-input id="collection-title"
           class="q-my-md"
           label="Title"
           v-model="title"
           outlined>
    <template v-slot:prepend>
      <q-icon name="title" />
    </template>
  </q-input>

  <div class="q-my-md">
    <q-input id="collection-description"
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
                      icon="fas fa-chart-area"
                      label="Datasets"
                      caption="Datasets to include in the collection">
      <q-table flat
               :data="onlySelected ? selectedDatasets : datasets"
               :columns="columns"
               row-key="_id"
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
                      v-model="onlySelected"
                      label="Show selected only"
                      color="primary"/>
          </div>
        </template>
      </q-table>
    </q-expansion-item>

    <q-expansion-item expand-separator
                      icon="far fa-user"
                      label="Editors"
                      caption="Users who may edit this collection and the associated datasets">
      <user-selector fieldTitle="Editors"
                     fieldDataName="editors"
                     class="q-my-sm"
                     helpText="Users who may edit this collection and the associated datasets"
                     value="collection.editors"
                     :isLoadingUsers="isLoadingUsers"
                     :isLoading="isLoading"/>
    </q-expansion-item>
  </q-list>
</div>
</template>

<script>
import UserSelector from 'components/UserSelector.vue'
import PropertyEditor from 'components/PropertyEditor.vue'
import TagEditor from 'components/TagEditor.vue'

export default {
  name: 'CollectionEdit',

  components: {
    'user-selector': UserSelector,
    'property-editor': PropertyEditor,
    'tag-editor': TagEditor,
  },

  props: {    
    isLoading: {
      type: Boolean,
      default: true
    }
  },

  computed: {
    collection: {
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
        if (this.isLoading)
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
      onlySelected: false,
      datasets: [],
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
          name: '_id',
          label: 'UUID',
          field: '_id',
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
  },

  mounted () {
    this.isLoadingUsers = true;
    this.$store.dispatch('entries/getEntries', 'user')
      .finally(() => this.isLoadingUsers = false);
    this.isLoadingDatasets = true;
    this.$store.dispatch('entries/resetEntryList')
      .then(() => {
        this.$store.dispatch('entries/getLocalEntries', 'dataset')
          .then((datasets) => this.datasets = datasets)
          .finally(() => this.isLoadingDatasets = false);
      });
  }
}
</script>
