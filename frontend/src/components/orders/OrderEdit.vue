<template>
<div class="order-edit">
  <form @submit="submitOrderForm">
    <div class="field" v-if="newOrder.id !== ''">
      <label for="order-id" class="label">Identifier</label>
      <div class="control">
        <input id="order-id"
               class="input"
               name="ORDER_ID"
               type="text"
               placeholder=""
               v-model="newOrder.id"
               disabled="true"/>
      </div>
    </div>
    <div class="field">
      <label class="label" for="order-title">Title</label>
      <input id="order-title"
             class="input"
             name="ORDER_TITLE"
             type="text"
             placeholder="Title"
             v-model="newOrder.title"/>
    </div>
    <div class="field">
      <label class="label" for="order-description">Description</label>
      <textarea class="textarea"
		id="order-description"
		v-model="newOrder.description"
		name="ORDER_DESCRIPTION"
		type="text"
		placeholder="Description"
		rows="10">
      </textarea>
    </div>
    <div class="field">
      <label class="label" for="order-creator">Creator</label>
      <input id="order-creator"
             class="input"
             v-model="newOrder.creator"
             name="ORDER_CREATOR"
             type="text"
             placeholder="Data creator (e.g. facility name)" />
    </div>
    <div class="field">
      <label class="label" for="order-receiver">Receiver</label>
      <input id="order-receiver"
             class="input"
             v-model="newOrder.receiver"
             name="ORDER_RECEIVER"
             type="text"
             placeholder="User _id or email" />
    </div>
    <div class="columns">
      <div class="column">
        <div class="field">
          <label class="label">Extra fields</label>
          <div class="field is-grouped">
            <input id="order-extra-key"
                   class="input"
                   v-model="extraKey"
                   name="ORDER_EXTRA_KEY"
                   type="text"
                   placeholder="Key" />
            <input id="order-extra-value"
                   class="input"
                   v-model="extraValue"
                   name="ORDER_EXTRA_VALUE"
                   type="text"
                   placeholder="Value" />
            <div class="control">
              <button class="button is-light" @click="saveExtra">Save</button>
            </div>
          </div>
        </div>
      </div>
      <div class="column">
        <table class="table is-fullwidth">
          <thead>
            <th scope="column">Key</th>
            <th scope="column">Value</th>
          </thead>
          <tbody>
            <tr v-for="key in Object.keys(newOrder.extra)" :key="key">
              <td>{{key}}</td>
              <td>{{newOrder.extra[key]}}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="field is-grouped">
      <div class="control">
        <button class="button is-link">Submit</button>
      </div>
      <div class="control">
        <button class="button is-light" @click="cancelChanges">Cancel</button>
      </div>
      <div class="control">
        <button class="button is-danger" v-if="newOrder.id != '' && user.permissions.includes('DATA_MANAGEMENT')" @click="deleteOrder">Delete</button>
      </div>
    </div>
  </form>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'OrderEdit',

  props: ['uuid'],

  components: {
  },
  
  computed: {
    ...mapGetters(['order', 'user']),
  },
  
  data () {
    return {
      newOrder: {
        id: '',
        title: '',
        description: '',
        creator: '',
        receiver: '',
        extra: {}
      },
      extraKey: '',
      extraValue: ''
    }
  },

  created () {
    if (this.uuid) {
      this.$store.dispatch('getOrder', this.uuid)
        .then(() => {
          this.newOrder = this.order;
          this.newOrder.id = this.newOrder._id;
          delete this.newOrder._id;
          delete this.newOrder.datasets;
        });
    }
  },

  methods: {
    saveExtra(event) {
      event.preventDefault();
      if (this.extraKey !== '') {
        if (this.newOrder.extra[this.extraKey] !== undefined) {
          if (this.extraValue === '') {
            this.$delete(this.newOrder.extra, this.extraKey);
          }
          else {
            this.newOrder.extra[this.extraKey] = this.extraValue;
          }
        }
        else {
          if (this.extraValue !== '') {
            this.$set(this.newOrder.extra, this.extraKey, this.extraValue);
          }
        }
      }
    },    

    cancelChanges(event) {
      event.preventDefault();
      if (this.newOrder.id === -1) {
        this.$router.push("/order/browser");
      }
      else {
        this.$router.push("/order/" + this.newOrder.id + "/about");
      }
    },

    deleteOrder(event) {
      event.preventDefault();
      this.$store.dispatch('deleteOrder', this.newOrder.id)
        .then(() => {
          this.$router.push("/order/browser");
        });
    },

    submitOrderForm(event) {
      event.preventDefault();
      this.$store.dispatch('saveOrder', this.newOrder)
        .then((response) => {
          // add performed
          let id = -1;
          if (response.data) {
            id = response.data._id;
          }
          else {
            id = this.$props.uuid;
          }
          this.$router.push("/order/" + id + "/about");
        });
    },
  },
}
</script>

<style scoped>
.order-title {
    font-weight: bold;
    font-size: 2em;
    text-align: center;
    margin: 0em 0em 0.4em 0em;
}

.field-label {
    font-weight: bold;
}

.field {
    margin: 0.4em 0em;
}

.warning {
    font-weight: bold;
    text-align: center;
    font-size: large;
}
</style>
