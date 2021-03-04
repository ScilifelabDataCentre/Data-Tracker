<template>
<q-page padding>
  <div class="flex">
    <q-btn-dropdown v-show="uuid !== ''"
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
                :disable="uuid === ''"
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
                :disable="uuid === ''"
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
           icon="cancel"
           label="Cancel"
           color="grey-6"
           @click="cancelEdit" />

    <q-btn class="q-ml-sm q-mr-lg"
           v-show="editMode"
           icon="save"
           label="Save"
           color="positive"
           :loading="isSaving"
           @click="saveEdit" />

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

  <q-tab-panels v-model="currentTab">
    <q-tab-panel name="preview">
      <order-about />
    </q-tab-panel>

    <q-tab-panel name="edit">
      <order-edit :isLoading="isLoading"/>
    </q-tab-panel>

  </q-tab-panels>

  <log-viewer v-model="showLogs"
              :dataType="dataType"
              :uuid="uuid" />

  <q-dialog v-model="showConfirmDelete">
    <q-card>
      <q-card-section class="row items-center">
        <q-avatar icon="fas fa-trash" color="alert" text-color="primary" />
        <span class="q-ml-sm">Are you sure you want to delete this {{ dataType }}?</span>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="grey-7" v-close-popup />
        <q-btn flat label="Delete" color="negative" @click="deleteEntry" />
        <q-spinner v-show="isDeleting"
                   color="negative"
                   size="1.5em" />
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
import OrderAbout from 'components/OrderAbout.vue'
import OrderEdit from 'components/OrderEdit.vue'
import LogViewer from 'components/LogViewer.vue'

export default {
  name: 'OrderInfo',

  components: {
    'order-about': OrderAbout,
    'order-edit': OrderEdit,
    'log-viewer': LogViewer,
  },
  
  props: {
    uuid: {
      type: String,
      default: '',
    },
  },


  watch: {
    $route() {
      this.loadData();
    }
  },

  computed: {
    order: {
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
      dataType: 'order',
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
          this.$router.push({ 'name': 'Order Browser' });
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
      this.$store.dispatch('entries/deleteEntry', {'id': this.uuid,
                                                'dataType': this.dataType})
        .then(() => {
          this.$router.push({ 'name': 'Order Browser' });
          this.showConfirmDelete = false;
        })
        .catch((err) => this.error = true);
    },

    saveEdit (event) {
      event.preventDefault();
      if (this.order.title === '')
        return;
      let orderToSubmit = JSON.parse(JSON.stringify(this.order));
      let field = '';
      for (field of ['authors', 'generators', 'editors']) {
        orderToSubmit[field] = orderToSubmit[field].map(item => item._id);
      }
      if (orderToSubmit.organisation.length && '_id' in orderToSubmit.organisation[0])
        orderToSubmit.organisation = orderToSubmit.organisation[0]._id;
      else
        orderToSubmit.organisation = '';
      // rename _id to id, otherwise it won't be dispatched
      if (this.uuid !== '')
        orderToSubmit.id = orderToSubmit._id;
      else
        orderToSubmit.id = ''
      delete orderToSubmit._id;
      delete orderToSubmit.datasets;
      this.isSaving = true;
      this.$store.dispatch('entries/saveEntry', {data: orderToSubmit,
                                                 dataType: this.dataType})
        .then((response) => {
          if (this.uuid === '') {
            this.$router.push({ name: 'Order About', params: { 'uuid': response.data._id } });
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
        this.$store.dispatch('entries/resetEntry')
          .then(() => {
            this.$store.dispatch('entries/getEmptyEntry', this.dataType)
              .then(() => this.isLoading = false)
              .catch(() => this.isLoading = false);
          });
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
      this.currentTab = 'edit';
    }
  }

}
</script>
