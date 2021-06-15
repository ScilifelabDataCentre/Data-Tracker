<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn flat
               dense
               round
               icon="menu"
               aria-label="Menu"
               @click="leftDrawerOpen = !leftDrawerOpen" />
        <q-toolbar-title>
          Data Tracker
        </q-toolbar-title>
        <q-space />
        <q-btn dense
               flat
               no-wrap
               class="q-ml-sm pull-right"
               type="a"
               target="_blank"
               rel="noopener"
               href="https://www.scilifelab.se/data/">
          <q-avatar square
                    size="2em">
            <img :src="require('../assets/scilifelab_symbol_white.svg')"
                 alt="SciLifeLab logo"/>
          </q-avatar>
        </q-btn>
      </q-toolbar>
      <q-toolbar inset>
        <q-breadcrumbs active-color="white" style="font-size: 16px">
          <q-breadcrumbs-el icon="home" :to="{ 'name': 'Home' }"/>
          <q-breadcrumbs-el v-for="(part, i) in breadcrumbs"
                            :key="part"
                            :label="part"
                            :to="'/' + breadcrumbs.slice(0, i+1).join('/')"/>
        </q-breadcrumbs>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      content-class="bg-grey-1"
      >
      <MainDrawerContent />
    </q-drawer>
    
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { openURL } from 'quasar'

import MainDrawerContent from 'components/MainDrawerContent.vue'

export default {
  name: 'MainLayout',

  components: {
    MainDrawerContent
  },

  watch: {
    '$route' () {
      let splitPath = this.$route.path.split('/').slice(1);
      if (splitPath[0]) this.breadcrumbs = splitPath; else this.breadcrumbs = [];
    }
  },
  
  data () {
    return {
      leftDrawerOpen: false,
      breadcrumbs: [],
    }
  },

  mounted () {
    let splitPath = this.$route.path.split('/').slice(1);
    if (splitPath[0]) this.breadcrumbs = splitPath; else this.breadcrumbs = [];
  },
  
  created () {
    this.$store.dispatch('currentUser/getInfo');
  },

  methods: {
    onClick: function (link) {
      openURL(link)
    }
  },
}
</script>
