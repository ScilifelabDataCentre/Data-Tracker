<template>
<div>
  <div class="q-my-md">
    <q-input stack-label
             outlined
             label="New Tag Name"
             v-model="newTag"
             @keyup.enter="addTag"
             :rules="[ function (val) { return (evaluateTag(val) || val.length === 0) || 'Must contain at least 3 characters, no whitespace at beginning nor end, and must not already exist.' }]">
      <template v-slot:after>
        <q-btn icon="fas fa-plus"
               dense
               rounded
               size="md"
               :disabled="!enableAdd"
               color="positive"
               @click="addTag" />
      </template>
    </q-input>
  </div>
  <div class="flex q-ma-sm">
    <q-chip v-for="tag of modelValue"
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

    modelValue: {
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

  emits: ['update:modelValue'],
  methods: {
    evaluateTag (val) {
      return (val.length >= 3 && val.trim() === val && !this.modelValue.includes(this.newTag));
    },

    addTag() {
      if (this.enableAdd) {
        this.tagExistsError = false;
        if (!this.modelValue.includes(this.newTag)) {
          this.$emit('update:modelValue', this.modelValue.concat(this.newTag))
          this.newTag = '';
        }
        else
          this.tagExistsError = true;
      }
    },

    deleteTag(tagName) {
      this.$emit('update:modelValue', this.modelValue.filter((entry) => entry !== tagName))
    },
  },
}
</script>
