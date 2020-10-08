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
                    @click="deleteEntry"
                    icon="fas fa-trash"
                    label="Delete" />
      <q-fab-action color="grey-6"
                    @click="cancelEdit"
                    icon="cancel"
                    label="Cancel" />
    </q-fab>
  </q-page-sticky>

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

    deleteEntry(event) {
      event.preventDefault();
      let response = confirm("Are you sure you want to delete the order?")
      if (response) {
        this.$store.dispatch('orders/deleteOrder', this.uuid)
          .then(() => {
            this.$router.push({ 'name': 'Order Browser' });
          })
          .catch((err) => {});
      }
    },

    saveEdit (event) {
      event.preventDefault();
      let orderToSubmit = JSON.parse(JSON.stringify(this.order));
      let field = '';
      for (field of ['authors', 'generators', 'editors']) {
        orderToSubmit[field] = orderToSubmit[field].map(item => item._id);
        }
      orderToSubmit.organisation = orderToSubmit.organisation._id;
      // rename _id to id, otherwise it won't be dispatched
      orderToSubmit.id = orderToSubmit._id;
      orderToSubmit.tags_standard = orderToSubmit.tagsStandard
      orderToSubmit.tags_user = orderToSubmit.tagsUser
      delete orderToSubmit._id;
      delete orderToSubmit.tagsStandard;
      delete orderToSubmit.tagsUser;
      delete orderToSubmit.datasets;
      this.$store.dispatch('orders/saveOrder', orderToSubmit)
        .then((response) => { })
        .catch((err) => { });
      this.editMode = false;
      this.currentTab = "preview";
    },

    loadData () {
      this.isLoading = true;
      if (this.uuid === '') {
        this.$store.dispatch('orders/getEmptyOrder', this.uuid)
          .then(() => this.isLoading = false)
          .catch(() => this.isLoading = false);
      }
      else {
        this.$store.dispatch('orders/getOrder', this.uuid)
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
