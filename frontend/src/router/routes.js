import MainLayout from 'layouts/MainLayout.vue'

const Index = () => import(/* webpackChunkName: "base" */ 'pages/Index.vue')
const About = () => import(/* webpackChunkName: "base" */ 'pages/About.vue')
const UserGuide = () => import(/* webpackChunkName: "base" */ 'pages/UserGuide.vue')
const Login = () => import(/* webpackChunkName: "base" */ 'pages/Login.vue')
const CurrentUser = () => import(/* webpackChunkName: "base" */ 'pages/CurrentUser.vue')

const Page404 = () => import(/* webpackChunkName: "errors" */ 'pages/Error404.vue')
const NonAuth = () => import(/* webpackChunkName: "errors" */ 'pages/NonAuth.vue')
const NoBackend = () => import(/* webpackChunkName: "errors" */ 'pages/NoBackend.vue')

const CollectionInfo = () => import(/* webpackChunkName: "data" */ 'pages/CollectionInfo.vue')
const DatasetInfo = () => import(/* webpackChunkName: "data" */ 'pages/DatasetInfo.vue')
const OrderInfo = () => import(/* webpackChunkName: "data" */ 'pages/OrderInfo.vue')
const EntryBrowser = () => import(/* webpackChunkName: "data" */ 'pages/EntryBrowser.vue')

const UserManager = () => import(/* webpackChunkName: "admin" */ 'pages/UserManager.vue')

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', component: Index, name: 'Home'},
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
    path: '/datasets',
    component: MainLayout,
    children: [
      {
        path: '',
        component: EntryBrowser,
        name: 'Dataset Browser',
        props: { 'entryType': 'dataset'}
      },
      {
        path: 'new',
        meta: {
          'permissionRequired': ['DATA_EDIT'],
          'loginRequired': true,
        },
        component: DatasetInfo,
        props: {'uuid': ''},
        name: 'Dataset New'
      },
      {
        path: ':uuid',
        component: DatasetInfo,
        props: true,
        name: 'Dataset About'
      },
    ]
  },

  {
    path: '/me',
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
        props: { 'entryType': 'order'}
      },
      {
        path: 'new',
        meta: {
          'permissionRequired': ['DATA_EDIT'],
          'loginRequired': true,
        },
        component: OrderInfo,
        props: {'uuid': ''},
        name: 'Order New'
      },
      {
        path: ':uuid',
        component: OrderInfo,
        props: true,
        name: 'Order About'
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
        props: { 'entryType': 'collection'}
      },
      {
        path: 'new',
        meta: {
          'permissionRequired': ['DATA_EDIT'],
          'loginRequired': true,
        },
        component: CollectionInfo,
        props: {'uuid': ''},
        name: 'Collection New'
      },
      {
        path: ':uuid',
        component: CollectionInfo,
        props: true,
        name: 'Collection About'
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

  {
    path: '*',
    component: MainLayout,
    children: [
      { path: '', component: Page404, name: '404' }
    ]
  }
]

export default routes
