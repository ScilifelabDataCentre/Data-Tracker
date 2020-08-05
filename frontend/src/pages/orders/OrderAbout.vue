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
      <q-list dense>
        <ListHeader title="Authors"
                    explanation="The ones who provided the sample, e.g. a researcher" />
        <UserEntry v-for="author in order.authors"
                   :key="author._id"
                   :entry="author" />

        <q-item-label header>
          <span>
            Generators
            <q-tooltip>
              The ones who generated the data, e.g. a facility
            </q-tooltip>
          </span>
        </q-item-label>
        <UserEntry v-for="generator in order.generators"
                   :key="generator._id"
                   :entry="generator" />

        <ListHeader title="Organisation"
                    explanation="The data owner, e.g. a university" />
        <q-item>
          <q-item-section avatar>
            <q-btn v-if="order.organisation.email.length > 0"
                   flat
                   round
                   dense
                   icon="email"
                   type="a"
                   :href="'mailto:' + order.organisation.email" />
          </q-item-section>
          <q-item-section>
            <q-item-label>
              {{ order.organisation.name }}
            </q-item-label>
            <q-item-label caption>
              {{ order.organisation.email }}
            </q-item-label>
          </q-item-section>
        </q-item>

        <ListHeader title="Editors"
                    explanation="Users that may edit this order" />
        <UserEntry v-for="editor in order.editors"
                   :key="editor._id"
                   :entry="editor" />

        <ListHeader title="Receivers"
                    explanation="Users that may connect datasets from this order to collections" />
        <UserEntry v-for="receiver in order.receivers"
                   :key="receiver._id"
                   :entry="receiver" />
      </q-list>
    </q-card-section>

    <q-card-section>
      <q-list dense>
        <ListHeader title="Datasets"
                    explanation="Datasets generated from this order" />
        <q-item v-for="dataset in order.datasets" :key="dataset._id">
          <q-item-section avatar>
            <q-btn 
              flat
              dense
              round
              icon="link"
              :to="{ 'name': 'Dataset About', 'params': { 'uuid': dataset._id } }" />
          </q-item-section>
          <q-item-section>
            <q-item-label>
              {{ dataset.title }}
            </q-item-label>
            <q-item-label caption>
              {{ dataset._id }}
            </q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
      
      <q-field
        v-for="field in Object.keys(order.tagsUser)" :key="field"
        :label="field"
        stack-label>
        <template v-slot:prepend>
          <q-icon name="label" />
        </template>
        <template v-slot:control>
          <span>
            {{ order.userTags[field] }}
          </span>
        </template>
      </q-field>
    </q-card-section>
  </q-card>

  <q-page-sticky position="top-right"
		 :offset="[18, 18]">
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
import UserEntry from 'components/UserEntry.vue'
import ListHeader from 'components/ListHeader.vue'

export default {
  name: 'OrderAbout',

  components: {
    UserEntry,
    ListHeader
  },
  
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
