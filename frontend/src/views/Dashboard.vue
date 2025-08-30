<template>
  <div>
    <!-- 總覽卡片區域 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card class="status-card pending">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="32"><Clock /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-number">{{ stats.pendingTasks }}</div>
              <div class="card-label">待處理任務</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="status-card in-progress">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="32"><Loading /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-number">{{ stats.inProgressTasks }}</div>
              <div class="card-label">進行中任務</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="status-card completed">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="32"><CircleCheck /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-number">{{ stats.completedTasks }}</div>
              <div class="card-label">已完成任務</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="status-card total">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="32"><List /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-number">{{ stats.totalTasks }}</div>
              <div class="card-label">總任務數</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 類別統計 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>類別任務分布</span>
              <el-icon><Pie /></el-icon>
            </div>
          </template>
          
          <div class="chart-container">
            <canvas ref="pieChartRef" class="pie-chart-canvas"></canvas>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>類別工時分布</span>
              <el-icon><TrendCharts /></el-icon>
            </div>
          </template>
          
          <div class="chart-container">
            <canvas ref="workHoursChartRef" class="pie-chart-canvas"></canvas>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 近期任務和逾期提醒 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>即將到期任務</span>
              <el-badge :value="upcomingTasks.length" :hidden="upcomingTasks.length === 0">
                <el-icon><Warning /></el-icon>
              </el-badge>
            </div>
          </template>
          
          <div v-if="upcomingTasks.length === 0" class="empty-state">
            <el-icon size="48"><CircleCheck /></el-icon>
            <p>暫無即將到期的任務</p>
          </div>
          
          <div v-else>
            <div 
              v-for="task in upcomingTasks.slice(0, 5)" 
              :key="task.id"
              class="upcoming-task-item"
            >
              <div class="task-info">
                <div class="task-title">[{{ task.category_name }}] - {{ task.form_name }} - {{ task.title }}</div>
                <div class="task-meta">
                  <el-tag :type="getPriorityType(task.priority)" size="small">
                    {{ getPriorityText(task.priority) }}
                  </el-tag>
                  <span class="due-date">{{ task.due_date }}</span>
                </div>
              </div>
              <div class="days-left">
                <span class="days-number">{{ getDaysUntilDue(task.due_date) }}</span>
                <span class="days-text">天</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>最近完成任務</span>
              <el-icon><SuccessFilled /></el-icon>
            </div>
          </template>
          
          <div v-if="recentCompletedTasks.length === 0" class="empty-state">
            <el-icon size="48"><DocumentAdd /></el-icon>
            <p>暫無最近完成的任務</p>
          </div>
          
          <div v-else>
            <div 
              v-for="task in recentCompletedTasks.slice(0, 5)" 
              :key="task.id"
              class="completed-task-item"
            >
              <div class="task-info">
                <div class="task-title">{{ task.title }}</div>
                <div class="task-meta">
                  <span class="category">{{ task.category_name || '未分類' }}</span>
                  <span class="completed-date">{{ formatDateTime(task.updated_at) }}</span>
                </div>
              </div>
              <el-icon class="completed-icon" color="#67c23a"><CircleCheck /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>


    <!-- 本月工作統計 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>本月工作統計</span>
              <div>
                <el-button @click="refreshData" size="small" circle>
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="month-stat-item">
                <div class="stat-number">{{ monthlyStats.totalCreated }}</div>
                <div class="stat-label">新建任務</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="month-stat-item">
                <div class="stat-number">{{ monthlyStats.totalCompleted }}</div>
                <div class="stat-label">完成任務</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="month-stat-item">
                <div class="stat-number">{{ monthlyStats.totalWorkLogs }}</div>
                <div class="stat-label">工作紀錄</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="month-stat-item">
                <div class="stat-number">{{ (monthlyStats.completionRate * 100).toFixed(1) }}%</div>
                <div class="stat-label">完成率</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Clock, Loading, CircleCheck, List, TrendCharts, Pie, 
  Warning, SuccessFilled, DocumentAdd, Refresh
} from '@element-plus/icons-vue'
import { taskApi, workLogApi, categoryApi } from '../api'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  DoughnutController,
  PieController
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement, DoughnutController, PieController)

