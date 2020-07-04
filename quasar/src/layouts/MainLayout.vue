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
          <q-btn
            flat
            dense
            no-caps
            no-wrap
            to="/"
            >
            Data Tracker
          </q-btn>
        </q-toolbar-title>
        <q-btn
          dense
          flat
          no-wrap
          no-caps
          label="SciLifeLab Data Centre"
          class="q-ml-sm pull-right"
          />
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
import MainDrawerContent from 'components/MainDrawerContent.vue'

export default {
  name: 'MainLayout',

  components: {
    MainDrawerContent
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
