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
      Lorem ipsum dolor sit amet consectetur adipisicing elit.
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

export default {
  name: 'OrderInfo',

  components: {
    'order-about': OrderAbout,
  },
  
  props: {
    uuid: {
      type: String,
      required: true
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
      this.editMode = !this.editMode;
      this.currentTab = "edit";
    },

    cancelEdit () {
      this.editMode = false;
      this.loadData();
      this.currentTab = "preview";
    },

    saveEdit () {
      this.editMode = false;
      // dispatch job to save entry as provided in state
    },

    loadData () {
      this.isLoading = true;
      this.$store.dispatch('orders/getOrder', this.uuid)
        .then(() => this.isLoading = false)
        .catch(() => this.isLoading = false);
    }
  },
  
  mounted () {
    this.loadData();
  }

}
</script>
