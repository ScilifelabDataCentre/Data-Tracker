<template>
<div class="dataset-browser">
  <h1 class="title is-1">Orders</h1>
  <router-link v-if="user.permissions.includes('OWNERS_SELF') || user.permissions.includes('DATA_MANAGEMENT')" to="/order/add">
    <img class="icon-add" :src="require('../../assets/open-iconic/svg/plus.svg')" alt="Add" />
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

<style scoped>
.icon-add {
  width: 1.2em;
  height: 1.2em;
}
</style>
