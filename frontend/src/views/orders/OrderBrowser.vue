<template>
<div class="dataset-browser">
  <h1 class="title is-1">Orders</h1>
  <router-link class="button is-link" to="add">
    Add
  </router-link>
  <browser-entry v-for="order in orders" :key="order._id" :entry="order" entry_type="order">
  </browser-entry>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import BrowserEntry from '../../components/BrowserEntry.vue';

export default {
  name: 'OrderBrowser',
  data () {
    return {
    }
  },
  computed: {
    ...mapGetters(['orders', 'user']),
  },
  components: {
    'browser-entry': BrowserEntry
  },
  created () {
    this.$store.dispatch('getOrders');
  },
}
</script>
