/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Composables
import { createVuetify } from 'vuetify'
// Styles
import '@mdi/font/css/materialdesignicons.css'

import 'vuetify/styles'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: 'lightYellow',
    themes: {
      lightYellow: {
        dark: false,
        colors: {
          primary: '#F5E6D3',
          secondary: '#FDF8F0',
          accent: '#D9B48B',
          background: '#FDF7F0',
          surface: '#FFFFFF',
          error: '#E57373',
          info: '#64B5F6',
          success: '#81C784',
          warning: '#FFB74D',
        },
      },
    },
  },
})
