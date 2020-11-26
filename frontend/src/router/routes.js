import MainLayout from 'layouts/MainLayout.vue'

const Index = () => import(/* webpackChunkName: "base" */ 'pages/Index.vue')
const About = () => import(/* webpackChunkName: "base" */ 'pages/About.vue')
const UserGuide = () => import(/* webpackChunkName: "base" */ 'pages/UserGuide.vue')
const Login = () => import(/* webpackChunkName: "base" */ 'pages/Login.vue')
const CurrentUser = () => import(/* webpackChunkName: "base" */ 'pages/CurrentUser.vue')

const CollectionInfo = () => import(/* webpackChunkName: "data" */ 'pages/CollectionInfo.vue')
const DatasetInfo = () => import(/* webpackChunkName: "data" */ 'pages/DatasetInfo.vue')
const OrderInfo = () => import(/* webpackChunkName: "data" */ 'pages/OrderInfo.vue')
const EntryBrowser = () => import(/* webpackChunkName: "data" */ 'pages/EntryBrowser.vue')

const UserManager = () => import(/* webpackChunkName: "admin" */ 'pages/UserManager.vue')

const routes = [
  {
    path: '/',
    component:  MainLayout,
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
    component:  MainLayout,
    children: [
      {
        path: '',
        component: EntryBrowser,
        name: 'Dataset Browser',
        props: { 'entryType': 'dataset'}
      },
      {
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        component: DatasetInfo,
        props: true,
        name: 'Dataset About'
      },
      {
        path: 'new',
        component: DatasetInfo,
        props: {'uuid': ''},
        name: 'Dataset New'
      },
    ]
  },

  {
    path: '/me',
    component:  MainLayout,
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
    component:  MainLayout,
    meta: {
      'permissionRequired': ['ORDERS'],
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
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        component: OrderInfo,
        props: true,
        name: 'Order About'
      },
      {
        path: 'new',
        component: OrderInfo,
        props: {'uuid': ''},
        name: 'Order New'
      },
    ]
  },

  {
    path: '/collections',
    component:  MainLayout,
    children: [
      {
        path: '',
        component: EntryBrowser,
        name: 'Collection Browser',
        props: { 'entryType': 'collection'}
      },
      {
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        component: CollectionInfo,
        props: true,
        name: 'Collection About'
      },
      {
        path: 'new',
        component: CollectionInfo,
        props: {'uuid': ''},
        name: 'Collection New'
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
    path: '*',
    component: () => import('pages/Error404.vue'),
  }
]

export default routes
