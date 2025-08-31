import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router'
import App from './App.vue'
import vDebounce from './directives/debounce.js'

const app = createApp(App)

app.use(ElementPlus)
app.use(router)

// 註冊防連點指令
app.directive('debounce', vDebounce)

app.mount('#app')