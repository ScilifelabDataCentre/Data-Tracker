<template>
<q-drawer
  v-model="drawerOpen"
  show-if-above
  bordered
  content-class="bg-grey-1"
  >
  
  <q-list>
    <q-item-label
      header
      class="text-grey-8"
      >
      Data Types
    </q-item-label>
    
    <!-- Show only if permitted -->
    <NavEntry
      v-if="currentUser.permissions.includes('ORDERS_SELF')"
      v-bind="orderLink"
      />
    
    <NavEntry
      v-for="link in dataLinks"
      :key="link.title"
      v-bind="link"
      />
    
    <div v-if="currentUser.permissions.includes('USER_MANAGEMENT')">
      <q-item-label
        header
        class="text-grey-8"
        >
        User Admin
      </q-item-label>
      
      <NavEntry
        v-bind="adminUserLink"
        />
    </div>
    <div
      v-if="currentUser.name !== ''"
      >
      <q-item-label
        header
        class="text-grey-8"
        >
        Current User
      </q-item-label>
      
      <NavEntry
        v-for="link in userLinks"
        :key="link.title"
        v-bind="link"
        />
      <q-item
        clickable
        tag="a"
        :href="logoutLink.link"
        >
        <q-item-section
          v-if="logoutLink.icon"
          avatar
          >
          <q-icon :name="logoutLink.icon" />
        </q-item-section>
        
        <q-item-section>
          <q-item-label>{{ logoutLink.title }}</q-item-label>
          <q-item-label caption>
            {{ logoutLink.caption }}
          </q-item-label>
    </q-item-section>
  </q-item>

    </div>
    <div
      v-else
      >
      <q-item-label
        header
        class="text-grey-8"
        >
        Current User
      </q-item-label>
      
      <NavEntry
        v-for="link in loginLinks"
        :key="link.title"
        v-bind="link"
        />
    </div>
  </q-list>
</q-drawer>
</template>

<script>
import NavEntry from 'components/NavEntry.vue'

export default {
  name: 'MainDrawer',

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
        caption: 'Order management',
        icon: 'assignment',
        link: '/orders'
      },

      adminUserLink: {
        title: 'Users',
        caption: 'User administration',
        icon: 'people',
        link: '/admin/users/'
      },

      dataLinks: [
        {
          title: 'Datasets',
          caption: 'Data deliveries',
          icon: 'memory',
          link: '/datasets'
        },
        {
          title: 'Collections',
          caption: 'Collections of datasets',
          icon: 'local_library',
          link: '/collections'
        }
      ],
      
      userLinks: [
        {
          title: 'Current User',
          caption: 'About the current user',
          icon: 'person',
          link: '/user/about'
        },
      ],
      
      logoutLink: {
        title: 'Log Out',
        caption: 'Log out the current user',
        icon: 'exit_to_app',
        link: '/api/logout/'
      },

      loginLinks: [
        {
          title: 'Log In',
          caption: 'Log in',
          icon: 'login',
          link: '/login'
        },
      ],

      otherLinks: [
        {
          title: 'About',
          caption: 'Information about the system',
          icon: 'info',
          link: '/about'
        },
      ]
    }
  },

  props: {
    drawerOpen: {
      type: Boolean,
      default: true
    }
  }
}
</script>
