<template>
<div class="dataset-info">
  <h1 class="title is-2">Changelog for {{ capitalize(dType) }} Entry</h1>
  <div v-if="logs.length === 0">
    No logs found.
  </div>
  <div v-else class="content">
    <ol>
      <li v-for="log in logs" :key="log._id">
        <ul>
          <li><span class="field-title">Id:</span> {{ log._id }}</li>
          <li><span class="field-title">Action:</span> {{ log.action }}</li>
          <li><span class="field-title">Comment:</span> {{ log.comment }}</li>
          <li><span class="field-title">Data Type:</span> {{ log.dataType }}</li>
          <li><span class="field-title">Time:</span> {{ log.timestamp }}</li>
        </ul>
      </li>
    </ol>
  </div>
</div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'LogViewer',
  props: ['dataType'],
  data () {
    return {
      logs: [],
      uuid: '',
      dType: '',
    }
  },
  mounted () {
    if (this.dataType === 'me') {
      this.uuid = 'me';
      this.dType = 'user';
    }
    else {
      this.uuid = this.$route.params.uuid;
      this.dType = this.dataType;
    }
    axios
      .get('/api/' + this.dType + '/' + this.uuid + '/actions/')
      .then((response) => {
        this.logs = response.data.logs;
      });
  },

  methods: {
    capitalize (text) {
      return text.charAt(0).toUpperCase() + text.slice(1);
    }
  }
}
</script>

<style scoped>
.field-title {
    font-weight: bold;
}
</style>
