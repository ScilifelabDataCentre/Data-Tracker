import Vue from 'vue';
import VueRouter from 'vue-router';
import ProjectAbout from '../components/projects/ProjectAbout.vue'
import ProjectBrowser from '../components/projects/ProjectBrowser.vue'
import ProjectContainer from '../components/projects/ProjectContainer.vue'
import ProjectViewer from '../components/projects/ProjectContainer.vue'
import DatasetAbout from '../components/projects/ProjectAbout.vue'
import DatasetBrowser from '../components/projects/ProjectBrowser.vue'
import DatasetContainer from '../components/projects/ProjectContainer.vue'
import DatasetViewer from '../components/projects/ProjectContainer.vue'
import AdminUserBrowser from '../components/admin/AdminUserBrowser.vue'
import NotFound from '../components/NotFound.vue'
import StartPage from '../components/StartPage.vue'

Vue.use(VueRouter);

const router = new VueRouter({
  mode: 'history',
  base: '/',
  routes: [
    {
      path: '/',
      component: StartPage,
    },
    {
      path: '/project',
      component: ProjectContainer,
      children: [
        {
          path: '',
          redirect: 'browser',
        },
        {
          path: 'browser',
          component: ProjectBrowser
        },
        {
          path: ':id',
          component: ProjectViewer,
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
        }
      ],
    },
    {
      path: '/dataset',
      component: DatasetContainer,
      children: [
        {
          path: '',
          redirect: 'browser',
        },
        {
          path: 'browser',
          component: DatasetBrowser
        },
        {
          path: ':id',
          component: DatasetViewer,
          props: true,
          children: [
            {
              path: '',
              redirect: 'about',
            },
            {
              path: 'about',
              component: DatasetAbout,
            },
            {
              path: 'edit',
              component: DatasetAbout,
            }
          ],
        }
      ],
    },
    {
      path: '/user',
      component: AdminUserBrowser,
      children: [   
        {
          path: '',
          redirect: 'about'
        },
        {
          path: 'about',
          component: AdminUserBrowser,
        },
        {
          path: 'edit',
          component: AdminUserBrowser,
        },
      ],
    },
    {
      path: '/admin',
      component: AdminUserBrowser,
      children: [
        {
          path: '',
          redirect: 'stats',
        },

        {
          path: 'stats',
          component: AdminUserBrowser,
        },
        {
          path: 'projects',
          component: AdminUserBrowser,
        },
        {
          path: 'datasets',
          component: AdminUserBrowser,
        },
        {
          path: 'users',
          component: AdminUserBrowser,
        }
      ],
    },
    {
      path: '*',
      component: NotFound
    },
  ]
});

export default router;
