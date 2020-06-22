<template>
<div class="order-info">
  <h1 class="title is-2">{{ order.title }}</h1>
  <section class="section">
    <div class="content">
      <vue-simple-markdown :source="order.description"></vue-simple-markdown>
    </div>
  </section>
  <section class="section">
    <table class="info-list table is-hoverable is-striped">
      <tbody>
	<tr>
          <th scope="row">Creator</th>
          <td>{{order.creator.name}} <span v-if="order.creator.identifier !== order.creator.name">({{order.creator.identifier}})</span></td>
          <td></td>
	</tr>
	<tr>
          <th scope="row">Receiver</th>
          <td>{{order.receiver}}</td>
          <td></td>
	</tr>
	<tr>
          <th scope="row">Datasets</th>
          <td>
            <ul>
              <li v-for="dataset in order.datasets" :key="dataset._id">
		<router-link :to="'/dataset/' + dataset._id">{{dataset.title}}</router-link>
              </li>
            </ul>
          </td>
          <td>
            <button class="button is-link" @click="addDataset">Add</button>
          </td>
	</tr>
	<tr v-for="field in Object.keys(order.extra)" :key="field">
          <th scope="row">{{ capitalize(field) }}</th>
          <td>{{ order.extra[field] }}</td>
          <td></td>
	</tr>
      </tbody>
    </table>
  </section>
  
  <div class="field is-grouped">
    <div class="control">
      <router-link to="edit">
        <button class="button is-link">
          Edit
        </button>
      </router-link>
    </div>
    <div class="control">
      <router-link to="log">
        <button class="button is-light">
          Logs
        </button>
      </router-link>
    </div>
  </div>
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

  methods: {
    addDataset(event) {
      event.preventDefault();
      this.$store.dispatch('addDataset', {'data': {'title': this.order.title + ' dataset ' + (this.order.datasets.length + 1)},
                                          'uuid': this.uuid})
        .then(() => {
          this.$store.dispatch('getOrder', this.uuid);
        });
    },

    capitalize (text) {
      return text.charAt(0).toUpperCase() + text.slice(1);
    }

  },
}
</script>

<style scoped>
.info-list th {
  text-align: right;
}
</style>
