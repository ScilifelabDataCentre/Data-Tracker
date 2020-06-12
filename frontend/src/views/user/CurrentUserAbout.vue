<template>
<div class="user-about">
  <h4 class="title is-4">User Information</h4>
  <table class="table is-hoverable is-striped">
    <tbody>
      <tr>
        <th scope="row">Name</th>
        <td>{{ user.name }}</td>
      </tr>
      <tr>
        <th scope="row">Affiliation</th>
        <td>{{ user.affiliation }}</td>
      </tr>
      <tr>
        <th scope="row">Email</th>
        <td>{{ user.email }}</td>
      </tr>
      <tr>
        <th scope="row">Authentication ID</th>
        <td>{{ user.authId }}</td>
      </tr>
      <tr v-if="user.permissions.length > 0">
        <th scope="row" :rowspan="user.permissions.length">Permissions</th>
        <td>
          <ul>
            <li v-for="entry in user.permissions" :key="entry">
              <span class="tag is-info is-light">
                {{entry}}
              </span>
            </li>
          </ul>
        </td>
      </tr>
    </tbody>
  </table>

  <div v-if="user_orders.length > 0">
    <h4 class="title is-4">Orders</h4>
    <table class="table is-hoverable is-striped">
      <thead>
        <tr>
          <th>UUID</th>
          <th>Title</th>
          <th>Datasets</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in user_orders" :key="order._id">
          <td><a :href="'/dataset/' + order._id">{{ order._id }}</a></td>
          <td>{{ order.title }}</td>
          <td>
            <ul>
              <li v-for="ds_uuid in order.datasets" :key="ds_uuid">
                <a :href="'/dataset/' + ds_uuid">{{ ds_uuid }}</a>
              </li>
            </ul>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="user_datasets.length > 0">
    <h4 class="title is-4">Datasets</h4>
    <table class="table is-hoverable is-striped">
      <thead>
        <tr>
          <th>UUID</th>
          <th>Title</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="dataset in user_datasets" :key="dataset._id">
          <td><a :href="'/dataset/' + dataset._id">{{ dataset._id }}</a></td>
          <td>{{ dataset.title }}</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-if="user_projects.length > 0">
    <h4 class="title is-4">Projects</h4>
    <table class="table is-hoverable is-striped is-fullwidth">
      <thead>
        <tr>
          <th>UUID</th>
          <th>Title</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="project in user_projects" :key="project._id">
          <td><a :href="'/dataset/' + project._id">{{ project._id }}</a></td>
          <td>{{ project.title }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <router-link to="edit">
    <button class="button is-link">
      Edit
    </button>
  </router-link>

</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'CurrentUserAbout',
  data () {
    return {
    }
  },
  computed: {
    ...mapGetters(['user',
                   'userOrders',
                   'userDatasets',
                   'userProjects']),
  },
  mounted () {
    this.$store.dispatch('getCurrentUser');
    this.$store.dispatch('getCurrentUserOrders');
    this.$store.dispatch('getCurrentUserDatasets');
    this.$store.dispatch('getCurrentUserProjects');
  }
}
</script>

<style scoped>
  
</style>
