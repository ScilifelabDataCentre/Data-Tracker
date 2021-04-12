<template>
<div>
  <div class="q-my-md">
    <q-input stack-label
             outlined
             label="New Tag Name"
             v-model="newTag"
             @keyup.enter="addTag"
             :rules="[ function (val) { return (evaluateTag(val) || val.length === 0) || 'At least three characters, no whitespace at beginning nor end.' }]">
      <template v-slot:append>
        <q-btn icon="fas fa-plus"
               dense
               round
               size="sm"
               v-show="enableAdd"
               color="positive"
               @click="addTag" />
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
    enableAdd: {
      get () {
        return this.evaluateTag(this.newTag);
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
    evaluateTag (val) {
      return (val.length >= 3 && val.trim() === val);
    },

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
