<template>
<div class="user-about">
  <h1 class="title is-1">About the Current User ({{ user.name }})</h1>

  <section class="section">
    <h2 class="title is-3">Basic Information</h2>
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

  <router-link to="edit">
    <button class="button is-link">
      Edit
    </button>
  </router-link>
  </section>

  <section class="section">
    <div v-if="userOrders.length > 0">
      <h2 class="title is-3">Orders</h2>
      <table class="table is-hoverable is-striped">
	<thead>
          <tr>
            <th>UUID</th>
            <th>Title</th>
            <th>Datasets</th>
          </tr>
	</thead>
	<tbody>
          <tr v-for="order in userOrders" :key="order._id">
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
  </section>

  <section class="section">
    <div v-if="userDatasets.length > 0">
      <h2 class="title is-3">Datasets</h2>
      <table class="table is-hoverable is-striped">
	<thead>
          <tr>
            <th>UUID</th>
            <th>Title</th>
          </tr>
	</thead>
	<tbody>
          <tr v-for="dataset in userDatasets" :key="dataset._id">
            <td><a :href="'/dataset/' + dataset._id">{{ dataset._id }}</a></td>
            <td>{{ dataset.title }}</td>
          </tr>
	</tbody>
      </table>
    </div>
  </section>


  <section class="section">
    <div v-if="userProjects.length > 0">
      <h2 class="title is-3">Projects</h2>
      <table class="table is-hoverable is-striped">
	<thead>
          <tr>
            <th>UUID</th>
            <th>Title</th>
          </tr>
	</thead>
	<tbody>
          <tr v-for="project in userProjects" :key="project._id">
            <td><a :href="'/dataset/' + project._id">{{ project._id }}</a></td>
            <td>{{ project.title }}</td>
          </tr>
	</tbody>
      </table>
    </div>
  </section>
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
