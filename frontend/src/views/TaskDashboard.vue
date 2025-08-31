<template>
  <div>
    <!-- 日期範圍查詢 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>任務查詢條件</span>
              <el-icon><Search /></el-icon>
            </div>
          </template>
          
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="font-size: 14px; color: #34495e; font-weight: 500;">時間範圍：</span>
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="開始日期"
                end-placeholder="結束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                @change="handleDateRangeChange"
                style="width: 300px;"
              />
            </div>
            <el-button @click="refreshData" :loading="loading" v-debounce="2000" circle>
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 任務總覽卡片區域 -->
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

    <!-- 類別任務分布 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>類別任務分布</span>
              <el-icon><PieChart /></el-icon>
            </div>
          </template>
          
          <div class="chart-container">
            <canvas ref="pieChartRef" class="pie-chart-canvas"></canvas>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 近期任務 -->
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

    <!-- 任務統計 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>{{ dateRangeTitle }}</span>
              <div>
                <el-button @click="refreshData" v-debounce="2000" size="small" circle>
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="month-stat-item">
                <div class="stat-number">{{ taskStats.totalCreated }}</div>
                <div class="stat-label">新建任務</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="month-stat-item">
                <div class="stat-number">{{ taskStats.totalCompleted }}</div>
                <div class="stat-label">完成任務</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="month-stat-item">
                <div class="stat-number">{{ taskStats.totalInProgress }}</div>
                <div class="stat-label">進行中任務</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="month-stat-item">
                <div class="stat-number">{{ (taskStats.completionRate * 100).toFixed(1) }}%</div>
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
  Clock, Loading, CircleCheck, List, PieChart, 
  Warning, SuccessFilled, DocumentAdd, Refresh, Search
} from '@element-plus/icons-vue'
import { taskApi, categoryApi } from '../api'
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
  name: 'TaskDashboard',
  components: {
    Clock, Loading, CircleCheck, List, PieChart,
    Warning, SuccessFilled, DocumentAdd, Refresh, Search
  },
  setup() {
    const tasks = ref([])
    const categories = ref([])
    const pieChartRef = ref(null)
    
    // 預設當月日期範圍
    const getCurrentMonthRange = () => {
      const now = new Date()
      const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
      const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      
      const formatDate = (date) => {
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
      }
      
      return [
        formatDate(firstDay),
        formatDate(lastDay)
      ]
    }
    
    const dateRange = ref(getCurrentMonthRange())
    const loading = ref(false)
    let chartInstance = null
    
    const stats = computed(() => {
      let filteredTasks = tasks.value
      
      // 如果有設定日期範圍，按建立時間過濾
      if (dateRange.value && dateRange.value.length === 2) {
        const startDate = new Date(dateRange.value[0])
        const endDate = new Date(dateRange.value[1] + ' 23:59:59')
        
        filteredTasks = tasks.value.filter(task => {
          if (!task.created_at) return false
          const createDate = new Date(task.created_at)
          return createDate >= startDate && createDate <= endDate
        })
      }
      
      const pendingTasks = filteredTasks.filter(task => task.status === 'pending').length
      const inProgressTasks = filteredTasks.filter(task => task.status === 'in_progress').length
      const completedTasks = filteredTasks.filter(task => task.status === 'completed').length
      const totalTasks = filteredTasks.length
      
      return {
        pendingTasks,
        inProgressTasks,
        completedTasks,
        totalTasks
      }
    })
    
    const categoryStats = computed(() => {
      let filteredTasks = tasks.value
      
      // 如果有設定日期範圍，按建立時間過濾
      if (dateRange.value && dateRange.value.length === 2) {
        const startDate = new Date(dateRange.value[0])
        const endDate = new Date(dateRange.value[1] + ' 23:59:59')
        
        filteredTasks = tasks.value.filter(task => {
          if (!task.created_at) return false
          const createDate = new Date(task.created_at)
          return createDate >= startDate && createDate <= endDate
        })
      }
      
      const categoryMap = {}
      
      filteredTasks.forEach(task => {
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
    
    const upcomingTasks = computed(() => {
      const now = new Date()
      const thirtyDaysLater = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)
      
      let filteredTasks = tasks.value
      
      // 如果有設定日期範圍，先按日期範圍過濾
      if (dateRange.value && dateRange.value.length === 2) {
        const startDate = new Date(dateRange.value[0])
        const endDate = new Date(dateRange.value[1] + ' 23:59:59')
        
        filteredTasks = tasks.value.filter(task => {
          if (!task.created_at) return false
          const createDate = new Date(task.created_at)
          return createDate >= startDate && createDate <= endDate
        })
      }
      
      return filteredTasks
        .filter(task => {
          if (!task.due_date || task.status === 'completed') return false
          const dueDate = new Date(task.due_date)
          return dueDate >= now && dueDate <= thirtyDaysLater
        })
        .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
    })
    
    const recentCompletedTasks = computed(() => {
      let filteredTasks = tasks.value
      
      // 如果有設定日期範圍，先按日期範圍過濾
      if (dateRange.value && dateRange.value.length === 2) {
        const startDate = new Date(dateRange.value[0])
        const endDate = new Date(dateRange.value[1] + ' 23:59:59')
        
        filteredTasks = tasks.value.filter(task => {
          if (!task.created_at) return false
          const createDate = new Date(task.created_at)
          return createDate >= startDate && createDate <= endDate
        })
      } else {
        // 沒有日期範圍時，只顯示最近7天完成的任務
        const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        filteredTasks = tasks.value.filter(task => {
          if (task.status !== 'completed' || !task.updated_at) return false
          return new Date(task.updated_at) >= sevenDaysAgo
        })
      }
      
      return filteredTasks
        .filter(task => task.status === 'completed')
        .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    })
    
    const taskStats = computed(() => {
      let startDate, endDate
      
      if (dateRange.value && dateRange.value.length === 2) {
        startDate = new Date(dateRange.value[0])
        endDate = new Date(dateRange.value[1] + ' 23:59:59')
      } else {
        const now = new Date()
        startDate = new Date(now.getFullYear(), now.getMonth(), 1)
        endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59)
      }
      
      const totalCreated = tasks.value.filter(task => {
        if (!task.created_at) return false
        const createDate = new Date(task.created_at)
        return createDate >= startDate && createDate <= endDate
      }).length
      
      const totalCompleted = tasks.value.filter(task => {
        if (task.status !== 'completed' || !task.updated_at) return false
        const updateDate = new Date(task.updated_at)
        return updateDate >= startDate && updateDate <= endDate
      }).length
      
      const totalInProgress = tasks.value.filter(task => {
        if (task.status !== 'in_progress' || !task.created_at) return false
        const createDate = new Date(task.created_at)
        return createDate >= startDate && createDate <= endDate
      }).length
      
      const completionRate = totalCreated > 0 ? totalCompleted / totalCreated : 0
      
      return {
        totalCreated,
        totalCompleted,
        totalInProgress,
        completionRate
      }
    })
    
    const loadTasks = async (startDate = null, endDate = null) => {
      try {
        const params = {}
        if (startDate && endDate) {
          params.start_date = startDate
          params.end_date = endDate
        }
        const response = await taskApi.getAll(params)
        tasks.value = response.data
      } catch (error) {
        ElMessage.error('載入任務資料失敗')
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
      loading.value = true
      try {
        const [startDate, endDate] = dateRange.value || []
        await Promise.all([
          loadTasks(startDate, endDate), 
          loadCategories()
        ])
        await nextTick()
        initPieChart()
        ElMessage.success('資料已刷新')
      } finally {
        loading.value = false
      }
    }
    
    const handleDateRangeChange = async (value) => {
      dateRange.value = value
      if (value && value.length === 2) {
        await refreshData()
      }
    }
    
    const dateRangeTitle = computed(() => {
      if (dateRange.value && dateRange.value.length === 2) {
        return `${dateRange.value[0]} ~ ${dateRange.value[1]} 任務統計`
      }
      return '本月任務統計'
    })
    
    const initPieChart = () => {
      if (!pieChartRef.value) return
      
      if (chartInstance) {
        chartInstance.destroy()
      }
      
      if (categoryStats.value.length === 0) return
      
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
    })
    
    return {
      stats,
      categoryStats,
      upcomingTasks,
      recentCompletedTasks,
      taskStats,
      refreshData,
      handleDateRangeChange,
      dateRangeTitle,
      getCategoryColor,
      getPriorityType,
      getPriorityText,
      getDaysUntilDue,
      formatDateTime,
      pieChartRef,
      dateRange,
      loading
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
  font-size: 30px;
  font-weight: bold;
  color: #2c3e50;
  line-height: 1;
}

.card-label {
  font-size: 14px;
  color: #34495e;
  margin-top: 5px;
  font-weight: 500;
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
  font-size: 15px;
  color: #2c3e50;
  margin-bottom: 5px;
  font-weight: 600;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #34495e;
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
  font-size: 13px;
  color: #34495e;
  font-weight: 500;
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
  font-size: 14px;
  color: #34495e;
  margin-top: 5px;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: #5a6c7d;
  font-size: 15px;
}

.empty-state .el-icon {
  color: #7f8c8d;
  margin-bottom: 10px;
}
</style>