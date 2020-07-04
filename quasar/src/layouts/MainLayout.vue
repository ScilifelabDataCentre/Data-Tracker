<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />

        <q-toolbar-title>
	  Data Tracker
        </q-toolbar-title>

        <div>Quasar v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <MainDrawer :drawerOpen="leftDrawerOpen"/>
    
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import MainDrawer from 'components/MainDrawer.vue'

export default {
  name: 'MainLayout',

  components: {
    MainDrawer
  },

  data () {
    return {
      leftDrawerOpen: false,
    }
  },

  created () {
    this.$store.dispatch('currentUser/getInfo');
  }
}
</script>
