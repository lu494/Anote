import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNoteStore = defineStore('note', () => {
  const selectedCategory = ref('')

  function setCategory (cat: string) {
    selectedCategory.value = cat
  }

  return { selectedCategory, setCategory }
})
