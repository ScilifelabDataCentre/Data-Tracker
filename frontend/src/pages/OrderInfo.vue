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
      <order-about />
    </q-tab-panel>

    <q-tab-panel name="edit">
      <order-edit />
    </q-tab-panel>

  </q-tab-panels>

  <q-page-sticky position="top-left"
		 :offset="[14, 14]">
    <q-fab v-model="editMode"
           vertical-actions-align="center"
           :label="editMode ? 'Save' : 'Edit'"
           :color="editMode ? 'positive' : 'accent'"
           icon="edit"
           active-icon="save"
           direction="down"
           @show="activateEditMode"
           @hide="saveEdit">
      <q-fab-action v-show="uuid !== ''"
                    color="negative"
                    @click="confirmDelete"
                    icon="fas fa-trash"
                    label="Delete" />
      <q-fab-action color="grey-6"
                    @click="cancelEdit"
                    icon="cancel"
                    label="Cancel" />
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

  <q-inner-loading :showing="isLoading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
</q-page>
</template>

<script>
import OrderAbout from 'components/OrderAbout.vue'
import OrderEdit from 'components/OrderEdit.vue'

export default {
  name: 'OrderInfo',

  components: {
    'order-about': OrderAbout,
    'order-edit': OrderEdit,
  },
  
  props: {
    uuid: {
      type: String,
      default: '',
    },
  },

  computed: {
    order: {
      get () {
        return this.$store.state.orders.order;
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
    }
  },

  methods: {
    activateEditMode () {
      this.editMode = true;
      this.currentTab = "edit";
    },

    submitOrderForm(event) {
      event.preventDefault();

      let orderToSubmit = JSON.parse(JSON.stringify(this.order));
      this.$store.dispatch('orders/saveOrder', orderToSubmit)
        .then(() => {
          this.$router.push({'name': 'Order About', params: { 'uuid': this.uuid } });
        });
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
      this.editMode = true;
    },
    
    deleteEntry(event) {
      event.preventDefault();
      this.$store.dispatch('entries/deleteEntry', {'id': this.uuid,
                                                'dataType': this.dataType})
        .then(() => {
          this.$router.push({ 'name': 'Order Browser' });
        })
        .catch((err) => {});
    },

    saveEdit (event) {
      event.preventDefault();
      let orderToSubmit = JSON.parse(JSON.stringify(this.order));
      let field = '';
      for (field of ['authors', 'generators', 'editors']) {
        orderToSubmit[field] = orderToSubmit[field].map(item => item._id);
        }
      orderToSubmit.organisation = orderToSubmit.organisation[0]._id;
      // rename _id to id, otherwise it won't be dispatched
      orderToSubmit.id = orderToSubmit._id;
      orderToSubmit.tags_standard = orderToSubmit.tagsStandard
      orderToSubmit.tags_user = orderToSubmit.tagsUser
      delete orderToSubmit._id;
      delete orderToSubmit.tagsStandard;
      delete orderToSubmit.tagsUser;
      delete orderToSubmit.datasets;
      this.$store.dispatch('entries/saveEntry', {data: orderToSubmit,
                                                 dataType: this.dataType})
        .then((response) => { })
        .catch((err) => { });
      this.editMode = false;
      this.currentTab = "preview";
    },

    loadData () {
      this.isLoading = true;
      if (this.uuid === '') {
        this.$store.dispatch('entries/getEmptyEntry', this.dataType)
          .then(() => this.isLoading = false)
          .catch(() => this.isLoading = false);
      }
      else {
        this.$store.dispatch('entries/getEntry', {'id': this.uuid,
                                                  'dataType': this.dataType})
          .then(() => this.isLoading = false)
          .catch(() => this.isLoading = false);
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
