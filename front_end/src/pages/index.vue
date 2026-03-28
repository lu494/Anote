<template>
  <v-container>
    <!-- 搜索栏（支持全文搜索） -->
    <v-row class="mb-4" justify="center">
      <v-col cols="12" md="12">
        <v-text-field
          v-model="keyword"
          clearable
          label="搜索笔记（标题/内容）"
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

      <!-- 笔记卡片列表 -->
      <template v-if="notesFiltered.length > 0">
        <v-col v-for="note in notesFiltered" :key="note.noteId" cols="12" md="4">
          <v-card class="hover-card note-card">
            <v-card-title class="title-text" @click="openNote(note.noteId)">{{ note.title }}</v-card-title>
            <v-card-text class="content-text" @click="openNote(note.noteId)">
              {{ note.content ? (note.content.length > 60 ? note.content.slice(0, 60) + '...' : note.content) : '' }}
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn icon @click.stop="exportNote(note.noteId)">
                <v-icon>mdi-download</v-icon>
              </v-btn>
            </v-card-actions>
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
      return matchesCategory
    })
  })

  function openNote (id: number) {
    router.push(`/note/${id}`)
  }

  function createNote () {
    router.push('/note/create')
  }

  // 导出笔记为 PDF
  async function exportNote (id: number) {
    try {
      const response = await axios.get('/note/export', {
        params: { noteId: id, format: 'pdf' },
        responseType: 'blob',   // 重要：以二进制流接收
      })
      // 从响应头获取文件名，如果不存在则构造
      const contentDisposition = response.headers['content-disposition']
      let filename = `note_${id}.pdf`
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?(.+)"?/)
        if (match) filename = match[1]
      }
      // 创建下载链接并触发点击
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error: any) {
      console.error('导出失败', error)
      // 如果后端返回 JSON 错误，尝试解析
      if (error.response && error.response.data) {
        try {
          // 注意：如果响应是 JSON，但 responseType 是 blob，需要先转为文本
          const text = await error.response.data.text()
          const errJson = JSON.parse(text)
          alert(errJson.msg || '导出失败')
        } catch {
          alert('导出失败')
        }
      } else {
        alert('导出失败')
      }
    }
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
  cursor: default; /* 卡片本身不设置手型，内部标题和内容区域单独设置 */
}
.note-card .title-text,
.note-card .content-text {
  cursor: pointer;
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
.v-card-actions {
  justify-content: flex-end;
}
</style>