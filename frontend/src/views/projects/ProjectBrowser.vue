<template>
<div class="project-browser">
  <h1 class="title is-2">Projects</h1>
  <router-link v-if="user.role === 'Steward' || user.role === 'Admin'" to="/project/add">
    <img class="icon-add" :src="require('../../assets/open-iconic/svg/plus.svg')" alt="Add" />
  </router-link>
  <browser-entry v-for="project in projects" :key="project.id" :entry="project" entry_type="project">
  </browser-entry>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import BrowserEntry from '../../components/BrowserEntry.vue';

export default {
  name: 'ProjectBrowser',
  data () {
    return {
    }
  },
  computed: {
    ...mapGetters(['projects', 'user']),
  },
  components: {
    'browser-entry': BrowserEntry
  },
  created () {
    this.$store.dispatch('getProjects');
  },
}
</script>

<style scoped>
.icon-add {
  width: 1.2em;
  height: 1.2em;
}
</style>
