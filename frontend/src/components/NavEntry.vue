<template>
  <q-item clickable
          :to="link">
    <q-item-section v-if="icon.length > 0"
                    avatar>
      <q-icon :name="icon" />
    </q-item-section>

    <q-item-section>
      <q-item-label>
        {{ title }}
      </q-item-label>
      <q-item-label caption>
        {{ caption }}
      </q-item-label>
    </q-item-section>
  </q-item>
</template>

<script>
export default {
  name: 'NavEntry',
  props: {
    title: {
      type: String,
      required: true
    },

    caption: {
      type: String,
      default: ''
    },

    link: {
      default: '#'
    },

    icon: {
      type: String,
      default: ''
    }
  }
}
</script>
