<template>
<div>
  <div class="row q-my-md">
    <q-input stack-label
             outlined
             label="New Tag Name"
             v-model="newTag"
             @keyup.enter="addTag"
             :rules="[ val => { val.length > 3 && val.trim() === val } ]"
             class="col-10">
      <template v-slot:append>
        <q-btn icon="fas fa-plus"
               dense
               round
               size="sm"
               :disable="disableButton"
               :color="disableButton ? 'grey' : 'positive'"
               @click="addTag" />
      </template>
      <template v-slot:hint>
        At least three characters, may not start nor end with whitespace characters.
      </template>
    </q-input>
  </div>
  <div class="flex q-ma-sm">
    <q-chip v-for="tag of value"
            :key="tag"
            square
            removable
            color="grey-3"
            @remove="deleteTag(tag)">
      <q-avatar color="secondary" text-color="white" icon="fas fa-tag" />
      {{ tag }}
    </q-chip>
  </div>
  <q-inner-loading :showing="isLoading">
    <q-spinner-gears size="100px" color="primary" />
  </q-inner-loading>
</div>
</template>

<script>
export default {
  name: 'TagEditor',

  computed: {
    disableButton: {
      get () {
        return this.newTag.length < 3 || this.newTag.trim() !== this.newTag;
      },
    }
  },
  
  props: {
    isLoading: {
      type: Boolean,
      default: false,
    },

    value: {
      type: Array,
      required: true,
    },
  },

  data () {
    return {
      newTag: '',
      tagExistsError: false,
    }
  },

  methods: {
    addTag() {
      this.tagExistsError = false;
      if (!this.value.includes(this.newTag)) {
        this.$emit('input', this.value.concat(this.newTag))
        this.newTag = '';
      }
      else
        this.tagExistsError = true;
    },

    deleteTag(tagName) {
      this.$emit('input', this.value.filter((entry) => entry !== tagName))
    },
  },
}
</script>
