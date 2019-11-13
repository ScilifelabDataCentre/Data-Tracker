<template>
<div class="project-edit">
  <form @submit="submitProjectForm">
    <div class="field" v-if="newProject.id !== -1">
      <label for="project-id" class="label">Project ID</label>
      <div class="control">
        <input id="project-id"
               class="input"
               name="PROJECT_ID"
               type="text"
               placeholder="id"
               v-model="newProject.id"
               disabled="true"/>
      </div>
    </div>
    <div class="field">
      <label class="label" for="project-title">Title</label>
      <input id="project-title"
             class="input"
             name="PROJECT_TITLE"
             type="text"
             placeholder="Title"
             v-model="newProject.title"/>
    </div>
    <div class="field">
      <label class="label" for="project-description">Description</label>
      <input id="project-description"
             class="input"
             v-model="newProject.description"
             name="PROJECT_DESCRIPTION"
             type="text"
             placeholder="Description" />
    </div>
    <div class="field">
      <label class="label" for="project-contact">Contact information</label>
      <input id="project-contact"
             class="input"
             v-model="newProject.contact"
             name="PROJECT_CONTACT"
             type="text"
             placeholder="Contact information" />
    </div>

    <div class="field is-grouped">
      <div class="control">
        <button class="button is-link">Submit</button>
      </div>
      <div class="control">
        <button class="button is-light @click=cancelChanges">Cancel</button>
      </div>
      <div class="control">
        <button class="button is-danger" v-if="newProject.id != -1 && (user.permission === 'Steward' || user.permission === 'Admin')" @click="deleteProject">Delete</button>
      </div>
    </div>
  </form>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'ProjectEdit',
  props: ['id'],
  components: {
  },
  computed: {
    ...mapGetters(['project', 'user']),
  },
  data () {
    return {
      newProject: {
        id: -1,
        title: '',
        description: '',
        contact: '',
        datasets: [],
      },
      value: null,
    }
  },
  created () {
    this.$store.dispatch('getProject', this.id)
      .then(() => {
        this.newProject = this.project;
      });
  },
  methods: {
    cancelChanges(event) {
      event.preventDefault();
      if (this.newProject.id === -1) {
        this.$router.push("/project/browser");
      }
      else {
        this.$router.push("/project/" + this.newProject.id + "/about");
      }
    },

    deleteProject(event) {
      event.preventDefault();
      this.$store.dispatch('deleteProject', this.newProject.id)
        .then(() => {
          this.$router.push("/project/browser");
        });
    },
    submitProjectForm(event) {
      event.preventDefault();
      this.$store.dispatch('saveProject', this.newProject)
        .then((response) => {
          // add performed
          let id = -1;
          if (response.data) {
            id = response.data.id;
          }
          else {
            id = this.newProject.id
          }
          this.$router.push("/project/" + id + "/about");
        });
    },
  },
}
</script>

<style scoped>
.warning {
    font-weight: bold;
    text-align: center;
    font-size: large;
}
</style>
