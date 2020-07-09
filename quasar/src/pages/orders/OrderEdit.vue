<template>
<q-page padding>
  <q-card>
    <q-card-section>
      <q-field
	v-if="newOrder.id !== ''"
        label="UUID"
	stack-label
	  filled
          >
	  <template v-slot:prepend>
            <q-icon name="label_important" />
          </template>
	  <template v-slot:control>
            {{ newOrder.id }}
          </template>
	</q-field>
      </q-card-section>

      <q-card-section>
        <div class="text-h6 q-mt-sm q-mb-xs">General</div>
        <q-input id="order-title"
                 label="Title"
                 v-model="newOrder.title">
	  <template v-slot:prepend>
            <q-icon name="title" />
          </template>
	</q-input>
        <q-input id="order-description"
                 type="textarea"
                 label="Description"
                 v-model="newOrder.description"
                 autogrow>
	  <template v-slot:prepend>
            <q-icon name="description" />
          </template>
	</q-input>
      </q-card-section>

      <q-card-section>
        <q-input id="order-title"
                 label="Creator"
                 v-model="newOrder.creator">
	  <template v-slot:prepend>
            <q-icon name="person" />
          </template>
        </q-input>

        <q-input id="order-title"
                 label="Receiver"
                 v-model="newOrder.receiver">
	  <template v-slot:prepend>
            <q-icon name="person" />
          </template>
        </q-input>

        <div class="text-h6 q-mt-sm q-mb-xs">Datasets</div>
        <div class="row flex">
          <q-btn flat icon="add" color="primary" @click="addDataset"/>
         </div>
        <q-list dense>
          <q-item v-for="(link, i) in newOrder.links" :key="i">
            <q-input :label="link.description"
                     v-model="link.url"
                     stack-label>
              <template v-slot:prepend>
                <q-icon name="link" />
              </template>
              <template v-slot:append>
                <q-btn icon="delete"
                       flat
                       size="sm"
                       round
                       @click="deleteLink($event, i)" />
              </template>
            </q-input>
          </q-item>
        </q-list>
      </q-card-section>

      <q-card-section>
        <div class="text-h6 q-mt-sm q-mb-xs">User Tags</div>
        <div class="row flex">
          <q-input class="col-5 q-mr-md"
                   id="order-description"
                   label="User tag name"
                   v-model="tagName" />
           <q-btn flat icon="add" color="primary" @click="addUserTag"/>
         </div>
        <q-list dense>
          <q-item v-for="key in Object.keys(newOrder.extra)" :key="key">
            <q-input :label="key"
                     v-model="newOrder.extra[key]"
                     stack-label>
              <template v-slot:prepend>
                <q-icon name="label" />
              </template>
              <template v-slot:append>
                <q-btn icon="delete"
                       flat
                       size="sm"
                       round
                       @click="deleteUserTag($event, i)" />
              </template>
            </q-input>
          </q-item>
        </q-list>
      </q-card-section>
      <q-card-section>
        <q-btn label="Submit" color="positive" class="q-mr-md" @click="submitOrderForm"/>
        <q-btn label="Cancel" color="blue-grey-4" class="q-mr-lg" @click="cancelChanges"/>
        <q-btn label="Delete" color="negative" class="q-ml-xl" @click="deleteOrder"/>
      </q-card-section>
  </q-card>
  <q-inner-loading :showing="loading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
</q-page>
</template>

<script>
export default {
  name: 'OrderEdit',

  props: {
    uuid: {
      type: String,
      required: true
    }
  },

  computed: {
    origOrder: {
      get () {
        return this.$store.state.orders.order;
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
      loading: true,
      newOrder: {
        id: '',
        title: '',
        description: '',
        datasets: '',
        creator: '',
        receiver: '',
        extra: {}
      },
      linkDesc: '',
      tagName: '',
    }
  },

  methods: {    
    addDataset(event) {
      event.preventDefault();
      this.$store.dispatch('addDataset', {
        'data': {
          'title': this.order.title + ' dataset ' + (this.order.datasets.length + 1)
        },
        'uuid': this.uuid
      })
        .then(() => {
          this.$store.dispatch('getOrder', this.uuid);
        });
    },

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

    submitOrderForm(event) {
      event.preventDefault();
      this.orderToSubmit = JSON.parse(JSON.stringify(this.Neworder));
      delete this.orderToSubmit.datasets;
      this.$store.dispatch('orders/saveOrder', this.orderToSubmit)
        .then(() => {
          this.$router.push({'name': 'Order About', params: { 'uuid': this.uuid } });
        });
    },
    
    deleteOrder(event) {
      event.preventDefault();
      this.$store.dispatch('orders/deleteOrder', this.newOrder.id)
        .then(() => {
          this.$router.push({ 'name': 'Order Browser' });
        });
    },

    cancelChanges(event) {
      event.preventDefault();
      this.$router.push({'name': 'Order About', params: { 'uuid': this.newOrder.id } });
    },
    
  },
  
  mounted () {
    this.$store.dispatch('orders/getOrder', this.uuid)
      .then((response) => {
        this.newOrder = JSON.parse(JSON.stringify(response.data.order));
        this.newOrder.id = this.newOrder._id;
        delete this.newOrder._id;
        this.newOrder.creator = this.newOrder.creator.identifier;
        this.loading = false;
      })
      .catch(() => this.loading = false);
  }
}
</script>
