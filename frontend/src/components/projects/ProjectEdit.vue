<template>
<div class="project-edit">
  <form @submit="submitProjectForm">
    <div class="field">
      <label for="PROJECT_ID" class="field-label">Id:</label>
      <input v-if="newProject.id !== -1" name="PROJECT_ID"
             type="text"
             placeholder="id"
             v-model="newProject.id"
             disabled="true"/>

    </div>
    <div class="field">
      <label class="field-label">Title:</label>
      <input name="PROJECT_TITLE"
             type="text"
             placeholder="Title"
             v-model="newProject.title"/>
    </div>
    <div class="field">
      <label class="field-label">Description:</label>
      <input v-model="newProject.description" name="PROJECT_DESCRIPTION"
             type="text" placeholder="Description" />
    </div>
    <div class="field">
      <label class="field-label">Contact information:</label>
      <input v-model="newProject.contact" name="PROJECT_CONTACT"
             type="text" placeholder="Contact information" />
    </div>
    <button>Submit</button>
    <div>
      <button v-if="newProject.id != -1" @click="deleteProject" class="delete-entry">Delete</button>
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
    ...mapGetters(['project']),
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
.project-title {
    font-weight: bold;
    font-size: 2em;
    text-align: center;
    margin: 0em 0em 0.4em 0em;
}

.field-label {
    font-weight: bold;
}

.field {
    margin: 0.4em 0em;
}

.warning {
    font-weight: bold;
    text-align: center;
    font-size: large;
}
</style>
