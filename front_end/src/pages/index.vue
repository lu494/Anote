<template>
  <v-container>
    <!-- 搜索栏 -->
    <v-row class="mb-4" justify="center">
      <v-col cols="12" md="12">
        <v-text-field
          v-model="keyword"
          clearable
          label="搜索笔记标题"
          prepend-icon="mdi-magnify"
          @keyup.enter="loadNotes"
        >
          <template #append>
            <v-btn color="primary" @click="loadNotes">搜索</v-btn>
          </template>
        </v-text-field>
      </v-col>
    </v-row>

    <v-row dense>
      <!-- 创建笔记卡片 -->
      <v-col cols="12" md="4">
        <v-card class="hover-card create-card" @click="createNote">
          <v-card-title class="justify-center">+ 创建笔记</v-card-title>
        </v-card>
      </v-col>

      <!-- 搜索结果笔记卡片 -->
      <template v-if="notesFiltered.length > 0">
        <v-col v-for="note in notesFiltered" :key="note.noteId" cols="12" md="4">
          <v-card class="hover-card note-card" @click="openNote(note.noteId)">
            <v-card-title class="title-text">{{ note.title }}</v-card-title>
            <v-card-text class="content-text">
              {{ note.content ? (note.content.length > 60 ? note.content.slice(0, 60) + '...' : note.content) : '' }}
            </v-card-text>
          </v-card>
        </v-col>
      </template>

      <!-- 无笔记提示卡片 -->
      <template v-else>
        <v-col cols="12" md="4">
          <v-card class="hover-card no-note-card">
            <v-card-title class="justify-center">暂无笔记</v-card-title>
          </v-card>
        </v-col>
      </template>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
  import { computed, onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import axios from '@/plugins/axios'
  import { useNoteStore } from '@/stores/note'

  interface Note {
    noteId: number
    title: string
    category?: string
    tags: string[]
    content?: string
  }

  const noteStore = useNoteStore()
  const router = useRouter()
  const notes = ref<Note[]>([])
  const loadingNotes = ref(true)
  const keyword = ref('')

  const token = localStorage.getItem('token')
  if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

  async function loadNotes () {
    loadingNotes.value = true
    try {
      const res = await axios.get('/note/list', { params: { keyword: keyword.value } })
      if (res.data.code === 0) {
        notes.value = res.data.data.notes.map((n: any) => ({ ...n, content: '' }))
        await Promise.all(
          notes.value.map(async (note: Note) => {
            try {
              const detailRes = await axios.get('/note/detail', {
                params: { noteId: note.noteId },
              })
              if (detailRes.data.code === 0) note.content = detailRes.data.data.content
            } catch {}
          }),
        )
      }
    } finally {
      loadingNotes.value = false
    }
  }

  const notesFiltered = computed(() => {
    return notes.value.filter(n => {
      const matchesCategory = !noteStore.selectedCategory || n.category === noteStore.selectedCategory
      const matchesKeyword = !keyword.value || n.title.includes(keyword.value)
      return matchesCategory && matchesKeyword
    })
  })

  function openNote (id: number) {
    router.push(`/note/${id}`)
  }

  function createNote () {
    router.push('/note/create')
  }

  onMounted(() => {
    loadNotes()
  })
</script>

<style scoped>
.hover-card {
  min-height: 150px;
  transition: 0.2s;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: stretch;
}
.hover-card:hover {
  transform: translateY(-4px);
}
.create-card {
  font-weight: bold;
  font-size: 18px;
  color: #1976d2;
  border: 2px dashed #1976d2;
  justify-content: center;
  text-align: center;
}
.note-card {
  padding: 8px;
}
.no-note-card {
  font-weight: bold;
  font-size: 16px;
  color: #999;
  border: 1px dashed #ccc;
  justify-content: center;
  text-align: center;
}
.title-text {
  text-align: left;
  font-weight: 600;
  font-size: 16px;
}
.content-text {
  text-align: left;
  font-size: 14px;
  color: #555;
}
.v-card-title.justify-center {
  justify-content: center;
}
</style>
