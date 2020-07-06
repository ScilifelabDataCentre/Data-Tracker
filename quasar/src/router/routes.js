import MainLayout from 'layouts/MainLayout.vue'
import Index from 'pages/Index.vue'
import About from 'pages/About.vue'
import DatasetBase from 'pages/datasets/DatasetBase.vue'
import DatasetBrowser from 'pages/datasets/DatasetBrowser.vue'

const routes = [
  {
    path: '/',
    component:  MainLayout,
    children: [
      { path: '', component: Index },
      { path: 'about', component: About },
    ]
  },
  {
    path: '/datasets',
    component:  MainLayout,
    children: [
      { path: '', redirect: 'browser' },
      { path: 'browser', component: DatasetBrowser },
    ]
  },

  {
    path: '*',
    component: () => import('pages/Error404.vue')
  }
]

export default routes
