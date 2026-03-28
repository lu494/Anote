<template>
  <v-container>
    <!-- 用户信息卡片 -->
    <v-card class="mx-auto mt-8" max-width="600">
      <v-card-title class="text-h6 text-center">用户信息</v-card-title>
      <v-card-text>
        <v-text-field
          v-model="user.username"
          label="用户名"
          readonly
        />
        <v-text-field
          v-model="user.role"
          label="角色"
          readonly
        />
      </v-card-text>
    </v-card>

    <!-- 修改密码卡片 -->
    <v-card class="mx-auto mt-4" max-width="600">
      <v-card-title class="text-h6 text-center">修改密码</v-card-title>
      <v-card-text>
        <v-form ref="passwordForm">
          <v-text-field
            v-model="form.oldPassword"
            label="旧密码"
            required
            :rules="[rules.required]"
            type="password"
          />
          <v-text-field
            v-model="form.newPassword"
            label="新密码"
            required
            :rules="[rules.required, rules.password]"
            type="password"
          />
          <v-text-field
            v-model="form.confirmPassword"
            label="确认新密码"
            required
            :rules="[rules.required, rules.confirmPassword]"
            type="password"
          />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn block color="primary" @click="onSubmit">修改密码</v-btn>
      </v-card-actions>
    </v-card>

    <!-- 顶部提示 -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      elevation="2"
      location="top"
      rounded
      timeout="3000"
    >
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
  import { onMounted, reactive, ref } from 'vue'
  import axios from '@/plugins/axios'

  interface User {
    username: string
    role: string
  }

  const user = ref<User>({ username: '', role: '' })
  const form = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
  const snackbar = reactive({ show: false, message: '', color: 'success' })
  const passwordForm = ref()

  const rules = {
    required: (v: string) => !!v || '此项为必填',
    password: (v: string) => v.length >= 6 || '密码至少6位',
    confirmPassword: (v: string) => v === form.newPassword || '两次输入的密码不一致',
  }

  function showMessage (message: string, color = 'success') {
    snackbar.message = message
    snackbar.color = color
    snackbar.show = true
  }

  async function loadUser () {
    try {
      const res = await axios.get('/user/me')
      if (res.data.code === 0) user.value = res.data.data
      else showMessage(res.data.msg, 'error')
    } catch (error: any) {
      showMessage(error.response?.data?.msg || '获取用户信息失败', 'error')
    }
  }

  async function onSubmit () {
    if (!passwordForm.value?.validate?.()) return
    try {
      const res = await axios.post('/user/changePassword', {
        oldPassword: form.oldPassword,
        newPassword: form.newPassword,
      })
      if (res.data.code === 0) {
        showMessage('密码修改成功', 'success')
        form.oldPassword = ''
        form.newPassword = ''
        form.confirmPassword = ''
      } else {
        showMessage(res.data.msg, 'error')
      }
    } catch (error: any) {
      showMessage(error.response?.data?.msg || '修改密码失败', 'error')
    }
  }

  onMounted(loadUser)
</script>

<style scoped>
.v-card { padding: 16px; }
</style>
