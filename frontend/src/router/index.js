import Vue from 'vue';
import VueRouter from 'vue-router';

import AboutPage from '../components/AboutPage.vue'

import AdminUserBrowser from '../components/admin/AdminUserBrowser.vue'

import NotFound from '../components/NotFound.vue'

import StartPage from '../components/StartPage.vue'

import UserAbout from '../components/user/UserAbout.vue'
import UserContainer from '../components/user/UserContainer.vue'

const DatasetAbout = () => import(/* webpackChunkName: "dataset" */ '../components/datasets/DatasetAbout.vue')
const DatasetBrowser = () => import(/* webpackChunkName: "dataset" */ '../components/datasets/DatasetBrowser.vue')
const DatasetContainer = () => import(/* webpackChunkName: "dataset" */ '../components/datasets/DatasetContainer.vue')
const DatasetEdit = () => import(/* webpackChunkName: "dataset" */ '../components/datasets/DatasetEdit.vue')

const ProjectAbout = () => import(/* webpackChunkName: "project" */ '../components/projects/ProjectAbout.vue')
const ProjectBrowser = () => import(/* webpackChunkName: "project" */ '../components/projects/ProjectBrowser.vue')
const ProjectContainer = () => import(/* webpackChunkName: "project" */ '../components/projects/ProjectContainer.vue')
const ProjectEdit = () => import(/* webpackChunkName: "project" */ '../components/projects/ProjectEdit.vue')

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
      path: '/about',
      component: AboutPage,
    },
    {
      path: '/search',
      component: AboutPage,
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
          path: 'add',
          component: ProjectEdit,
        },
        {
          path: ':id',
          redirect: ':id/about',
        },
        {
          path: ':id/about',
          component: ProjectAbout,
          props: true,
        },
        {
          path: ':id/edit',
          component: ProjectEdit,
          props: true,
          meta: {
            loginRequired: true,
          },
        },
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
          path: 'add',
          component: DatasetEdit,
        },

        {
          path: ':id/about',
          component: DatasetAbout,
          props: true,
        },
        {
          path: ':id/edit',
          component: DatasetEdit,
          props: true,
          meta: {
            loginRequired: true,
          },
        },
        {
          path: ':id',
          redirect: ':id/about',
        },
      ],
    },

    {
      path: '/user',
      component: UserContainer,
      children: [   
        {
          path: '',
          redirect: 'about'
        },
        {
          path: 'about',
          component: UserAbout,
        },
        {
          path: 'edit',
          component: UserAbout,
          meta: {
            loginRequired: true,
          },
        },
      ],
    },

    {
      path: '/manage',
      component: AdminUserBrowser,
      meta: {
        loginRequired: true,
      },
      children: [
        {
          path: '',
          redirect: 'summary',
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
          meta: {
            adminRequired: true,
          },

        }
      ],
    },
    {
      path: '*',
      component: NotFound
    },
  ]
});

router.beforeEach((to, from, next) => {
  if(to.matched.some(record => record.meta.loginRequired)) {
    from;
    // if from and not logged in return to from, show notification
    if(to.matched.some(record => record.meta.adminRequired)) {
      from;
    }
  }
  next({ to })
});

export default router;