export default {
  name: 'Dashboard',
  components: {
    Clock, Loading, CircleCheck, List, TrendCharts, Pie,
    Warning, SuccessFilled, DocumentAdd, Refresh
  },
  setup() {
    const tasks = ref([])
    const workLogs = ref([])
    const categories = ref([])
    const pieChartRef = ref(null)
    const workHoursChartRef = ref(null)
    let chartInstance = null
    let workHoursChartInstance = null
    
    const stats = computed(() => {
      const pendingTasks = tasks.value.filter(task => task.status === 'pending').length
      const inProgressTasks = tasks.value.filter(task => task.status === 'in_progress').length
      const completedTasks = tasks.value.filter(task => task.status === 'completed').length
      const totalTasks = tasks.value.length
      
      const highPriority = tasks.value.filter(task => task.priority === 'high').length
      const mediumPriority = tasks.value.filter(task => task.priority === 'medium').length
      const lowPriority = tasks.value.filter(task => task.priority === 'low').length
      
      return {
        pendingTasks,
        inProgressTasks,
        completedTasks,
        totalTasks,
        highPriority,
        mediumPriority,
        lowPriority
      }
    })
    
    const categoryStats = computed(() => {
      const categoryMap = {}
      
      tasks.value.forEach(task => {
        const categoryName = task.category_name || '未分類'
        if (!categoryMap[categoryName]) {
          categoryMap[categoryName] = 0
        }
        categoryMap[categoryName]++
      })
      
      return Object.entries(categoryMap)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 8)
    })
    
    const workHoursStats = computed(() => {
      const categoryHours = {}
      
      workLogs.value.forEach(log => {
        const task = tasks.value.find(t => t.id === log.task_id)
        const categoryName = task?.category_name || '未分類'
        if (!categoryHours[categoryName]) {
          categoryHours[categoryName] = 0
        }
        categoryHours[categoryName] += log.hours || 0
      })
      
      return Object.entries(categoryHours)
        .map(([name, hours]) => ({ name, hours }))
        .sort((a, b) => b.hours - a.hours)
        .slice(0, 8)
    })
    
    const upcomingTasks = computed(() => {
      const now = new Date()
      const thirtyDaysLater = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)
      
      return tasks.value
        .filter(task => {
          if (!task.due_date || task.status === 'completed') return false
          const dueDate = new Date(task.due_date)
          return dueDate >= now && dueDate <= thirtyDaysLater
        })
        .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
    })
    
    const recentCompletedTasks = computed(() => {
      const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      
      return tasks.value
        .filter(task => {
          if (task.status !== 'completed' || !task.updated_at) return false
          return new Date(task.updated_at) >= sevenDaysAgo
        })
        .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    })
    
    const monthlyStats = computed(() => {
      const now = new Date()
      const firstDayOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
      
      const totalCreated = tasks.value.filter(task => {
        return task.created_at && new Date(task.created_at) >= firstDayOfMonth
      }).length
      
      const totalCompleted = tasks.value.filter(task => {
        return task.status === 'completed' && 
               task.updated_at && 
               new Date(task.updated_at) >= firstDayOfMonth
      }).length
      
      const totalWorkLogs = workLogs.value.filter(log => {
        return log.work_date && new Date(log.work_date) >= firstDayOfMonth
      }).length
      
      const completionRate = totalCreated > 0 ? totalCompleted / totalCreated : 0
      
      return {
        totalCreated,
        totalCompleted,
        totalWorkLogs,
        completionRate
      }
    })
    
    const loadTasks = async () => {
      try {
        const response = await taskApi.getAll()
        tasks.value = response.data
      } catch (error) {
        ElMessage.error('載入任務資料失敗')
      }
    }
    
    const loadWorkLogs = async () => {
      try {
        const response = await workLogApi.getAll()
        workLogs.value = response.data
      } catch (error) {
        ElMessage.error('載入工作紀錄失敗')
      }
    }
    
    const loadCategories = async () => {
      try {
        const response = await categoryApi.getAll()
        categories.value = response.data
      } catch (error) {
        ElMessage.error('載入類別資料失敗')
      }
    }
    
    const refreshData = async () => {
      await Promise.all([loadTasks(), loadWorkLogs(), loadCategories()])
      await nextTick()
      initPieChart()
      initWorkHoursChart()
      ElMessage.success('資料已刷新')
    }
    
    const initPieChart = () => {
      if (!pieChartRef.value || categoryStats.value.length === 0) return
      
      if (chartInstance) {
        chartInstance.destroy()
      }
      
      const ctx = pieChartRef.value.getContext('2d')
      
      chartInstance = new ChartJS(ctx, {
        type: 'pie',
        data: {
          labels: categoryStats.value.map(item => item.name || '未分類'),
          datasets: [{
            data: categoryStats.value.map(item => item.count),
            backgroundColor: categoryStats.value.map((_, index) => getCategoryColor(index)),
            borderColor: '#ffffff',
            borderWidth: 2,
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: {
                font: {
                  size: 13
                },
                padding: 20,
                generateLabels: (chart) => {
                  const data = chart.data
                  if (data.labels.length && data.datasets.length) {
                    return data.labels.map((label, i) => {
                      const count = data.datasets[0].data[i]
                      const percentage = ((count / stats.value.totalTasks) * 100).toFixed(1)
                      return {
                        text: `${label} (${count}個, ${percentage}%)`,
                        fillStyle: data.datasets[0].backgroundColor[i],
                        strokeStyle: data.datasets[0].borderColor,
                        lineWidth: data.datasets[0].borderWidth,
                        index: i
                      }
                    })
                  }
                  return []
                }
              }
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const label = context.label || ''
                  const value = context.parsed
                  const percentage = ((value / stats.value.totalTasks) * 100).toFixed(1)
                  return `${label}: ${value}個 (${percentage}%)`
                }
              }
            }
          }
        }
      })
    }
    
    const initWorkHoursChart = () => {
      if (!workHoursChartRef.value || workHoursStats.value.length === 0) return
      
      if (workHoursChartInstance) {
        workHoursChartInstance.destroy()
      }
      
      const ctx = workHoursChartRef.value.getContext('2d')
      const totalHours = workHoursStats.value.reduce((sum, item) => sum + item.hours, 0)
      
      workHoursChartInstance = new ChartJS(ctx, {
        type: 'pie',
        data: {
          labels: workHoursStats.value.map(item => item.name || '未分類'),
          datasets: [{
            data: workHoursStats.value.map(item => item.hours),
            backgroundColor: workHoursStats.value.map((_, index) => getCategoryColor(index)),
            borderColor: '#ffffff',
            borderWidth: 2,
            hoverOffset: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: {
                font: {
                  size: 13
                },
                padding: 20,
                generateLabels: (chart) => {
                  const data = chart.data
                  if (data.labels.length && data.datasets.length) {
                    return data.labels.map((label, i) => {
                      const hours = data.datasets[0].data[i]
                      const percentage = totalHours > 0 ? ((hours / totalHours) * 100).toFixed(1) : '0.0'
                      return {
                        text: `${label} (${hours}h, ${percentage}%)`,
                        fillStyle: data.datasets[0].backgroundColor[i],
                        strokeStyle: data.datasets[0].borderColor,
                        lineWidth: data.datasets[0].borderWidth,
                        index: i
                      }
                    })
                  }
                  return []
                }
              }
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const label = context.label || ''
                  const value = context.parsed
                  const percentage = totalHours > 0 ? ((value / totalHours) * 100).toFixed(1) : '0.0'
                  return `${label}: ${value}小時 (${percentage}%)`
                }
              }
            }
          }
        }
      })
    }
    
    const getPercentage = (value) => {
      return stats.value.totalTasks > 0 ? (value / stats.value.totalTasks) * 100 : 0
    }
    
    const getCategoryColor = (index) => {
      const colors = [
        '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', 
        '#909399', '#C45656', '#73767A', '#626AEF',
        '#53A8FF', '#85CE61'
      ]
      return colors[index % colors.length]
    }
    
    const getPriorityType = (priority) => {
      const types = {
        low: 'info',
        medium: 'warning',
        high: 'danger'
      }
      return types[priority] || 'info'
    }
    
    const getPriorityText = (priority) => {
      const texts = {
        low: '低',
        medium: '中',
        high: '高'
      }
      return texts[priority] || priority
    }
    
    const getDaysUntilDue = (dueDate) => {
      if (!dueDate) return 0
      const now = new Date()
      const due = new Date(dueDate)
      const diffTime = due - now
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return diffDays
    }
    
    const formatDateTime = (dateTime) => {
      if (!dateTime) return ''
      return new Date(dateTime).toLocaleString('zh-TW')
    }
    
    onMounted(async () => {
      await refreshData()
    })
    
    onUnmounted(() => {
      if (chartInstance) {
        chartInstance.destroy()
      }
      if (workHoursChartInstance) {
        workHoursChartInstance.destroy()
      }
    })
    
    return {
      stats,
      categoryStats,
      workHoursStats,
      upcomingTasks,
      recentCompletedTasks,
      monthlyStats,
      refreshData,
      getPercentage,
      getCategoryColor,
      getPriorityType,
      getPriorityText,
      getDaysUntilDue,
      formatDateTime,
      pieChartRef,
      workHoursChartRef
    }
  }
}
</script>

