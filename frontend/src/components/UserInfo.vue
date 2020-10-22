<template>
<q-list>
  <user-entry v-for="entry in entries" :key="entry._id" v-bind="entry" />
</q-list>
</template>

<script>
import UserEntry from 'components/UserEntry.vue'

export default {
  name: 'UserInfo',

  components: {'user-entry': UserEntry},
  
  props: {
    entries: {
      type: Object,
      required: true,
    },
  },

  data () {
    return {}
  }
}
</script>
