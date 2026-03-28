<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" md="4" sm="8">
        <v-card>
          <v-card-title class="text-h5 text-center">登录</v-card-title>
          <v-card-text>
            <v-form ref="loginForm">
              <v-text-field
                v-model="form.username"
                label="用户名"
                prepend-icon="mdi-account"
                :rules="[rules.required]"
              />
              <v-text-field
                v-model="form.password"
                label="密码"
                prepend-icon="mdi-lock"
                :rules="[rules.required]"
                type="password"
              />
              <v-btn
                block
                class="mt-4"
                color="primary"
                @click="onSubmit"
              >登录</v-btn>
            </v-form>
            <div class="mt-5 text-center">
              没有账号？<span class="link-text" @click="goRegister">去注册</span>
            </div>
          </v-card-text>
        </v-card>

        <!-- 顶部弹窗 -->
        <v-snackbar
          v-model="snackbar.show"
          :color="snackbar.color"
          elevation="2"
          location="top"
          rounded
          timeout="2000"
        >
          {{ snackbar.message }}
        </v-snackbar>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
  import { defineComponent, reactive, ref } from 'vue'
  import { useRouter } from 'vue-router'
  import request from '@/plugins/axios'

  export default defineComponent({
    setup () {
      const router = useRouter()
      const loginForm = ref()
      const form = reactive({ username: '', password: '' })
      const snackbar = reactive({ show: false, message: '', color: 'success' })

      const rules = {
        required: (v: string) => !!v || '此项为必填',
      }

      const showSnackbar = (message: string, color = 'success') => {
        snackbar.message = message
        snackbar.color = color
        snackbar.show = true
      }

      const onSubmit = async () => {
        if (!loginForm.value?.validate?.()) return
        try {
          const res = await request.post('/user/login', {
            username: form.username,
            password: form.password,
          })
          if (res.data.code === 0) {
            const token = res.data.data.token
            localStorage.setItem('token', token)
            // 手动触发自定义事件，让 NavDrawer 更新用户信息
            window.dispatchEvent(new Event('login-success'))
            showSnackbar('登录成功，正在跳转首页', 'success')
            setTimeout(() => router.push('/'), 1000)
          } else {
            showSnackbar(res.data.msg, 'error')
          }
        } catch (error: any) {
          showSnackbar(error.response?.data?.msg || '登录失败', 'error')
        }
      }

      const goRegister = () => {
        router.push('/register')
      }

      return { form, rules, loginForm, onSubmit, goRegister, snackbar }
    },
  })
</script>

<style scoped>
.link-text { color: #1976d2; cursor: pointer; text-decoration: underline; }
</style>
