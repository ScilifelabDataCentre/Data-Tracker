<template>
<q-page padding>
  <div v-if="badEntry">
    <q-banner>
      The entry <span class="text-negative text-weight-medium">{{ uuid }}</span> could not be found.
    </q-banner>
    <q-btn flat
           no-caps
           class="q-my-md"
           color="primary"
           :to="{ 'name': 'Collection Browser' }"
           :label="'Back to ' + dataType + ' browser'" />
  </div>
  <div v-else>
    <div class="row justify-between">
      <div class="flex">
        <q-btn-dropdown v-show="uuid !== '' && 'editors' in entry"
                        class="q-mr-sm"
                        color="secondary"
                        icon="fas fa-cog"
                        label="Options">
          <q-list dense>
            <q-item :disable="editMode"
                    v-close-popup
                    clickable
                    @click="toggleEditMode">
              <q-item-section avatar>
                <q-avatar icon="edit"
                          text-color="primary" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Edit</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item clickable
                    v-close-popup
                    @click="confirmDelete">
              <q-item-section avatar>
                <q-avatar icon="fas fa-trash" text-color="negative" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Delete</q-item-label>
              </q-item-section>
            </q-item>
            
            <q-item clickable
                    v-close-popup
                    @click="showLogs = true">
              <q-item-section avatar>
                <q-avatar icon="fas fa-history" text-color="secondary" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Entry History</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
        
        <q-btn class="q-mx-sm"
               v-show="editMode"
               icon="save"
               label="Save"
               color="positive"
               :loading="isSaving"
               :disable="entry.title === '' ? true : false"
               @click="saveEdit" />
        
        <q-btn class="q-ml-sm q-mr-lg"
               v-show="editMode"
               icon="cancel"
               label="Cancel"
               color="grey-6"
               @click="cancelEdit" />
        
        <q-tabs v-show="editMode"
                v-model="currentTab"
                dense
                class="text-grey-8"
                active-color="primary"
                indicator-color="primary"
                align="center"
                narrow-indicator>
          <q-tab name="edit" label="Edit" />
          <q-tab name="preview" label="Preview" />
        </q-tabs>
      </div>
      <q-btn type="a"
             :href="'/api/v1/' + dataType + '/' + uuid"
             color="primary"
             label="JSON (API)" />
    </div>
    <q-tab-panels v-model="currentTab">
      <q-tab-panel name="preview">
        <entry-about :isLoading="isLoading" :dataType="dataType" />
      </q-tab-panel>
      
      <q-tab-panel name="edit">
        <entry-edit :isLoading="isLoading"  :dataType="dataType" />
      </q-tab-panel>
    </q-tab-panels>

    <log-viewer v-if="'editors' in entry"
                v-model="showLogs"
                :dataType="dataType"
                :uuid="uuid" />
    
    <q-dialog v-model="showConfirmDelete">
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="fas fa-trash" color="alert" text-color="primary" />
          <span class="q-ml-sm">Are you sure you want to delete this {{ dataType }}?</span>
        </q-card-section>
        
        <q-card-actions align="right">
          <q-spinner v-show="isDeleting"
                     color="negative"
                     size="1.5em"
                     class="q-mr-sm" />
          <q-btn flat label="Delete" color="negative" @click="deleteEntry" />
          <q-btn flat label="Cancel" color="grey-7" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
    
    <q-dialog v-model="error">
      <q-card>
        <q-card-section class="row items-center">
          <q-avatar icon="fas fa-exclamation-triangle" color="white" text-color="negative" />
          <span class="q-ml-sm">The operation failed. Please try again.</span>
        </q-card-section>
        
        <q-card-actions align="right">
        <q-btn flat label="Dismiss" color="negative" @click="error=false" v-close-popup />
      </q-card-actions>
    </q-card>
  </q-dialog>
  </div>
  <q-inner-loading :showing="isLoading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
</q-page>
</template>

<script>
import { format } from 'quasar'
const { capitalize } = format

import EntryAbout from 'components/EntryAbout.vue'
import EntryEdit from 'components/EntryEdit.vue'
import LogViewer from 'components/LogViewer.vue'

