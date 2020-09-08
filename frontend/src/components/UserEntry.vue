<template>
<q-item>
  <q-item-section avatar>

    <q-btn v-if="entry.email.length > 0"
           flat
           round
           dense
           icon="email"
           type="a"
           :href="'mailto:' + entry.email" />
  </q-item-section>
  <q-item-section>
    <q-item-label>
      {{ entry.name }}
    </q-item-label>
    <q-item-label caption>
      {{ entry.email }}
    </q-item-label>
  </q-item-section>
</q-item>
</template>

<script>
export default {
  name: 'UserEntry',
  props: {
    entry: {
      type: Object,
      required: true
    },
  }
}
</script>
