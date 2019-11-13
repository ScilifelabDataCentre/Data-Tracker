<template>
<div class="dataset-edit">
  <form @submit="submitDatasetForm">
    <div class="field" v-if="newDataset.id !== -1">
      <label for="dataset-id" class="label">Dataset ID</label>
      <div class="control">
        <input id="dataset-id"
               class="input"
               name="DATASET_ID"
               type="text"
               placeholder="id"
               v-model="newDataset.id"
               disabled="true"/>
      </div>
    </div>
    <div class="field">
      <label class="label" for="dataset-title">Title</label>
      <input id="dataset-title"
             class="input"
             name="DATASET_TITLE"
             type="text"
             placeholder="Title"
             v-model="newDataset.title"/>
    </div>
    <div class="field">
      <label class="label" for="dataset-description">Description</label>
      <input id="dataset-description"
             class="input"
             v-model="newDataset.description"
             name="DATASET_DESCRIPTION"
             type="text"
             placeholder="Description" />
    </div>
    <div class="field">
      <label class="label" for="dataset-creator">Dataset creator</label>
      <input id="dataset-creator"
             class="input"
             v-model="newDataset.creator"
             name="DATASET_CREATOR"
             type="text"
             placeholder="Dataset creator" />
    </div>
    <div class="field">
      <label class="label" for="dataset-projects">Project IDs</label>
      <input id="dataset-projects"
             class="input"
             v-model="newDataset.projects"
             name="DATASET_PROJECTS"
             type="text"
             placeholder="Project IDs" />
    </div>
    <div class="field is-grouped">
      <div class="control">
        <button class="button is-link">Submit</button>
      </div>
      <div class="control">
        <button class="button is-light" @click="cancelChanges">Cancel</button>
      </div>
      <div class="control">
        <button class="button is-danger" v-if="newDataset.id != -1 && (user.permission === 'Steward' || user.permission === 'Admin')" @click="deleteDataset">Delete</button>
      </div>
    </div>
  </form>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'DatasetEdit',
  props: ['id'],
  components: {
  },
  computed: {
    ...mapGetters(['dataset', 'user']),
  },
  data () {
    return {
      newDataset: {
        id: -1,
        title: '',
        description: '',
        contact: '',
        projects: [],
      },
      value: null,
    }
  },
  created () {
    this.$store.dispatch('getDataset', this.id)
      .then(() => {
        this.newDataset = this.dataset;
        this.newDataset.projects = this.newDataset.projects.join(' ')
      });
  },
  methods: {
    cancelChanges(event) {
      event.preventDefault();
      if (this.newDataset.id === -1) {
        this.$router.push("/dataset/browser");
      }
      else {
        this.$router.push("/dataset/" + this.newDataset.id + "/about");
      }
    },
    deleteDataset(event) {
      event.preventDefault();
      this.$store.dispatch('deleteDataset', this.newDataset.id)
        .then(() => {
          this.$router.push("/dataset/browser");
        });
    },
    submitDatasetForm(event) {
      event.preventDefault();
      this.newDataset.projects = this.newDataset.projects.split(' ');
      this.$store.dispatch('saveDataset', this.newDataset)
        .then((response) => {
          // add performed
          let id = -1;
          if (response.data) {
            id = response.data.id;
          }
          else {
            id = this.newDataset.id
          }
          this.$router.push("/dataset/" + id + "/about");
        });
    },
  },
}
</script>

<style scoped>
.dataset-title {
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