export default {
  name: 'EntryInfo',

  components: {
    'entry-about': EntryAbout,
    'entry-edit': EntryEdit,
    'log-viewer': LogViewer,
  },
  
  props: {
    uuid: {
      type: String,
      default: '',
    },
    dataType: {
      type: String,
      required: true,
    },
  },

  computed: {
    entry: {
      get () {
        return this.$store.state.entries.entry;
      },
    },

    currentUser: {
      get () {
        return this.$store.state.currentUser.info;
      },
    },
  },

  watch: {
    $route() {
      this.loadData();
    },
  },

  data () {
    return {
      badEntry: false,
      isLoading: true,
      currentTab: 'preview',
      editMode: false,
      showConfirmDelete: false,
      error: false,
      draggingEditButton: false,
      showOptions: false,
      isSaving: false,
      isDeleting: false,
      showLogs: false,
    }
  },

  methods: {
    toggleEditMode () {
      this.editMode = !this.editMode;
      if (this.editMode)
        this.currentTab = "edit";
      else
        this.currentTab = "preview";
    },

    cancelEdit () {
      if (this.uuid === '') {
          this.$router.push({ 'name': capitalize(this.dataType) + ' Browser' });
      }
      this.editMode = false;
      this.loadData();
      this.currentTab = "preview";
    },

    confirmDelete(event) {
      event.preventDefault();
      this.showConfirmDelete = true;
    },

    deleteEntry(event) {
      event.preventDefault();
      this.isDeleting =  true;
      this.$store.dispatch('entries/deleteEntry', {'id': this.uuid,
                                                   'dataType': this.dataType})
        .then(() => {
          console.log(capitalize(this.dataType));
          console.log({ 'name': capitalize(this.dataType) + ' Browser' });
          this.$router.push({ 'name': capitalize(this.dataType) + ' Browser' });
          console.log(capitalize(this.dataType))
          this.showConfirmDelete = false;
        })
        .catch((err) => this.error = true)
        .finally(() => this.isDeleting = false);
    },

    saveEdit (event) {
      event.preventDefault();
      if (this.entry.title === '')
        return;
      let dataToSubmit = {}
      dataToSubmit.title = this.entry.title;
      dataToSubmit.description = this.entry.description;
      dataToSubmit.properties = this.entry.properties;
      dataToSubmit.tags = this.entry.tags;
      if (this.dataType === 'order') {
        dataToSubmit.organisation = this.entry.organisation[0].id;
        for (const key of ['authors', 'generators', 'editors']) {
          dataToSubmit[key] = this.entry[key].map(item => item.id);
        }
      }
      if (this.dataType === 'collection') {
        for (const key of ['editors', 'datasets']) {
          dataToSubmit[key] = this.entry[key].map(item => item.id);
        }
      }
      this.isSaving = true;
      this.$store.dispatch('entries/saveEntry', {id: this.uuid,
                                                 data: dataToSubmit,
                                                 dataType: this.dataType})
        .then((response) => {
          if (this.uuid === '') {
            this.$router.push({ name: 'Collection About', params: { 'uuid': response.data.id } });
          }
          this.loadData();
          this.isSaving = false;
          this.editMode = false;
          this.currentTab = "preview";
        })
        .catch((err) => {
          this.error = true;
          this.isSaving = false;
        });
    },

    loadData () {
      this.isLoading = true;
      if (this.uuid === '') {
        this.$store.dispatch('entries/getEmptyEntry', this.dataType)
          .finally(() => this.isLoading = false);
      }
      else {
        this.$store.dispatch('entries/resetEntry')
          .then(() => {
            this.$store.dispatch('entries/getEntry', {'id': this.uuid,
                                                      'dataType': this.dataType})
              .catch((err) => {
                if (err.response.status === 404)
                  this.badEntry = true;
              })
              .finally(() => this.isLoading = false);
          });
      }
    }
  },
  
  mounted () {
    this.loadData();
    if (this.uuid === '') {
      this.editMode = true;
      this.currentTab = 'edit';
    }
  }

}
</script>
