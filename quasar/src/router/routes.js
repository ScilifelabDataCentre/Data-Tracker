import MainLayout from 'layouts/MainLayout.vue'
import Index from 'pages/Index.vue'
import About from 'pages/About.vue'
import DatasetAbout from 'pages/datasets/DatasetAbout.vue'
import DatasetBrowser from 'pages/datasets/DatasetBrowser.vue'
import DatasetEdit from 'pages/datasets/DatasetEdit.vue'

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
      {
        path: 'add',
        component: DatasetEdit,
        props: { 'uuid': '' },
        name: 'Dataset Add'
      },
    ]
  },

  {
    path: '*',
    component: () => import('pages/Error404.vue'),
  }
]

export default routes
