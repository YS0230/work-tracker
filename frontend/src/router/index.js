import { createRouter, createWebHistory } from 'vue-router'
import TaskDashboard from '../views/TaskDashboard.vue'
import WorkDashboard from '../views/WorkDashboard.vue'
import TaskList from '../views/TaskList.vue'
import CategoryManagement from '../views/CategoryManagement.vue'
import WorkLog from '../views/WorkLog.vue'

const routes = [
  {
    path: '/',
    redirect: '/work-logs'
  },
  {
    path: '/task-dashboard',
    name: 'TaskDashboard',
    component: TaskDashboard
  },
  {
    path: '/work-dashboard',
    name: 'WorkDashboard',
    component: WorkDashboard
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