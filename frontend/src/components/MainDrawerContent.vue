<template>
<q-list>
  <q-item-label header> Data </q-item-label>

  <NavEntry v-if="currentUser.permissions.includes('DATA_EDIT')"
            id="drawer-entry-orders"
            v-bind="orderLink" />

  <NavEntry v-bind="datasetLink"
            id="drawer-entry-datasets" />
  <NavEntry v-bind="collectionLink"
            id="drawer-entry-collections" />

  <div v-if="currentUser.permissions.includes('USER_MANAGEMENT')">
    <q-item-label header> Admin </q-item-label>
    <NavEntry v-bind="adminUserLink"
              id="drawer-entry-users" />
  </div>

  <div>
    <q-item-label header> Other </q-item-label>
    <NavEntry v-bind="aboutLink"
              id="drawer-entry-about" />
    <NavEntry v-bind="guideLink"
              id="drawer-entry-guide" />
  </div>

  <q-item-label header> User </q-item-label>
  <div v-if="currentUser.name !== ''">
    <NavEntry v-bind="currentUserLink"
              id="drawer-entry-current-user"/>
    <q-item clickable
            id="drawer-entry-log-out"
            @click="logOut">
      <q-item-section avatar>
        <q-icon :name="logoutLink.icon" />
      </q-item-section>

      <q-item-section>
        <q-item-label> {{ logoutLink.title }} </q-item-label>
        <q-item-label caption>
          {{ logoutLink.caption }}
        </q-item-label>
      </q-item-section>
    </q-item>
  </div>
  <div v-else>
    <NavEntry v-bind="loginLink"
              id="drawer-entry-log-in"/>
  </div>

</q-list>
</template>

<script>
import NavEntry from 'components/NavEntry.vue'

export default {
  name: 'MainDrawerContent',

  components: {
    NavEntry
  },

  computed: {
    currentUser: {
      get () {
        return this.$store.state.currentUser.info;
      },
      set (val) {
        this.$store.commit('currentUser/updateInfo', val)
      }
    }
  },

  data () {
    return {
      orderLink: {
        title: 'Orders',
        caption: 'Data orders',
        icon: 'assignment',
        link: { 'name': 'Order Browser'}
      },

      adminUserLink: {
        title: 'Users',
        caption: 'User administration',
        icon: 'people',
        link: { 'name': 'User Manager'}
      },

      datasetLink: {
        title: 'Datasets',
        caption: 'Data deliveries',
        icon: 'fas fa-chart-area',
        link:  { 'name': 'Dataset Browser'}
      },

      collectionLink:  {
        title: 'Collections',
        caption: 'Collections of datasets',
        icon: 'fas fa-layer-group',
        link:  { 'name': 'Collection Browser'}
      },
      
      currentUserLink: {
        title: 'Current User',
        caption: 'About the current user',
        icon: 'person',
        link: { 'name': 'About Current User'}
      },
      
      logoutLink: {
        title: 'Log Out',
        caption: 'Log out the current user',
        icon: 'exit_to_app',
        link: ''
      },

      loginLink: {
        title: 'Log In',
        caption: 'Log in using OpenID or API Key',
        icon: 'login',
        link: { 'name': 'Login'}
      },

      aboutLink: {
        title: 'About',
        caption: 'About the Data Tracker',
        icon: 'info',
        link:  { 'name': 'About'}
      },

      guideLink: {
        title: 'User Guide',
        caption: 'How to use the Data Tracker',
        icon: 'fas fa-map-signs',
        link:  { 'name': 'User Guide'}
      }
    }
  },

  props: {
    drawerOpen: {
      type: Boolean,
      default: true
    }
  },

  methods: {
    logOut () {
      this.$store.dispatch('currentUser/logOut')
        .then(() => {
          this.$router.push({ 'name': 'Home' })
          this.$store.dispatch('currentUser/getInfo');
        });
    }
  }
}
</script>
