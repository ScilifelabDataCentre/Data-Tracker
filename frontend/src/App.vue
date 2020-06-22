<template>
<div id="app">
  <nav-bar></nav-bar>
  
  <transition name="notification-fade">
    <div v-if="notification.message" :class="{notification: true, 
                                             'is-info': type === 'normal', 
                                             'is-danger': notification.type === 'warning'}">
      <hr class="navbar-divider">
      {{ notification.message }}
    </div>
  </transition>

  <div class="container">
    <router-view class="section"></router-view>
  </div>

  <footer class="footer">
    <img :src="require('./assets/img/data-centre-logo.svg')" alt="SciLife Data Centre logo" class="logo"/>
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
    this.$store.dispatch('getCurrentUser');
  },

  methods: {
    resetNotification(event) {
      event.preventDefault();
      this.$store.dispatch('updateNotification', ['', '']);
    }
  }
  
}
</script>

<style>
#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
}

.notification-fade-enter-active, .notification-fade-leave-active {
    transition: opacity .3s;
}

.notification-fade-enter, .notification-fade-leave-to {
    opacity: 0;
}

img.logo {
    height: 4em;
}
</style>
