<template>
<div>
  <q-card class="q-my-sm">
    <q-card-section>
      <q-field v-if="order._id !== ''"
               label="UUID"
	       stack-label
	       filled>
        <template v-slot:prepend>
          <q-icon name="label_important" />
        </template>
        <template v-slot:control>
          {{ order._id }}
        </template>
      </q-field>
    </q-card-section>
  
    <q-card-section>
      <q-input id="order-title"
               label="Title"
               v-model="title">
        <template v-slot:prepend>
          <q-icon name="title" />
        </template>
      </q-input>
      <q-input id="order-description"
               type="textarea"
               label="Description"
               v-model="description"
               autogrow>
        <template v-slot:prepend>
          <q-icon name="description" />
        </template>
      </q-input>
    </q-card-section>
  </q-card>

  <user-selector fieldTitle="Authors"
                 fieldDataName="authors"
                 class="q-my-sm"
                 helpText="The ones who own the sample (e.g. PI)"/>

  <user-selector fieldTitle="Generators"
                 fieldDataName="generators"
                 class="q-my-sm"
                 helpText="The ones who generated the data (e.g. Facility)"/>

  <user-selector fieldTitle="Organisation"
                 fieldDataName="organisation"
                 selectType="single"
                 class="q-my-sm"
                 helpText="The data controller (e.g. university)"/>

  <user-selector fieldTitle="Editors"
                 fieldDataName="editors"
                 class="q-my-sm"
                 helpText="Users who may edit this order and the associated datasets"/>
</div>
</template>

<script>
import UserSelector from 'components/UserSelector.vue'

export default {
  name: 'OrderEdit',

  components: {
    'user-selector': UserSelector
  },
  
  computed: {
    order: {
      get () {
        return this.$store.state.orders.order;
      },
    },

    title: {
      get () {
        return this.$store.state.orders.order.title;
      },
      set (newValue) {
        this.$store.dispatch('orders/setOrderFields', {'title': newValue});
      },
    },

    description: {
      get () {
        return this.$store.state.orders.order.description;
      },
      set (newValue) {
        this.$store.dispatch('orders/setOrderFields', {'description': newValue});
      },
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
      userList: [],
    }
  },

  methods: {
    addUserTag(event) {
      event.preventDefault();
      if (this.tagName !== '') {
        if (! Object.keys(this.newOrder.extra).includes(this.tagName)) {
          this.$set(this.newOrder.extra, this.tagName, '');
        }
      }
      this.tagName = '';
    },

    deleteUserTag(event, keyName) {
      event.preventDefault();
      this.$delete(this.newOrder.extra, keyName);
    },

    setField(event, data) {
      event.preventDefault();
      this.$store.dispatch('orders/setOrderFields', data);
    },
  },

  mounted () {
    this.$store.dispatch('adminUsers/getUsers');    
  }
}
</script>
