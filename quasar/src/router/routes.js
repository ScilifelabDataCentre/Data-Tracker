import MainLayout from 'layouts/MainLayout.vue'

const Index = () => import(/* webpackChunkName: "base" */ 'pages/Index.vue')
const About = () => import(/* webpackChunkName: "base" */ 'pages/About.vue')

const BaseContainer = () => import(/* webpackChunkName: "base" */ 'pages/BaseContainer.vue')

const CollectionAbout = () => import(/* webpackChunkName: "collection" */ 'pages/collections/CollectionAbout.vue')
const CollectionBrowser = () => import(/* webpackChunkName: "collection" */ 'pages/collections/CollectionBrowser.vue')
const CollectionEdit = () => import(/* webpackChunkName: "collection" */ 'pages/collections/CollectionEdit.vue')

const DatasetAbout = () => import(/* webpackChunkName: "dataset" */ 'pages/datasets/DatasetAbout.vue')
const DatasetBrowser = () => import(/* webpackChunkName: "dataset" */ 'pages/datasets/DatasetBrowser.vue')
const DatasetEdit = () => import(/* webpackChunkName: "dataset" */ 'pages/datasets/DatasetEdit.vue')

const OrderAbout = () => import(/* webpackChunkName: "order" */ 'pages/orders/OrderAbout.vue')
const OrderBrowser = () => import(/* webpackChunkName: "order" */ 'pages/orders/OrderBrowser.vue')
const OrderEdit = () => import(/* webpackChunkName: "order" */ 'pages/orders/OrderEdit.vue')

const UserManager = () => import(/* webpackChunkName: "admin" */ 'pages/admin/UserManager.vue')

const routes = [
  {
    path: '/',
    component:  MainLayout,
    children: [
      { path: '', component: Index, name: 'Home'},
      { path: 'about', component: About, name: 'About' },
    ]
  },

  {
    path: '/datasets',
    component:  MainLayout,
    children: [
      {
        path: '',
        component: DatasetBrowser,
        name: 'Dataset Browser'
      },
      {
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        component: DatasetAbout,
        props: true,
        name: 'Dataset About'
      },
      {
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/edit',
        component: DatasetEdit,
        props: true,
        name: 'Dataset Edit'
      },
    ]
  },
  
  {
    path: '/orders',
    component:  MainLayout,
    meta: {
      'accessReq': ['ordersSelf'],
    },
    children: [
      {
        path: '',
        component: OrderBrowser,
        name: 'Order Browser'
      },
      {
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        component: OrderAbout,
        props: true,
        name: 'Order About'
      },
      {
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/edit',
        component: OrderEdit,
        props: true,
        name: 'Order Edit'
      },
      {
        path: 'add',
        component: OrderEdit,
        props: { 'uuid': '' },
        name: 'Order Add'
      },
    ]
  },

  {
    path: '/collections',
    component:  MainLayout,
    children: [
      {
        path: '',
        component: CollectionBrowser,
        name: 'Collection Browser'
      },
      {
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
        component: CollectionAbout,
        props: true,
        name: 'Collection About'
      },
      {
        path: ':uuid([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/edit',
        component: CollectionEdit,
        props: true,
        name: 'Collection Edit'
      },
      {
        path: 'add',
        component: CollectionEdit,
        props: { 'uuid': '' },
        name: 'Collection Add'
      },
    ]
  },

  {
    path: '/admin',
    component: MainLayout,
    children: [
      {
        path: 'user',
        component: BaseContainer,
        name: 'Admin User Manager',
        meta: {
          'accessReq': ['userManagement'],
        },
        children: [
          {
            path: '',
            component: UserManager,
            name: 'Admin User Manager',
          },
          {
            path: 'add',
            component: UserManager,
            props: { 'uuid': '' },
            name: 'Admin User Add'
          },
          {
            path: ':uuid/edit',
            component: UserManager,
            props: true,
            name: 'Admin User Edit'
          },
        ]
      },
    ]
  },

  {
    path: '*',
    component: () => import('pages/Error404.vue'),
  }
]

export default routes
