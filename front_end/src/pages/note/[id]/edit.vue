<template>
  <v-app>
    <v-main>
      <v-container>
        <NoteForm
          v-if="note"
          :model-value="form"
          submit-text="保存修改"
          @submit="onSubmit"
        />

        <div v-else class="d-flex justify-center align-center" style="height:100vh;">
          <v-progress-circular color="primary" indeterminate size="64" />
        </div>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
  import { onMounted, reactive, ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import NoteForm from '@/components/NoteForm.vue'
  import axios from '@/plugins/axios'

  interface NoteDetail {
    noteId: number
    title: string
    content: string
    category?: string
    tags: string[]
  }

  const route = useRoute()
  const router = useRouter()
  const noteId = Number((route.params as { id: string }).id)

  const note = ref<NoteDetail | null>(null)
  const form = reactive({ title: '', content: '', category: '', tags: '' })

  const token = localStorage.getItem('token')
  if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

  async function loadNote () {
    try {
      const res = await axios.get('/note/detail', { params: { noteId } })
      if (res.data.code === 0) {
        note.value = res.data.data

        form.title = note.value!.title
        form.content = note.value!.content
        form.category = note.value!.category || ''
        form.tags = note.value!.tags.join(',')
      } else {
        router.push('/')
      }
    } catch {
      router.push('/')
    }
  }

  async function onSubmit (data: typeof form) {
    try {
      const payload = {
        noteId,
        ...data,
        tags: data.tags.split(',').map(t => t.trim()).filter(Boolean),
      }
      const res = await axios.post('/note/update', payload)
      if (res.data.code === 0) router.push(`/note/${noteId}`)
      else alert(res.data.msg)
    } catch (error: any) {
      alert(error.response?.data?.msg || '保存失败')
    }
  }

  onMounted(() => {
    loadNote()
    // 页面加载时自动滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' })
  })
</script>
