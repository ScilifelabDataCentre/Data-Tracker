import Vue from 'vue';
import VueRouter from 'vue-router';

import AdminUserBrowser from '../components/admin/AdminUserBrowser.vue'

import DatasetAbout from '../components/datasets/DatasetAbout.vue'
import DatasetEdit from '../components/datasets/DatasetEdit.vue'
import DatasetBrowser from '../components/datasets/DatasetBrowser.vue'
import DatasetContainer from '../components/datasets/DatasetContainer.vue'

import NotFound from '../components/NotFound.vue'

import ProjectAbout from '../components/projects/ProjectAbout.vue'
import ProjectBrowser from '../components/projects/ProjectBrowser.vue'
import ProjectEdit from '../components/projects/ProjectEdit.vue'
import ProjectContainer from '../components/projects/ProjectContainer.vue'

import StartPage from '../components/StartPage.vue'

import UserAbout from '../components/user/UserAbout.vue'
import UserContainer from '../components/user/UserContainer.vue'


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
          path: 'add',
          component: ProjectEdit,
        },
        {
          path: ':id(\\d+)',
          redirect: ':id/about',
        },
        {
          path: ':id(\\d+)/about',
          component: ProjectAbout,
          props: true,
        },
        {
          path: ':id(\\d+)/edit',
          component: ProjectEdit,
          props: true,
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
          path: ':id(\\d+)',
          redirect: ':id/about',
        },
        {
          path: ':id(\\d+)/about',
          component: DatasetAbout,
          props: true,
        },
        {
          path: ':id(\\d+)/edit',
          component: DatasetEdit,
          props: true,
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
