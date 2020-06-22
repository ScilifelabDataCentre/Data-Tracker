import Vue from 'vue';
import VueRouter from 'vue-router';

import AboutPage from '../components/AboutPage.vue'

import NotFound from '../components/NotFound.vue'

import StartPage from '../views/StartPage.vue'

import LoginPageKey from '../views/LoginPageKey.vue'

const CurrentUserAbout = () => import(/* webpackChunkName: "user" */ '../views/user/CurrentUserAbout.vue')
const CurrentUserEdit = () => import(/* webpackChunkName: "user" */ '../views/user/CurrentUserEdit.vue')
const CurrentUserContainer = () => import(/* webpackChunkName: "user" */ '../views/user/CurrentUserContainer.vue')

const DatasetAbout = () => import(/* webpackChunkName: "dataset" */ '../views/datasets/DatasetAbout.vue')
const DatasetBrowser = () => import(/* webpackChunkName: "dataset" */ '../views/datasets/DatasetBrowser.vue')
const DatasetContainer = () => import(/* webpackChunkName: "dataset" */ '../views/datasets/DatasetContainer.vue')
const DatasetEdit = () => import(/* webpackChunkName: "dataset" */ '../views/datasets/DatasetEdit.vue')

const ProjectAbout = () => import(/* webpackChunkName: "project" */ '../views/projects/ProjectAbout.vue')
const ProjectBrowser = () => import(/* webpackChunkName: "project" */ '../views/projects/ProjectBrowser.vue')
const ProjectContainer = () => import(/* webpackChunkName: "project" */ '../views/projects/ProjectContainer.vue')
const ProjectEdit = () => import(/* webpackChunkName: "project" */ '../views/projects/ProjectEdit.vue')

const AdminContainer = () => import(/* webpackChunkName: "admin" */ '../views/admin/AdminContainer.vue')
const Stats = () => import(/* webpackChunkName: "admin" */ '../views/admin/Stats.vue')
const UserManager = () => import(/* webpackChunkName: "admin" */ '../views/admin/UserManager.vue')
const UserEdit = () => import(/* webpackChunkName: "admin" */ '../views/admin/UserEdit.vue')

const OrderAbout = () => import(/* webpackChunkName: "order" */ '../views/orders/OrderAbout.vue')
const OrderBrowser = () => import(/* webpackChunkName: "order" */ '../views/orders/OrderBrowser.vue')
const OrderContainer = () => import(/* webpackChunkName: "order" */ '../views/orders/OrderContainer.vue')
const OrderEdit = () => import(/* webpackChunkName: "order" */ '../views/orders/OrderEdit.vue')

const LogViewer = () => import(/* webpackChunkName: "logs" */ '../components/LogViewer.vue')
const ActionLogViewer = () => import(/* webpackChunkName: "logs" */ '../components/ActionLogViewer.vue')

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
          path: ':uuid',
          redirect: ':uuid/about',
        },
        {
          path: ':uuid/about',
          component: ProjectAbout,
          props: true,
        },
        {
          path: ':uuid/edit',
          component: ProjectEdit,
          props: true,
          meta: {
            loginRequired: true,
          },
        },
        {
          path: ':uuid/log',
          component: LogViewer,
          props: {'dataType': 'project' },
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
          path: ':uuid/log',
          component: LogViewer,
          props: {'dataType': 'dataset' },
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
          path: 'add',
          component: OrderEdit,
        },
        {
          path: 'browser',
          component: OrderBrowser
        },
        {
          path: ':uuid/about',
          component: OrderAbout,
          props: true,
        },
        {
          path: ':uuid/log',
          component: LogViewer,
          props: {'dataType': 'order' },
        },
        {
          path: ':uuid/edit',
          component: OrderEdit,
          props: true,
        },
        {
          path: ':uuid',
          redirect: ':uuid/about',
        },
      ],
    },
    
    {
      path: '/user',
      component: CurrentUserContainer,
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
          component: CurrentUserAbout,
        },
        {
          path: 'edit',
          component: CurrentUserEdit,
          meta: {
            loginRequired: true,
          },
        },
        {
          path: 'log',
          component: LogViewer,
          props: {'dataType': 'me' },
        },
        {
          path: 'actions',
          component: ActionLogViewer,
          props: {'dataType': 'me' },
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
          path: 'stat',
          component: Stats,
        },
        {
          path: 'user/list',
          component: UserManager,
          meta: {
            adminRequired: true,
          },
        },
        {
          path: 'user/:uuid/edit',
          component: UserEdit,
          props: true,
          meta: {
            adminRequired: true,
          },
        },
        {
          path: 'user/:uuid/log',
          component: LogViewer,
          props: {'dataType': 'user' },
        },
        {
          path: 'user/:uuid/actions',
          component: ActionLogViewer,
          props: {'dataType': 'user' },
        },

        {
          path: 'user/add',
          component: UserEdit,
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
