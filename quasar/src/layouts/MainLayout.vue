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

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      content-class="bg-grey-1"
      >

      <q-list>
        <q-item-label
          header
          class="text-grey-8"
        >
          Data types
        </q-item-label>

        <!-- Show only if permitted -->
        <NavEntry
          v-if="true"
          v-bind="orderLink"
        />

        <NavEntry
          v-for="link in dataLinks"
          :key="link.title"
          v-bind="link"
        />

        <div v-if="true">
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
          v-if="true"
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

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import NavEntry from 'components/NavEntry.vue'

export default {
  name: 'MainLayout',

  components: {
    NavEntry
  },

  data () {
    return {
      leftDrawerOpen: false,
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
        {
          title: 'Log Out',
          caption: 'Log out the current user',
          icon: 'exit_to_app',
          link: '/api/logout/'
        },
      ],

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
  }
}
</script>
