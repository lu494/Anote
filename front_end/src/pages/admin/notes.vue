<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="12">
        <!-- 搜索栏 -->
        <v-text-field
          v-model="keyword"
          class="mb-4"
          clearable
          label="搜索笔记标题"
          prepend-icon="mdi-magnify"
          @keyup.enter="loadNotes"
        >
          <template #append>
            <v-btn color="primary" @click="loadNotes">搜索</v-btn>
          </template>
        </v-text-field>

        <!-- 笔记列表 -->
        <v-card>
          <v-data-table
            class="elevation-1"
            :headers="headers"
            item-value="noteId"
            :items="notes"
            :items-per-page="10"
          >
            <template #item.view="{ item }">
              <v-btn color="primary" icon @click="viewNote(item)">
                <v-icon>mdi-eye</v-icon>
              </v-btn>
            </template>
            <template #item.delete="{ item }">
              <v-btn color="error" icon @click="deleteNote(item)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-card>

        <!-- 顶部提示 -->
        <v-snackbar
          v-model="snackbar.show"
          :color="snackbar.color"
          timeout="3000"
          top
        >
          {{ snackbar.message }}
        </v-snackbar>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
  import { onMounted, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import axios from '@/plugins/axios'

  interface NoteItem {
    noteId: number
    title: string
    owner: string
  }

  const router = useRouter()
  const keyword = ref('')
  const notes = ref<NoteItem[]>([])
  const snackbar = ref({ show: false, message: '', color: 'success' })
  const headers = [
    { title: 'ID', key: 'noteId', width: '80px', align: 'start' as const },
    { title: '标题', key: 'title', align: 'start' as const },
    { title: '用户', key: 'owner', width: '150px', align: 'start' as const },
    { title: '查看', key: 'view', width: '80px', sortable: false, align: 'center' as const },
    { title: '删除', key: 'delete', width: '80px', sortable: false, align: 'center' as const },
  ]

  function showSnackbar (message: string, color = 'success') {
    snackbar.value = { show: true, message, color }
  }

  async function loadNotes () {
    try {
      const res = await axios.get('/admin/notes', { params: { keyword: keyword.value } })
      if (res.data.code === 0) notes.value = res.data.data.notes
      else showSnackbar(res.data.msg, 'error')
    } catch (error: any) {
      showSnackbar(error.response?.data?.msg || '获取笔记列表失败', 'error')
    }
  }

  function viewNote (note: NoteItem) {
    router.push(`/note/${note.noteId}`)
  }

  async function deleteNote (note: NoteItem) {
    if (!confirm(`确定要删除笔记 "${note.title}" 吗？`)) return
    try {
      const res = await axios.post('/admin/note/delete', { noteId: note.noteId })
      if (res.data.code === 0) {
        showSnackbar('删除成功', 'success')
        loadNotes()
      } else showSnackbar(res.data.msg, 'error')
    } catch (error: any) {
      showSnackbar(error.response?.data?.msg || '删除失败', 'error')
    }
  }

  onMounted(loadNotes)
</script>

<style scoped>
.v-card { padding: 16px; }
</style>
