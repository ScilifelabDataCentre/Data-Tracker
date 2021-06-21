<template>
<q-list>
  <q-item-label header> Data </q-item-label>

  <NavEntry v-if="currentUser.permissions.includes('DATA_EDIT')"
            v-bind="orderLink" />

  <NavEntry v-for="link in dataLinks"
            :key="link.title"
            v-bind="link" />

  <div v-if="currentUser.permissions.includes('USER_MANAGEMENT')">
    <q-item-label header> Admin </q-item-label>
    <NavEntry v-bind="adminUserLink" />
  </div>

  <div>
    <q-item-label header> Other </q-item-label>
    <NavEntry v-for="link in otherLinks"
              :key="link.title"
              v-bind="link"/>
  </div>

  <q-item-label header> User </q-item-label>
  <div v-if="currentUser.name !== ''">
    <NavEntry v-for="link in userLinks"
              :key="link.title"
              v-bind="link" />
    <q-item clickable
            tag="a"
            @click="logOut">
      <q-item-section v-if="logoutLink.icon"
                      avatar>
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
    <NavEntry v-for="link in loginLinks"
              :key="link.title"
              v-bind="link" />
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

      dataLinks: [
        {
          title: 'Datasets',
          caption: 'Data deliveries',
          icon: 'fas fa-chart-area',
          link:  { 'name': 'Dataset Browser'}
        },
        {
          title: 'Collections',
          caption: 'Collections of datasets',
          icon: 'fas fa-layer-group',
          link:  { 'name': 'Collection Browser'}
        }
      ],
      
      userLinks: [
        {
          title: 'Current User',
          caption: 'About the current user',
          icon: 'person',
          link: { 'name': 'About Current User'}
        },
      ],
      
      logoutLink: {
        title: 'Log Out',
        caption: 'Log out the current user',
        icon: 'exit_to_app',
        link: '/api/v1/logout/'
      },

      loginLinks: [
        {
          title: 'Login',
          caption: 'Log in using OpenID or API Key',
          icon: 'login',
          link: { 'name': 'Login'}
        },
      ],

      otherLinks: [
        {
          title: 'About',
          caption: 'About the Data Tracker',
          icon: 'info',
          link:  { 'name': 'About'}
        },
        {
          title: 'User guide',
          caption: 'How to use the Data Tracker',
          icon: 'fas fa-map-signs',
          link:  { 'name': 'User Guide'}
        }
      ]
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
