import Vue from 'vue';
import VueRouter from 'vue-router';
import ProjectInfo from '../components/ProjectInfo.vue'

Vue.use(VueRouter);

const router = new VueRouter({
  mode: 'hash',
  base: '/menu/',
  routes: [
    {
      path: '/project/:id',
      component: ProjectInfo,
      props: true,
    },
    {
      path: '*',
      component: { template: `<div>404.</div>` }
    },
  ]
});

export default router;
