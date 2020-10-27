<template>
<div>
  <q-card class="q-my-sm">
    <q-card-section>
      <q-field v-if="collection._id !== ''"
               label="UUID"
	       stack-label
	       filled>
        <template v-slot:prepend>
          <q-icon name="label_important" />
        </template>
        <template v-slot:control>
          {{ collection._id }}
        </template>
      </q-field>
    </q-card-section>
  
    <q-card-section>
      <q-input id="collection-title"
               label="Title"
               v-model="title"
               outlined>
        <template v-slot:prepend>
          <q-icon name="title" />
        </template>
      </q-input>
    </q-card-section>
    <q-card-section>
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
    </q-card-section>
  </q-card>

  <q-card class="q-my-sm">
    <q-card-section>
      <q-table title="Datasets"
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
    </q-card-section>
  </q-card>

  <q-card>
    <q-card-section>
      <tag-editor fieldTitle="Standard Tags"
                  helpText="Set standard tags"
                  fieldDataName="tagsStandard"
                  :isLoading="isLoading"/>
    </q-card-section>
    <q-card-section>
      <tag-editor fieldTitle="User Tags"
                  helpText="Set user tags"
                  fieldDataName="tagsUser"
                  :isLoading="isLoading"/>
    </q-card-section>
  </q-card>

  <user-selector fieldTitle="Editors"
                 fieldDataName="editors"
                 class="q-my-sm"
                 helpText="Users who may edit this collection and the associated datasets"
                 value="collection.editors"
                 :isLoadingUsers="isLoadingUsers"
                 :isLoading="isLoading"/>
</div>
</template>

<script>
import UserSelector from 'components/UserSelector.vue'
import TagEditor from 'components/TagEditor.vue'

export default {
  name: 'CollectionEdit',

  components: {
    'user-selector': UserSelector,
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

    datasets: {
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
    setField(event, data) {
      event.preventDefault();
      this.$store.dispatch('entries/setEntryFields', data);
    },
  },

  mounted () {
    this.isLoadingUsers = true;
    this.$store.dispatch('adminUsers/getUsers')
      .then(() => this.isLoadingUsers = false)
      .catch(() => this.isLoadingUsers = false);
    this.isLoadingDatasets = true;
    this.$store.dispatch('entries/resetEntryList')
      .then(() => {
        this.$store.dispatch('entries/getEntries', 'dataset')
          .then(() => this.isLoadingDatasets = false)
          .catch(() => this.isLoadingDatasets = false);
      });
  }
}
</script>
