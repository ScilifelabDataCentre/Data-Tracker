<template>
<q-page padding>
  <q-tabs v-show="editMode"
          v-model="currentTab"
          dense
          class="text-grey"
          active-color="primary"
          indicator-color="primary"
          align="center"
          narrow-indicator>
    <q-tab name="edit" label="Edit" />
    <q-tab name="preview" label="Preview" />
  </q-tabs>

  <q-tab-panels v-model="currentTab">
    <q-tab-panel name="preview">
      <dataset-about />
    </q-tab-panel>

    <q-tab-panel name="edit">
      <dataset-edit :isLoading="isLoading"/>
    </q-tab-panel>

  </q-tab-panels>

  <q-page-sticky position="top-left"
		 :offset="editButtonPos">
    <q-fab v-model="editMode"
           vertical-actions-align="left"
           :label="editMode ? 'Save' : 'Edit'"
           :color="editMode ? 'positive' : 'accent'"
           icon="edit"
           active-icon="save"
           direction="down"
           @show="activateEditMode"
           @hide="saveEdit"
           v-touch-pan.prevent.mouse="moveEditButton">
      <q-fab-action v-show="uuid !== ''"
                    color="negative"
                    @click="confirmDelete"
                    icon="fas fa-trash"
                    label="Delete"
                    external-label/>
      <q-fab-action color="grey-6"
                    @click="cancelEdit"
                    icon="cancel"
                    label="Cancel"
                    external-label/>
    </q-fab>
  </q-page-sticky>

  <q-dialog v-model="showConfirmDelete">
    <q-card>
      <q-card-section class="row items-center">
        <q-avatar icon="fas fa-trash" color="alert" text-color="primary" />
        <span class="q-ml-sm">Are you sure you want to delete this {{ dataType }}?</span>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="grey-9" v-close-popup />
        <q-btn flat label="Delete" color="negative" @click="deleteEntry" v-close-popup />
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

  <q-inner-loading :showing="isLoading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
</q-page>
</template>

<script>
import DatasetAbout from 'components/DatasetAbout.vue'
import DatasetEdit from 'components/DatasetEdit.vue'

export default {
  name: 'DatasetInfo',

  components: {
    'dataset-about': DatasetAbout,
    'dataset-edit': DatasetEdit,
  },
  
  props: {
    uuid: {
      type: String,
      default: '',
    },
  },

  beforeRouteUpdate (to, from, next) {
    console.log(to);
    this.loadData();
    next()
  },

  computed: {
    dataset: {
      get () {
        return this.$store.state.entries.entry;
      },
    },
  },

  data () {
    return {
      isLoading: true,
      currentTab: 'preview',
      editMode: false,
      showConfirmDelete: false,
      dataType: 'dataset',
      error: false,
      editButtonPos: [18, 18],
      draggingEditButton: false,
    }
  },

  methods: {
    moveEditButton (ev) {
      this.draggingEditButton = ev.isFirst !== true && ev.isFinal !== true

      this.editButtonPos = [
        this.editButtonPos[0] + ev.delta.x,
        this.editButtonPos[1] + ev.delta.y
      ]
    },

    activateEditMode () {
      this.editMode = true;
      this.currentTab = "edit";
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
      this.editMode = true;
    },

    deleteEntry(event) {
      event.preventDefault();
      this.$store.dispatch('entries/deleteEntry', {'id': this.uuid,
                                                'dataType': this.dataType})
        .then(() => {
          this.$router.push({ 'name': 'Dataset Browser' });
        })
        .catch((err) => this.error = true);
    },

    saveEdit () {
      this.editMode = true;
      if (this.dataset.title.length === 0)
        return;
      let datasetToSubmit = JSON.parse(JSON.stringify(this.dataset));
      let field = '';
      for (field of ['authors', 'generators', 'editors']) {
        datasetToSubmit[field] = datasetToSubmit[field].map(item => item._id);
      }
      if (datasetToSubmit.organisation.length && '_id' in datasetToSubmit.organisation[0])
        datasetToSubmit.organisation = datasetToSubmit.organisation[0]._id;
      else
        datasetToSubmit.organisation;
      // rename _id to id, otherwise it won't be dispatched
      if (this.uuid !== '')
        datasetToSubmit.id = datasetToSubmit._id;
      else
        datasetToSubmit.id = ''
      delete datasetToSubmit._id;
      datasetToSubmit.tags_standard = datasetToSubmit.tagsStandard;
      datasetToSubmit.tags_user = datasetToSubmit.tagsUser;
      delete datasetToSubmit.tagsStandard;
      delete datasetToSubmit.tagsUser;
      delete datasetToSubmit.datasets;
      this.$store.dispatch('entries/saveEntry', {data: datasetToSubmit,
                                                 dataType: this.dataType})
        .then((response) => {
          this.editMode = false;
          this.currentTab = "preview";
          if (this.uuid === '') {
            this.$router.push({ name: 'Dataset About', params: { 'uuid': response.data._id } });
          }
          this.loadData();
        })
        .catch((err) => {
          this.error = true;
          this.editMode = true;
        });
    },

    loadData () {
      this.isLoading = true;
      if (this.uuid === '') {
        this.$store.dispatch('entries/getEmptyEntry', this.dataType)
          .then(() => this.isLoading = false)
          .catch(() => this.isLoading = false);
      }
      else {
        this.$store.dispatch('entries/resetEntry')
          .then(() => {
            this.$store.dispatch('entries/getEntry', {'id': this.uuid,
                                                      'dataType': this.dataType})
              .then(() => this.isLoading = false)
              .catch(() => this.isLoading = false);
          });
      }
    }
  },
  
  mounted () {
    this.loadData();
    if (this.uuid === '') {
      this.editMode = true;
      this.currentTab = "edit";
    }
  }

}
</script>
