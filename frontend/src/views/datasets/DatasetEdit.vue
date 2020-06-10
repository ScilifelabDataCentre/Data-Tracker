<template>
<div class="dataset-edit">
  <form @submit="submitDatasetForm">
    <div class="field" v-if="newDataset.uuid !== ''">
      <label for="dataset-id" class="label">Dataset UUID</label>
      <div class="control">
        <input id="dataset-id"
               class="input"
               name="DATASET_ID"
               type="text"
               placeholder="uuid"
               v-model="newDataset.uuid"
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
      <textarea class="textarea"
		id="dataset-description"
		v-model="newDataset.description"
		name="DATASET_DESCRIPTION"
		type="text"
		placeholder="Dataset Description"
		rows="10">
      </textarea>
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

    <div class="columns">
      <div class="column">
        <div class="field">
          <label class="label">Extra fields</label>
          <div class="field is-grouped">
            <input id="dataset-extra-key"
                   class="input"
                   v-model="extraKey"
                   name="DATASET_EXTRA_KEY"
                   type="text"
                   placeholder="Key" />
            <input id="dataset-extra-value"
                   class="input"
                   v-model="extraValue"
                   name="DATASET_EXTRA_VALUE"
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
            <tr v-for="key in Object.keys(newDataset.extra)" :key="key">
              <td>{{key}}</td>
              <td>{{newDataset.extra[key]}}</td>
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
        <button class="button is-light" @click="cancelChanges">Cancel</button>
      </div>
      <div class="control">
        <button class="button is-danger" v-if="dataset.uuid && (user.role === 'Steward' || user.role === 'Admin')" @click="deleteDataset">Delete</button>
      </div>
    </div>
  </form>
</div>
</template>

<script>
import {mapGetters} from 'vuex';

export default {
  name: 'DatasetEdit',
  props: ['uuid'],
  components: {
  },
  computed: {
    ...mapGetters(['dataset', 'user']),
  },
  data () {
    return {
      newDataset: {
        uuid: '',
        title: '',
        description: '',
      },
      value: null,
    }
  },
  created () {
    this.$store.dispatch('getDataset', this.uuid)
      .then(() => {
        this.newDataset = this.dataset;
        this.newDataset.projects = this.newDataset.projects.join(' ')
      });
  },
  methods: {
    cancelChanges(event) {
      event.preventDefault();
      if (this.newDataset.id === '') {
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
      this.$store.dispatch('saveDataset', this.newDataset)
        .then((response) => {
          // add performed
          let uuid = '';
          if (response.data) {
            uuid = response.data.uuid;
          }
          else {
            uuid = this.newDataset.uuid
          }
          this.$router.push("/dataset/" + uuid + "/about");
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
