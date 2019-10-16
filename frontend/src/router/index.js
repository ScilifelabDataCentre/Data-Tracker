import Vue from 'vue';
import VueRouter from 'vue-router';
import ProjectInfo from '../components/ProjectInfo.vue'
import NotFound from '../components/NotFound.vue'
import StartPageComponent from '../components/StartPageComponent.vue'

Vue.use(VueRouter);

const router = new VueRouter({
  mode: 'history',
  base: '/menu/',
  routes: [
    {
      path: '/project/:id',
      component: ProjectInfo,
      props: true,
    },
    {
      path: '/',
      component:  StartPageComponent,
    },
    {
      path: '*',
      component:  NotFound
    },
  ]
});

export default router;
