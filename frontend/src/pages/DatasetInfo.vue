<template>
<q-page padding>
  <div v-if="badEntry">
    <q-banner>
      The entry <span class="text-negative text-weight-medium">{{ uuid }}</span> could not be found.
    </q-banner>
    <q-btn class="q-my-md"
           color="primary"
           :to="{ 'name': 'Dataset Browser' }"
           label="Back to dataset browser" />
  </div>
  <div v-else>
  <div class="row justify-between">
    <div class="flex">
      <q-btn-dropdown v-show="uuid !== '' && 'editors' in dataset"
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
           :href="'/api/v1/dataset/' + uuid + '/'"
           color="primary"
           label="JSON (API)" />
  </div>
  <q-tab-panels v-model="currentTab">
    <q-tab-panel name="preview">
      <dataset-about />
    </q-tab-panel>

    <q-tab-panel name="edit">
      <dataset-edit :isNew="this.uuid === ''"
                    :isLoading="isLoading"/>
    </q-tab-panel>
  </q-tab-panels>

  <log-viewer v-if="'editors' in dataset"
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
import DatasetAbout from 'components/DatasetAbout.vue'
import DatasetEdit from 'components/DatasetEdit.vue'
import LogViewer from 'components/LogViewer.vue'

export default {
  name: 'DatasetInfo',

  components: {
    'dataset-about': DatasetAbout,
    'dataset-edit': DatasetEdit,
    'log-viewer': LogViewer,
  },
  
  props: {
    uuid: {
      type: String,
      default: '',
    },
  },

  computed: {
    dataset: {
      get () {
        return this.$store.state.entries.entry;
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
      dataType: 'dataset',
      error: false,
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
        this.$router.push({ 'name': 'Dataset Browser' });
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
      this.isDeleting = true;
      this.$store.dispatch('entries/deleteEntry', {'id': this.uuid,
                                                   'dataType': this.dataType})
        .then(() => {
          this.$router.push({ 'name': 'Dataset Browser' });
          this.showConfirmDelete = false;
        })
        .catch((err) => this.error = true)
        .finally(() => this.isDeleting = false);
    },

    saveEdit (event) {
      event.preventDefault();
      if (this.dataset.title === '' || this.dataset.order === [])
        return;
      let datasetToSubmit = JSON.parse(JSON.stringify(this.dataset));
      let field = '';
      for (field of ['authors', 'generators', 'editors',
                     'organisation', 'related', 'collections',]) {
        delete datasetToSubmit[field]
      }
      // rename _id to id, otherwise it won't be dispatched
      if (this.uuid !== '')
        datasetToSubmit.id = datasetToSubmit._id;
      else
        datasetToSubmit.id = ''
      delete datasetToSubmit._id;
      if (this.uuid !== '')
        delete datasetToSubmit.order;
      datasetToSubmit.cross_references = datasetToSubmit.crossReferences;
      delete datasetToSubmit.crossReferences;
      this.isSaving = true;
      this.$store.dispatch('entries/saveEntry', {data: datasetToSubmit,
                                                 dataType: this.dataType})
        .then((response) => {
          if (this.uuid === '') {
            this.$router.push({ name: 'Dataset About', params: { 'uuid': response.data._id } });
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