<style scoped>
.status-card {
  height: 100px;
}

.status-card.pending {
  border-left: 4px solid #E6A23C;
}

.status-card.in-progress {
  border-left: 4px solid #409EFF;
}

.status-card.completed {
  border-left: 4px solid #67C23A;
}

.status-card.total {
  border-left: 4px solid #909399;
}

.card-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.card-icon {
  color: #409EFF;
  margin-right: 15px;
}

.card-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.card-label {
  font-size: 13px;
  color: #606266;
  margin-top: 5px;
}


.chart-container {
  height: 300px;
  margin-top: 20px;
  position: relative;
}

.pie-chart-canvas {
  width: 100% !important;
  height: 100% !important;
}


.upcoming-task-item, .completed-task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.upcoming-task-item:last-child, .completed-task-item:last-child {
  border-bottom: none;
}

.task-info {
  flex: 1;
}

.task-title {
  font-size: 14px;
  color: #303133;
  margin-bottom: 5px;
  font-weight: 500;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #606266;
}

.days-left {
  text-align: center;
  min-width: 50px;
}

.days-number {
  font-size: 18px;
  font-weight: bold;
  color: #E6A23C;
}

.days-text {
  font-size: 12px;
  color: #606266;
}

.completed-icon {
  font-size: 20px;
}

.month-stat-item {
  text-align: center;
  padding: 20px 0;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: #606266;
  margin-top: 5px;
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: #909399;
}

.empty-state .el-icon {
  color: #C0C4CC;
  margin-bottom: 10px;
}
</style>