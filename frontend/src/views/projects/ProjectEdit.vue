<template>
<div class="project-edit">
  <form @submit="submitProjectForm">

    <div class="field" v-if="newProject.id !== -1">
      <label for="project-id" class="label">Project UUID</label>
      <div class="control">
        <input id="project-id"
               class="input"
               name="PROJECT_ID"
               type="text"
               placeholder="uuid"
               v-model="newProject.id"
               disabled />
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
      <textarea class="textarea"
		id="project-description"
		v-model="newProject.description"
		name="PROJECT_DESCRIPTION"
		type="text"
		placeholder="Project Description"
		rows="10">
      </textarea>
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
    <div class="columns">
      <div class="column">
        <div class="field">
          <label class="label">Extra fields</label>
          <div class="field is-grouped">
            <input id="project-extra-key"
                   class="input"
                   v-model="extraKey"
                   name="PROJECT_EXTRA_KEY"
                   type="text"
                   placeholder="Key" />
            <input id="project-extra-value"
                   class="input"
                   v-model="extraValue"
                   name="PROJECT_EXTRA_VALUE"
                   type="text"
                   placeholder="Value" />
            <div class="control">
              <button class="button is-light" @click="saveExtra">Save</button>
            </div>
          </div>
        </div>
      </div>
      <div class="column">
        <table class="table is-fullwidth">
          <thead>
            <th scope="column">Key</th>
            <th scope="column">Value</th>
          </thead>
          <tbody>
            <tr v-for="key in Object.keys(newProject.extra)" :key="key">
              <td>{{ key }}</td>
              <td>{{ newProject.extra[key] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="field is-grouped">
      <div class="control">
        <button class="button is-link">Submit</button>
      </div>
      <div class="control">
        <button class="button is-light @click=cancelChanges">Cancel</button>
      </div>
      <div class="control">
        <button class="button is-danger" v-if="newProject.id != -1" @click="deleteProject">Delete</button>
      </div>
    </div>
  </form>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'ProjectEdit',
  props: ['uuid'],
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
        dmp: '',
        contact: '',
        datasets: [],
        extra: {}
      },
      extraKey: '',
      extraValue: ''
    }
  },
  created () {
    if (this.uuid) {
      this.$store.dispatch('getProject', this.uuid)
        .then(() => {
          this.newProject = this.project;
          this.newProject.id = this.newProject._id;
          delete this.newProject._id;
        });
    }
  },
  methods: {
    saveExtra(event) {
      event.preventDefault();
      if (this.extraKey !== '') {
        if (this.newProject.extra[this.extraKey] !== undefined) {
          if (this.extraValue === '') {
            this.$delete(this.newProject.extra, this.extraKey);
          }
          else {
            this.newProject.extra[this.extraKey] = this.extraValue;
          }
        }
        else {
          if (this.extraValue !== '') {
            this.$set(this.newProject.extra, this.extraKey, this.extraValue);
          }
        }
      }
    },    

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
