<template>
<div class="dataset-info">
  <div v-if="Object.keys(dataset).length > 0">
    <h1 class="title is-2">{{ dataset.title }}</h1>
    <div class="dataset-description field" v-html="dataset.description"></div>
    <div class="message">
      <div class="message-header">
        Data access
      </div>
      <ul v-for="location in dataset.links" :key="location.id">
        <li class="test"><a :href="location.url">{{location.description}}</a></li>
      </ul>
    </div>
    <span class="timestamp">Last update: {{ dataset.timestamp }}</span>
  </div>
  <button class="button is-link" @click="editDataset">
    Edit
  </button>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'DatasetAbout',
  props: ['uuid'],
  components: {
  },
  computed: {
    ...mapGetters(['dataset']),
  },
  data () {
    return {
    }
  },
  created () {
    this.$store.dispatch('getDataset', this.uuid);
  },
  methods: {
    editDataset(event) {
      event.preventDefault();
      this.$router.push("/dataset/" + this.$props.uuid + "/edit");
    },
  },
}
</script>

<style scoped>
.dataset-title {
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
