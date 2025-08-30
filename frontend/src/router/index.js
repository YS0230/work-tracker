import { createRouter, createWebHistory } from 'vue-router'
import TaskList from '../views/TaskList.vue'
import CategoryManagement from '../views/CategoryManagement.vue'

const routes = [
  {
    path: '/',
    redirect: '/tasks'
  },
  {
    path: '/tasks',
    name: 'TaskList',
    component: TaskList
  },
  {
    path: '/categories',
    name: 'CategoryManagement',
    component: CategoryManagement
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router