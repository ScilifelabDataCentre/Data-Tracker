import Vue from 'vue';
import VueRouter from 'vue-router';
import ProjectAbout from '../components/projectInfo/ProjectAbout.vue'
import ProjectBrowser from '../components/ProjectBrowser.vue'
import ProjectContainer from '../components/projectInfo/ProjectContainer.vue'
import AdminUserBrowser from '../components/AdminUserBrowser.vue'
import NotFound from '../components/NotFound.vue'
import StartPage from '../components/StartPage.vue'

Vue.use(VueRouter);

const router = new VueRouter({
  mode: 'history',
  base: '/',
  routes: [
    {
      path: '/projects',
      component: ProjectBrowser,
    },
    {
      path: '/project/:id/',
      component: ProjectContainer,
      props: true,
      children: [
        {
          path: '',
          redirect: 'about',
        },
        {
          path: 'about',
          component: ProjectAbout,
        },
        {
          path: 'edit',
          component: ProjectAbout,
        }
      ],
    },
    {
      path: '/',
      component: StartPage,
    },
    {
      path: '/admin/users',
      component: AdminUserBrowser,
    },
    {
      path: '*',
      component: NotFound
    },
  ]
});

export default router;
