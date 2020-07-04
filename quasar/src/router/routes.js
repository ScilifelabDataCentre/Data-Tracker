import MainLayout from 'layouts/MainLayout.vue'
import Index from 'pages/Index.vue'
import About from 'pages/About.vue'

const routes = [
  {
    path: '/',
    component:  MainLayout,
    children: [
      { path: '', component: Index },
      { path: '/about', component: About }
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '*',
    component: () => import('pages/Error404.vue')
  }
]

export default routes
