<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row justify="center">
          <v-col cols="12" md="8">
            <v-card v-if="note">
              <v-card-title>{{ note.title }}</v-card-title>
              <v-card-subtitle v-if="note.category">
                分类: {{ note.category }}
              </v-card-subtitle>
              <v-card-text>
                <NoteContent :content="note.content" />
              </v-card-text>
            </v-card>

            <v-alert v-else-if="!loading" dense type="error">
              无效的分享链接或笔记不存在
            </v-alert>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
  import { onMounted, ref } from 'vue'
  import { useRoute } from 'vue-router'
  import NoteContent from '@/components/NoteContent.vue'
  import axios from '@/plugins/axios'

  interface NoteDetail {
    title: string
    content: string
    category?: string
    tags: string[]
  }

  const route = useRoute()
  const token = (route.params as { token?: string }).token || ''
  const note = ref<NoteDetail | null>(null)
  const snackbar = ref({ show: false, message: '', color: 'success' })
  const loading = ref(true)

  async function loadSharedNote () {
    if (!token) {
      showSnackbar('分享链接无效', 'error')
      loading.value = false
      return
    }
    try {
      const res = await axios.get('/share/view', { params: { token } })
      if (res.data.code === 0 && res.data.data) {
        note.value = res.data.data
      } else {
        note.value = null
        showSnackbar(res.data.msg || '笔记不存在', 'error')
      }
    } catch (error: any) {
      note.value = null
      showSnackbar(error.response?.data?.msg || '加载失败', 'error')
    } finally {
      loading.value = false
    }
  }

  function showSnackbar (message: string, color = 'success') {
    snackbar.value = { show: true, message, color }
  }

  onMounted(() => {
    loadSharedNote()
  })
</script>
