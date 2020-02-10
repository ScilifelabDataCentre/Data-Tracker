<template>
<div id="app">
  <nav-bar></nav-bar>

  <transition name="notification-fade">
    <div v-if="notification.message" :class="{notification: true, 'is-info': type === 'normal', 'is-danger': notification.type === 'warning'}">
      {{ notification.message }}
    </div>
  </transition>

  <router-view class="container"></router-view>
  <footer class="footer">
    <img class="logo" :src="require('./assets/img/data-centre-logo.png')" alt="SciLife Data Centre logo"/>
  </footer>
</div>
</template>

<script>
import {mapGetters} from 'vuex';
import NavigationBar from './components/NavigationBar.vue';

export default {
  name: 'App',
  components: {
    'nav-bar': NavigationBar
  },
  computed: {
    ...mapGetters(['notification']),
  },
  data() {
    return {
    }
  },
  
  created () {
    this.$store.dispatch('getUser');
  },
}
</script>

<style>
#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
}

img.logo {
    height: 70px;
}

.notification-fade-enter-active, .notification-fade-leave-active {
    transition: opacity .5s;
}

.notification-fade-enter, .notification-fade-leave-to {
    opacity: 0;
}

</style>
