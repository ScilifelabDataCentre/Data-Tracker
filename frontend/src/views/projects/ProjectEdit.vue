<template>
<div class="project-edit">
  <h1 class="title is-1">Edit Project <span v-if="newProject.title.length > 0">({{ newProject.title }})</span></h1>
  <form @submit="submitProjectForm">

    <div class="field" v-if="newProject.id !== '-1'">
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

    <div class="field">
      <label class="label" for="project-contact">Data Management Plan</label>
      <div class="control">
        <input id="project-dmp"
               class="input"
               v-model="newProject.dmp"
               name="PROJECT_DMP"
               type="text"
               placeholder="https://dmp.url" />
      </div>
    </div>

    <div class="columns">
      <div class="column">
        <div class="field">
          <label class="label" for="project-publication">Publications</label>
          <div class="field has-addons">
            <div class="control">
              <div class="field is-grouped">
                <input id="project-publication"
                       class="input"
                       v-model="publication"
                       name="PROJECT_PUBLICATION"
                       type="text"
                       placeholder="Value" />
                <div class="control">
                  <button class="button is-primary" @click="addPublication">Add</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="column">
        <ul>
          <li class="nobullet" href="#" v-for="(pubtext, i) in newProject.publications" :key="i">
            <div class="tag is-light">{{ pubtext }} <button class="delete" href="#" @click="deletePublication($event, i)"></button></div>
          </li>
        </ul>
      </div>
    </div>
    
    <div class="columns">
      <div class="column">
        <div class="field">
          <label class="label" for="project-datasets">Datasets</label>
          <div class="control">
            <div class="select">
              <select id="project-datasets"
                      name="PROJECT_DATASETS"
                      v-model="datasetSelection" @change="addDataset" :disabled="availableDatasets.length === 0">
                <option :value="-1">Choose dataset to add</option>
                <option v-for="(dataset, i) in availableDatasets" :key="dataset._id" :value="i">{{ dataset.title }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>
      <div class="column">
        <ul>
          <li></li>
          <li class="nobullet" href="#" v-for="(dataset, i) in newProject.datasets" :key="dataset._id">
            <div class="tag is-light">{{ dataset.title }} <button class="delete" href="#" @click="deleteDataset($event, i)"></button></div>
          </li>
        </ul>
      </div>
    </div>

    <div class="columns">
      <div class="column">
        <div class="field">
          <label class="label" for="project-owner">Owners</label>
          <div class="field has-addons">
            <div class="control">
              <input id="project-owner"
                     class="input"
                     v-model="owner"
                     name="PROJECT_OWNER"
                     type="text"
                     placeholder="Value" />
            </div>
            <div class="control">
              <button class="button is-primary" @click="addOwner">Add</button>
            </div>
          </div>
        </div>
      </div>
      <div class="column">
        <ul>
          <li class="nobullet" href="#" v-for="(userId, i) in newProject.owners" :key="i">
            <div class="tag is-light">{{ userId }} <button class="delete" href="#" @click="deleteOwner($event, i)"></button></div>
          </li>
        </ul>
      </div>
    </div>
    
    <div class="columns">
      <div class="column">
        <div class="field">
          <label class="label">Extra fields</label>
          <div class="field has-addons">
            <div class="control">
              <input id="project-extra-key"
                     class="input"
                     v-model="extraKey"
                     name="PROJECT_EXTRA_KEY"
                     type="text"
                     placeholder="Key" />
            </div>
            <div class="control">
              <input id="project-extra-value"
                     class="input"
                     v-model="extraValue"
                     name="PROJECT_EXTRA_VALUE"
                     type="text"
                     placeholder="Value" />
            </div>
            <div class="control">
              <button class="button is-primary" @click="saveExtra">Save</button>
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
        <button class="button is-link" @click="submitProjectForm">Submit</button>
      </div>
      <div class="control">
        <button class="button is-light" @click="cancelChanges">Cancel</button>
      </div>
      <div class="control">
        <button class="button is-danger" v-if="newProject.id !== -1" @click="deleteProject">Delete</button>
      </div>
      <p v-if="submitError" class="help is-danger">Action failed</p>
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
        id: '-1',
        title: '',
        description: '',
        dmp: '',
        contact: '',
        datasets: [],
        publications: [],
        extra: {}
      },
      extraKey: '',
      extraValue: '',
      publication: '',
      submitError: false,
      datasetSelection: -1,
      owner: '',
      availableDatasets: '',
    }
  },

  mounted () {
    if (this.uuid) {
      this.$store.dispatch('getProject', this.uuid)
        .then(() => {
          this.newProject = this.project;
          this.newProject.id = this.newProject._id;
          delete this.newProject._id;
        });
      this.$store.dispatch('getCurrentUser', this.uuid)
        .then(() => {
          if (this.user.permissions.includes('DATA_MANAGEMENT')) {
            this.$store.dispatch('getDatasets')
              .then((response) => {
                this.availableDatasets = response.data.datasets;
              });
          }
          else {
            this.$store.dispatch('getCurrentUserDatasets')
              .then((response) => {
                this.availableDatasets = response.data.datasets;
              });
          }
          this.availableDatasets.sort((a, b) => {
            if (a.title > b.title) {
              return 1;
            }
            if (a.title < b.title) {
              return -1;
            }
            return 0;
          });
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

    addPublication(event) {
      event.preventDefault();
      this.newProject.publications.push(this.publication);
      this.publication = '';
    },

    deletePublication(event, position) {
      event.preventDefault();
      this.newProject.publications.splice(position, 1);
    },

    addDataset(event) {
      event.preventDefault();
      if (this.datasetSelection !== '-1' && !this.newProject.datasets.includes(this.availableDatasets[this.datasetSelection])) {
        this.newProject.datasets.push(this.availableDatasets[this.datasetSelection]);
        this.datasetSelection = -1;
      }
    },

    deleteDataset(event, position) {
      event.preventDefault();
      this.newProject.datasets.splice(position, 1);
    },
    
    addOwner(event) {
      event.preventDefault();
      this.newProject.owners.push(this.owner);
      this.owner = '';
    },

    deleteOwner(event, position) {
      event.preventDefault();
      this.newProject.owners.splice(position, 1);
    },

    cancelChanges(event) {
      event.preventDefault();
      if (this.uuid === null) {
        this.$router.push("/project/browser");
      }
      else {
        this.$router.push("/project/" + this.uuid + "/about");
      }
    },

    deleteProject(event) {
      event.preventDefault();
      this.$store.dispatch('deleteProject', this.uuid)
        .then(() => {
          this.$router.push("/project/browser");
        })
        .catch(() => {
          this.submitError = true;
        });

    },

    submitProjectForm(event) {
      event.preventDefault();
      let newData = this.newProject;
      let datasetUuids = [];
      for (let i=0; i < newData.datasets.length; i++) {
        datasetUuids.push(newData.datasets[i]._id);
      }
      newData.datasets = datasetUuids;
      this.$store.dispatch('saveProject', newData)
        .then((response) => {
          // add performed
          let id = '-1';
          if (this.uuid === undefined) {
            id = response.data._id;
          }
          else {
            id = this.uuid;
          }
          this.$router.push("/project/" + id + "/about");
        })
        .catch(() => {
          this.submitError = true;
        });
    },
  },
}
</script>

<style scoped>
.no-bullet {
    list-style-type: none;
}
</style>
