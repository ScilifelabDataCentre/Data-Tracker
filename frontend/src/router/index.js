import Vue from 'vue';
import VueRouter from 'vue-router';

import AboutPage from '../components/AboutPage.vue'

import NotFound from '../components/NotFound.vue'

import StartPage from '../components/StartPage.vue'

import LoginPageKey from '../components/LoginPageKey.vue'

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

const AdminContainer = () => import(/* webpackChunkName: "admin" */ '../components/admin/AdminContainer.vue')
const DoiManager = () => import(/* webpackChunkName: "admin" */ '../components/admin/DoiManager.vue')
const Stats = () => import(/* webpackChunkName: "admin" */ '../components/admin/Stats.vue')
const UserManager = () => import(/* webpackChunkName: "admin" */ '../components/admin/UserManager.vue')

const OrderAbout = () => import(/* webpackChunkName: "order" */ '../components/orders/OrderAbout.vue')
const OrderBrowser = () => import(/* webpackChunkName: "order" */ '../components/orders/OrderBrowser.vue')
const OrderContainer = () => import(/* webpackChunkName: "order" */ '../components/orders/OrderContainer.vue')
const OrderEdit = () => import(/* webpackChunkName: "order" */ '../components/orders/OrderEdit.vue')

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
      path: '/login/key',
      component: LoginPageKey,
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
          path: ':uuid/about',
          component: DatasetAbout,
          props: true,
        },
        {
          path: ':uuid/edit',
          component: DatasetEdit,
          props: true,
          meta: {
            loginRequired: true,
          },
        },
        {
          path: ':uuid',
          redirect: ':uuid/about',
        },
      ],
    },

    {
      path: '/order',
      component: OrderContainer,
      meta: {
        loginRequired: true,
        stewardRequired: true,
      },
      children: [
        {
          path: '',
          redirect: 'browser',
        },
        {
          path: 'browser',
          component: OrderBrowser
        },
        {
          path: ':id/about',
          component: OrderAbout,
          props: true,
        },
        {
          path: ':id/edit',
          component: OrderEdit,
          props: true,
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
      meta: {
        loginRequired: true,
      },
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
      path: '/admin',
      component: AdminContainer,
      meta: {
        loginRequired: true,
      },
      children: [
        {
          path: 'stats',
          component: Stats,
        },
        {
          path: 'dois',
          component: DoiManager,
        },
        {
          path: 'users',
          component: UserManager,
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
