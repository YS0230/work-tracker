import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import TaskList from '../views/TaskList.vue'
import CategoryManagement from '../views/CategoryManagement.vue'
import WorkLog from '../views/WorkLog.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
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
  },
  {
    path: '/work-logs',
    name: 'WorkLog',
    component: WorkLog
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router