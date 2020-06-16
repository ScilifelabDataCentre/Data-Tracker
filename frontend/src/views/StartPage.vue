<template>
<div class="start-page">
  <section class="section">
    <h1 class="title is-1">SciLifeLab Data Tracker</h1>
    Welcome to the SciLifeLab Data Tracker, a system for tracking datasets generated at SciLifeLab.
  </section>
  <section class="section">
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
          <div class="fade-helper"></div>
        </div>
      </div>
    </div>
    </section>
    <section class="section">
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
          <div class="fade-helper"></div>
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
  height: 15em;
  position: relative;
  overflow: hidden;
  margin-bottom: 0.5em;
}

.browser-entry .fade-helper { 
  position: absolute;
  bottom: 0; 
  left: 0;
  width: 100%; 
  margin: 0;
  padding: 1.5em 0;
  background-image: linear-gradient(to bottom, transparent, white);
}
</style>
