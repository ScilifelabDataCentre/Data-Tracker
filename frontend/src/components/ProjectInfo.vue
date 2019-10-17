<template>
<div class="project-info">
  <div class="warning" v-if="projectInfo == null">
    <span>Unable to retrieve project</span>
  </div>
  <div v-if="projectInfo != null">
    <h1>{{ projectInfo.title }}</h1>
    <p class="description">{{ projectInfo.description }}</p>
    <p class="doi"><span class="field-header">DOI: </span>{{ projectInfo.doi }}</p>
    <p class="owners">
      <span class="field-header">Owners: </span>
      <div class="owner" v-for="owner in projectInfo.owners" :key="owner.name">
        {{ owner.name }}
      </div>
    <p class="creator"><span class="field-header">Data creator: </span>{{ projectInfo.creator }}</p>
    <p class="tags">
      <span class="field-header">Tags: </span>
      <tag-entry v-for="tag in projectInfo.tags" :key="tag.id" :tagData="tag"></tag-entry>
    </p>
    <p class="dmp">
      <span class="field-header">Data management plan: </span>{{ projectInfo.dmp }}
    </p>
    <p class="publications">
      <span class="field-header">Publications: </span>
    </p>
    <p>
      <span class="field-header">Data access URLs: </span>
      <url-entry v-for="url in projectInfo.dataUrls" :key="url.id" :urlData="url"></url-entry>
    </p>
  </div>
</div>
</template>

<script>
import axios from 'axios';

import ProjectInfoTag from './ProjectInfoTag.vue';
import ProjectInfoUrl from './ProjectInfoUrl.vue';

export default {
  name: 'ProjectInfo',
  props: ['id'],
  components: {

    'tag-entry': ProjectInfoTag,
    'url-entry': ProjectInfoUrl,
  },
  data () {
    return {
      projectInfo: null,
      errorCode: null,
      errorText: null
    }
  },
  created () {
    axios
      .get('http://localhost:5000/api/dataset/' + this.id)
      .then((response) => (this.projectInfo = response.data))
      .catch(function (err) {this.errorCode = err.status;
                             this.errorText = err.statusText});
  }

}
</script>

<style scoped>
h1 {
    text-align: center;
}

.project-info {
    text-align: left;
}

.field-header {
    font-weight: bold;
}

.warning {
    font-weight: bold;
    text-align: center;
    font-size: large;
}
</style>
