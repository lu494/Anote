// stores/user.ts
import { defineStore } from 'pinia'
import axios from '@/plugins/axios'

interface User {
  id: number
  username: string
  role: string
}

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as User | null,
  }),
  actions: {
    async loadUser () {
      const token = localStorage.getItem('token')
      if (!token) {
        this.user = null
        delete axios.defaults.headers.common['Authorization']
        return
      }
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      try {
        const res = await axios.get('/user/me')
        this.user = res.data.code === 0 ? res.data.data : null
      } catch {
        this.user = null
      }
    },
    logout () {
      axios.post('/user/logout').finally(() => {
        localStorage.removeItem('token')
        this.user = null
      })
    },
  },
})
