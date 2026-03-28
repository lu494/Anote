<template>
  <v-form ref="formRef" @submit.prevent="onSubmit">
    <v-text-field
      v-model="form.title"
      label="标题"
      :rules="[rules.required]"
    />
    <v-textarea
      v-model="form.content"
      label="内容"
      rows="10"
      :rules="[rules.required]"
    />
    <v-text-field
      v-model="form.category"
      label="分类"
    />
    <v-text-field
      v-model="form.tags"
      label="标签(逗号分隔)"
    />
    <v-btn class="mt-4" color="primary" type="submit">
      {{ submitText }}
    </v-btn>
  </v-form>
</template>

<script setup lang="ts">
  import { ref, watch } from 'vue'

  interface FormData {
    title: string
    content: string
    category: string
    tags: string
  }

  const props = defineProps<{
    modelValue: FormData
    submitText?: string
  }>()

  const emit = defineEmits<{
    (e: 'submit', data: FormData): void
  }>()

  const formRef = ref()
  const form = ref({ ...props.modelValue })

  watch(
    () => props.modelValue,
    val => {
      form.value = { ...val }
    },
  )

  const rules = {
    required: (v: string) => !!v || '此项为必填',
  }

  function onSubmit () {
    emit('submit', { ...form.value })
  }
</script>

<style scoped>
.mt-4 {
  margin-top: 16px;
}
</style>
