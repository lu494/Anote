<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="10">
        <!-- 搜索栏 -->
        <v-text-field
          v-model="keyword"
          class="mb-4"
          clearable
          label="搜索用户名"
          prepend-icon="mdi-magnify"
          @keyup.enter="loadUsers"
        >
          <template #append>
            <v-btn color="primary" @click="loadUsers">搜索</v-btn>
          </template>
        </v-text-field>

        <!-- 用户列表 -->
        <v-card>
          <v-data-table
            class="elevation-1"
            :headers="headers"
            item-value="id"
            :items="users"
            :items-per-page="10"
          >
            <template #item.actions="{ item }">
              <v-btn
                color="error"
                :disabled="item.role === 'admin' && otherUsersExist(item.id)"
                icon
                :title="item.role === 'admin' && otherUsersExist(item.id) ? '不能删除管理员' : ''"
                @click="deleteUser(item)"
              >
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
  import axios from '@/plugins/axios'

  interface UserItem {
    id: number
    username: string
    role: string
  }

  const keyword = ref('')
  const users = ref<UserItem[]>([])
  const snackbar = ref({ show: false, message: '', color: 'success' })
  const headers = [
    { title: 'ID', key: 'id', width: '80px', align: 'start' as const },
    { title: '用户名', key: 'username', align: 'start' as const },
    { title: '角色', key: 'role', width: '120px', align: 'start' as const },
    { title: '操作', key: 'actions', sortable: false, width: '100px', align: 'center' as const },
  ]

  function showSnackbar (message: string, color = 'success') {
    snackbar.value = { show: true, message, color }
  }

  async function loadUsers () {
    try {
      const res = await axios.get('/admin/users', { params: { keyword: keyword.value } })
      if (res.data.code === 0) users.value = res.data.data.users
      else showSnackbar(res.data.msg, 'error')
    } catch (error: any) {
      showSnackbar(error.response?.data?.msg || '获取用户列表失败', 'error')
    }
  }

  function otherUsersExist (userId: number) {
    return users.value.some(u => u.id !== userId)
  }

  async function deleteUser (user: UserItem) {
    if (!confirm(`确定要删除用户 ${user.username} 吗？`)) return
    try {
      const res = await axios.post('/admin/user/delete', { userId: user.id })
      if (res.data.code === 0) {
        showSnackbar('删除成功', 'success')
        loadUsers()
      } else showSnackbar(res.data.msg, 'error')
    } catch (error: any) {
      showSnackbar(error.response?.data?.msg || '删除失败', 'error')
    }
  }

  onMounted(loadUsers)
</script>

<style scoped>
.v-card { padding: 16px; }
</style>
