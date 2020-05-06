<template>
<div class="order-info">
  <h1 class="title is-2">{{ order.title }}</h1>
  <div class="order-description field" v-html="order.description"></div>
  <table class="table is-hoverable">
    <tbody>
      <tr>
        <th scope="row">Creator</th>
        <td>{{order.creator}}</td>
      </tr>
      <tr>
        <th scope="row">Receiver</th>
        <td>{{order.receiver}}</td>
      </tr>
      <tr v-if="order.datasets.length > 0">
        <th scope="row" :rowspan="order.datasets.length">Datasets</th>
        <td>
          <ul>
            <li v-for="dataset in order.datasets" :key="dataset._id">
              <router-link :to="'/dataset/' + dataset._id">{{dataset.title}}</router-link>
            </li>
          </ul>
        </td>
      </tr>
      <tr v-for="field in Object.keys(order.extra)" :key="field">
        <th scope="row">{{ field }}</th>
        <td>{{ order.extra[field] }}</td>
      </tr>
    </tbody>
  </table>
  <router-link :to="'/order/' + uuid + '/edit'">
    <button class="button is-link">
      Edit
    </button>
  </router-link>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'OrderAbout',
  props: ['uuid'],
  components: {
  },
  computed: {
    ...mapGetters(['order']),
  },
  data () {
    return {
    }
  },
  created () {
    this.$store.dispatch('getOrder', this.uuid);
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

.data-header {
    text-align: right;
    font-weight: bold;
}

.field-header.td {
    font-weight: bold;
}

.field {
    margin: 0.4em 0em;
}

.table td {
    border: 0px;
}
.warning {
    font-weight: bold;
    text-align: center;
    font-size: large;
}
.timestamp {
    font-style: italic;
    font-size: 1em;
}
</style>
