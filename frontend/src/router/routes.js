const MainLayout = () => import(/* webpackChunkName: "base" */ 'layouts/MainLayout.vue')
const Index = () => import(/* webpackChunkName: "base" */ 'pages/Index.vue')
const About = () => import(/* webpackChunkName: "base" */ 'pages/About.vue')
const UserGuide = () => import(/* webpackChunkName: "base" */ 'pages/UserGuide.vue')
const Login = () => import(/* webpackChunkName: "base" */ 'pages/Login.vue')

const CurrentUser = () => import(/* webpackChunkName: "user" */ 'pages/CurrentUser.vue')

const Page404 = () => import(/* webpackChunkName: "errors" */ 'pages/Error404.vue')
const NonAuth = () => import(/* webpackChunkName: "errors" */ 'pages/NonAuth.vue')
const NoBackend = () => import(/* webpackChunkName: "errors" */ 'pages/NoBackend.vue')

const EntryInfo = () => import(/* webpackChunkName: "data" */ 'pages/EntryInfo.vue')
const EntryBrowser = () => import(/* webpackChunkName: "data" */ 'pages/EntryBrowser.vue')

const UserManager = () => import(/* webpackChunkName: "admin" */ 'pages/UserManager.vue')

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', component: Index, name: 'Home' },
      { path: 'about', component: About, name: 'About' },
      { path: 'guide', component: UserGuide, name: 'User Guide' },
      {
        path: 'login',
        component: Login,
        name: 'Login',
        props: true
      },

    ]
  },

    {
    path: '/collections',
    component: MainLayout,
    children: [
      {
        path: '',
        component: EntryBrowser,
        name: 'Collection Browser',
        props: { 'dataType': 'collection'}
      },
      {
        path: 'add',
        meta: {
          'permissionRequired': ['DATA_EDIT'],
          'loginRequired': true,
        },
        component: EntryInfo,
        props: {'uuid': '', dataType: 'collection', newEntry: true},
        name: 'Collection New'
      },
      {
        path: ':uuid',
        component: EntryInfo,
        props: route => ({'uuid': route.params.uuid, 'dataType': 'collection'}),
        name: 'Collection About'
      },
    ]
  },

  {
    path: '/datasets',
    component: MainLayout,
    children: [
      {
        path: '',
        component: EntryBrowser,
        name: 'Dataset Browser',
        props: { 'dataType': 'dataset'}
      },
      {
        path: 'add',
        meta: {
          'permissionRequired': ['DATA_EDIT'],
          'loginRequired': true,
        },
        component: EntryInfo,
        props: {'uuid': '', dataType: 'dataset', newEntry: true},
        name: 'Dataset New'
      },
      {
        path: ':uuid',
        component: EntryInfo,
        props: route => ({'uuid': route.params.uuid, 'dataType': 'dataset'}),
        name: 'Dataset About'
      },
    ]
  },

    {
    path: '/orders',
    component: MainLayout,
    meta: {
      'permissionRequired': ['DATA_EDIT'],
      'loginRequired': true,
    },
    children: [
      {
        path: '',
        component: EntryBrowser,
        name: 'Order Browser',
        props: { 'dataType': 'order'}
      },
      {
        path: 'add',
        meta: {
          'permissionRequired': ['DATA_EDIT'],
          'loginRequired': true,
        },
        component: EntryInfo,
        props: {'uuid': '', dataType: 'order', newEntry: true},
        name: 'Order New'
      },
      {
        path: ':uuid',
        component: EntryInfo,
        props: route => ({'uuid': route.params.uuid, 'dataType': 'order'}),
        name: 'Order About'
      },

    ]
  },

  {
    path: '/account',
    component: MainLayout,
    meta: {
      'loginRequired': true,
    },
    children: [
      {
        path: '',
        component: CurrentUser,
        name: 'About Current User',
      },
    ]
  },

  {
    path: '/admin',
    component: MainLayout,
    children: [
      {
        path: 'user',
        component: UserManager,
        meta: {
          'permissionRequired': ['USER_MANAGEMENT'],
          'loginRequired': true,
        },
        name: 'User Manager',
      },
    ]
  },

  {
    path: '/forbidden',
    component: MainLayout,
    children: [
      { path: '', component: NonAuth, name: 'Forbidden' }
    ]
  },

  {
    path: '/error',
    component: MainLayout,
    children: [
      { path: '', component: NoBackend, name: 'No Backend' }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: Page404,
  }
]

export default routes
