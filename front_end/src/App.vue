<template>
  <v-app>
    <NavDrawer app :title="title" />

    <v-main class="pt-0">
      <router-view />
      <v-btn
        v-show="showBackTop"
        class="fab-top"
        color="primary"
        icon
        @click="scrollTop"
      >
        <v-icon>mdi-arrow-up</v-icon>
      </v-btn>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
  import { onMounted, onUnmounted, ref, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import NavDrawer from '@/components/NavDrawer.vue'
  import axios from '@/plugins/axios'

  const route = useRoute()
  const router = useRouter()
  const title = ref('')

  // 动态更新导航栏标题
  function updateTitle () {
    const path = route.path
    if (/^\/login(\/)?$/.test(path)) title.value = '登录'
    else if (/^\/register(\/)?$/.test(path)) title.value = '注册'
    else if (/^\/note\/create(\/)?$/.test(path)) title.value = '创建笔记'
    else if (/^\/note\/\d+\/edit(\/)?$/.test(path)) title.value = '编辑笔记'
    else if (/^\/note\/\d+(\/)?$/.test(path)) title.value = '笔记详情'
    else if (/^\/share(\/.*)?$/.test(path)) title.value = '笔记详情'
    else if (/^\/user(\/)?$/.test(path)) title.value = '用户设置'
    else if (/^\/admin\/users(\/)?$/.test(path)) title.value = '用户管理'
    else if (/^\/admin\/notes(\/)?$/.test(path)) title.value = '笔记管理'
    else title.value = ''
  }

  watch(
    () => route.fullPath,
    () => updateTitle(),
    { immediate: true },
  )

  // 回到顶部按钮
  const showBackTop = ref(false)
  function onScroll () {
    showBackTop.value = window.scrollY > 300
  }
  function scrollTop () {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  async function checkLogin () {
    const token = localStorage.getItem('token')
    const publicPaths = [/^\/login(\/)?$/, /^\/register(\/)?$/, /^\/share(\/.*)?$/]
    const isPublic = publicPaths.some(p => p.test(route.path))

    if (!token) {
      if (!isPublic) router.replace('/login')
      return
    }

    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
    try {
      const res = await axios.get('/user/me')
      if (res.data.code !== 0) {
        localStorage.removeItem('token')
        if (!isPublic) router.replace('/login')
      }
    } catch {
      localStorage.removeItem('token')
      if (!isPublic) router.replace('/login')
    }
  }

  // 在 mounted 时等待路由准备好后再检查登录，避免首次渲染时因为路由未就绪导致误跳转
  onMounted(async () => {
    await router.isReady()
    window.addEventListener('scroll', onScroll)
    // 首次检查
    checkLogin()
  })

  // 每次路由变化也检查一次登录（例如用户手动在别处登录后跳转）
  watch(
    () => route.fullPath,
    () => {
      checkLogin()
    },
  )

  onUnmounted(() => {
    window.removeEventListener('scroll', onScroll)
  })
</script>

<style scoped>
.fab-top {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 1000;
}
</style>
