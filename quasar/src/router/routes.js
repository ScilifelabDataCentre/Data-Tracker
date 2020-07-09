import MainLayout from 'layouts/MainLayout.vue'

const Index = () => import(/* webpackChunkName: "base" */ 'pages/Index.vue')
const About = () => import(/* webpackChunkName: "base" */ 'pages/About.vue')

const DatasetAbout = () => import(/* webpackChunkName: "dataset" */ 'pages/datasets/DatasetAbout.vue')
const DatasetBrowser = () => import(/* webpackChunkName: "dataset" */ 'pages/datasets/DatasetBrowser.vue')
const DatasetEdit = () => import(/* webpackChunkName: "dataset" */ 'pages/datasets/DatasetEdit.vue')

const OrderAbout = () => import(/* webpackChunkName: "order" */ 'pages/orders/OrderAbout.vue')
const OrderBrowser = () => import(/* webpackChunkName: "order" */ 'pages/orders/OrderBrowser.vue')
const OrderEdit = () => import(/* webpackChunkName: "order" */ 'pages/orders/OrderEdit.vue')

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
    path: '*',
    component: () => import('pages/Error404.vue'),
  }
]

export default routes
