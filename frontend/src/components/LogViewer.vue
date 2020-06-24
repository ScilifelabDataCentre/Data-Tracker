<template>
<div class="dataset-info">
  <h1 class="title is-2">Changelog for {{ dType | capitalize }} Entry</h1>
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
          <li><span class="field-title">User:</span> {{ log.user }}</li>
          <li><span class="field-title">Time:</span> {{ log.timestamp }}</li>
          <li><span class="field-title">Change:</span>
            <ul>
              <li v-for="field in Object.keys(log.data)" :key="field">
                <span class="field-title">{{ field }}:</span> {{ log.data[field] }}
              </li>
            </ul>
          </li>
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
      loaded: false,
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
      .get('/api/' + this.dType + '/' + this.uuid + '/log/')
      .then((response) => {
        this.logs = response.data.logs;
      });
  },
}
</script>
