<template>
<q-page padding>
  <div class="text-center q-mb-lg">
    <h1 class="text-h2 q-mb-xs ">{{ order.title }}</h1>
    <div class="text-subtitle1 text-italic">
      {{ order._id }}
    </div>
  </div>

  <q-card class="q-my-lg">
    <q-card-section>
      <q-markdown :src="order.description" />
    </q-card-section>
  </q-card>

  <q-card>
    <q-card-section>
      <q-field label="Creator" stack-label>
        <template v-slot:prepend>
          <q-icon name="person" />
        </template>
        <template v-slot:control>
          {{ order.creator.name }}
        </template>
      </q-field>

      <q-field label="Receiver" stack-label>
        <template v-slot:prepend>
          <q-icon name="person" />
        </template>
        <template v-slot:control>
          {{ order.receiver }}
        </template>
      </q-field>

      <q-field
        v-for="field in Object.keys(order.extra)" :key="field"
        :label="field"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="label" />
        </template>
        <template v-slot:control>
          <span>
            {{ order.extra[field] }}
          </span>
        </template>
      </q-field>

      <q-field
        v-if="order.datasets.length > 0"
        label="Datasets"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="insights" />
        </template>

        <template v-slot:control>
          <ul class="">
            <li v-for="relOrder in order.datasets" :key="relOrder._id">
              <q-btn 
                flat
                no-caps
                dense
                :label="relOrder.title"
                :to="{ 'name': 'Order About', 'params': { 'uuid': relOrder._id } }" />
            </li>
          </ul>
        </template>
      </q-field>

    </q-card-section>
  </q-card>

  <q-page-sticky position="bottom-right"
                 :offset="[24, 24]">
    <q-btn fab
           icon="edit"
           color="accent"
           :to="{ 'name': 'Order Edit', params: {'uuid': uuid} }" />
  </q-page-sticky>

  <q-inner-loading :showing="loading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>    <!-- content -->
</q-page>
</template>

<script>
export default {
  name: 'OrderAbout',

    props: {
    uuid: {
      type: String,
      required: true
    }
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
      loading: true,
    }
  },
  
  mounted () {
    this.$store.dispatch('orders/getOrder', this.uuid)
      .then(() => this.loading = false)
      .catch(() => this.loading = false)
  }

}
</script>
