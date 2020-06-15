<template>
<div class="dataset-edit">
  <form @submit="submitDatasetForm">
    <div class="field" v-if="newDataset.id !== '-1'">
      <label for="dataset-id" class="label">Dataset UUID</label>
      <div class="control">
        <input id="dataset-id"
               class="input"
               name="DATASET_ID"
               type="text"
               placeholder="uuid"
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
      <textarea class="textarea"
                id="dataset-description"
                v-model="newDataset.description"
                name="DATASET_DESCRIPTION"
                type="text"
                placeholder="Dataset Description"
                rows="10">
      </textarea>
    </div>

    <div class="columns">
      <div class="column">
        <div class="field">
          <label class="label">Links</label>
          <div class="field has-addons">
            <div class="control">
              <input id="dataset-link-key"
                     class="input"
                     v-model="linkDesc"
                     name="DATASET_LINK_KEY"
                     type="text"
                     placeholder="Link description" />
            </div>
            <div class="control">
              <input id="dataset-link-value"
                     class="input"
                     v-model="linkUrl"
                     name="DATASET_LINK_VALUE"
                     type="text"
                     placeholder="https://link.url" />
            </div>
            <div class="control">
              <button class="button is-light" @click="addLink">Save</button>
            </div>
          </div>
        </div>
      </div>
      <div class="column">
        <ul>
          <li class="nobullet" href="#" v-for="(entry, i) in newDataset.links" :key="i">
            <div class="tag is-light">{{ entry.description }}: {{ entry.url }}<button class="delete" href="#" @click="deleteLink($event, i)"></button></div>
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
              <input id="dataset-extra-key"
                     class="input"
                     v-model="extraKey"
                     name="DATASET_EXTRA_KEY"
                     type="text"
                     placeholder="Key" />
            </div>
            <div class="control">
              <input id="dataset-extra-value"
                   class="input"
                   v-model="extraValue"
                   name="DATASET_EXTRA_VALUE"
                   type="text"
                     placeholder="Value" />
            </div>
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
        <button class="button is-link" @click="submitDatasetForm">Submit</button>
      </div>
      <div class="control">
        <button class="button is-light" @click="cancelChanges">Cancel</button>
      </div>
      <div class="control">
        <button class="button is-danger" v-if="user.permissions.includes('DATA_MANAGEMENT') || fullPermissions" @click="deleteDataset">Delete</button>
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
        id: '-1',
        title: '',
        description: '',
        links: [],
        extra: {},
      },
      fullPermissions: false,
      extraKey: '',
      extraValue: '',
      linkDesc: '',
      linkUrl: '',
    }
  },

  mounted () {
    this.$store.dispatch('getDataset', this.uuid)
      .then(() => {
        this.newDataset = this.dataset;
        this.newDataset.id = this.newDataset._id;
        delete this.newDataset._id;
        delete this.newDataset.related;
        delete this.newDataset.projects;
        if (this.newDataset.creator === this.user.name) {
          this.fullPermissions = true;
        }
        delete this.newDataset.creator;
      });
  },

  methods: {
    saveExtra(event) {
      event.preventDefault();
      if (this.extraKey !== '') {
        if (this.newDataset.extra[this.extraKey] !== undefined) {
          if (this.extraValue === '') {
            this.$delete(this.newDataset.extra, this.extraKey);
          }
          else {
            this.newDataset.extra[this.extraKey] = this.extraValue;
          }
        }
        else {
          if (this.extraValue !== '') {
            this.$set(this.newDataset.extra, this.extraKey, this.extraValue);
          }
        }
      }
    },

    addLink(event) {
      event.preventDefault();
      this.newDataset.links.push({'description': this.linkDesc,
                                  'url': this.linkUrl});
      this.linkDesc = '';
      this.linkUrl = '';
    },

    deleteLink(event, position) {
      event.preventDefault();
      this.newDataset.links.splice(position, 1);
    },
    
    cancelChanges(event) {
      event.preventDefault();
      this.$router.push("/dataset/" + this.newDataset.id + "/about");
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
        .then(() => {
          this.$router.push("/dataset/" + this.uuid + "/about");
        });
    },
  },
}
</script>
