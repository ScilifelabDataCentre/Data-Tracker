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

  <q-page-sticky position="top-right"
		 :offset="[18, 18]">
    <q-fab v-model="editMode"
           vertical-actions-align="center"
           :label="editMode ? 'Save' : 'Edit'"
           :color="editMode ? 'positive' : 'accent'"
           icon="edit"
           active-icon="save"
           direction="down"
           @show="activateEditMode"
           @hide="saveEdit">
        <q-fab-action color="negative" @click="cancelEdit" icon="cancel" label="Cancel" />
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
    },
    isNew: {
      type: Boolean,
      default: false
    }
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

    cancelEdit () {
      this.editMode = false;
      this.loadData();
      this.currentTab = "preview";
    },

    saveEdit () {
      // dispatch job to save entry as provided in state
      this.editMode = false;
      this.currentTab = "preview";
    },

    loadData () {
      this.isLoading = true;
      if (this.isNew) {
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
  }

}
</script>
