<template>
<div class="start-page">
  <h1 class="title is-1">SciLifeLab Data Tracker</h1>
    <section id="introduction" class="section">
      Welcome to the SciLifeLab Data Tracker, a system for tracking datasets generated at SciLifeLab.
  </section>
  <section id="random-dataset" class="section">
    <div v-if="random_ds !== undefined">
      <div>
        <h2 class="title is-3">Random Dataset</h2>
        <div class="browser-entry card">
          <div class="card-content">
            <p class="has-text-weight-bold">
              <router-link :to="'/dataset/' + random_ds._id"> {{ random_ds.title }}</router-link>
            </p>
            <p class="has-text-weight-semibold">
              Creator: {{ random_ds.creator }}
            </p>
            <vue-simple-markdown :source="random_ds.description"></vue-simple-markdown>
          </div>
        </div>
      </div>
    </div>
    </section>
    <section id="random-project" class="section">
    <div v-if="random_proj !== undefined">
      <div>
        <h2 class="title is-3">Random Project</h2>
        <div class="browser-entry card">
          <div class="card-content">
            <p class="has-text-weight-bold">
              <router-link :to="'/project/' + random_proj._id"> {{ random_proj.title }}</router-link>
            </p>
            <p class="has-text-weight-bold">
              Contact: {{ random_proj.contact }}
            </p>
              <vue-simple-markdown :source="random_proj.description"></vue-simple-markdown>
          </div>
        </div>
      </div>
    </div>
  </section>
</div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'StartPage',

  data () {
    return {
      random_ds: undefined,
      random_proj: undefined,
    }
  },

  mounted () {
    axios
      .get('/api/dataset/random/')
      .then((response) => {
        this.random_ds = response.data.datasets[0];
      });
    axios
      .get('/api/project/random/')
      .then((response) => {
        this.random_proj = response.data.projects[0];
      });

  },
}
</script>

<style scoped>
.browser-entry {
  max-height: 15em;
  position: relative;
  overflow: hidden;
  text-overflow: ellipsis;
}

.browser-entry:after {
  content: "";
  position: absolute;
  top: 13em;
  left: 0;
  height: 2em;
  width: 100%; 
  background: linear-gradient(rgba(255,255,255,0), #FFF);
}
</style>
