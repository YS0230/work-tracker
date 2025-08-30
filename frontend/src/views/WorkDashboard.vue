<template>
  <div>
    <!-- 日期範圍查詢 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>工作查詢條件</span>
              <el-icon><Search /></el-icon>
            </div>
          </template>
          
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span style="font-size: 14px; color: #606266;">時間範圍：</span>
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
            <el-button @click="refreshData" :loading="loading" circle>
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工作時數總覽卡片區域 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="8">
        <el-card class="status-card work-hours">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="32"><Timer /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-number">{{ workStats.totalHours }}</div>
              <div class="card-label">總工作時數</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="status-card work-logs">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="32"><Document /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-number">{{ workStats.totalLogs }}</div>
              <div class="card-label">工作紀錄數</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="status-card avg-hours">
          <div class="card-content">
            <div class="card-icon">
              <el-icon size="32"><TrendCharts /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-number">{{ workStats.avgDailyHours }}</div>
              <div class="card-label">平均日工時</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 類別工時分布 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>類別工時分布</span>
              <el-icon><Pie /></el-icon>
            </div>
          </template>
          
          <div class="chart-container">
            <canvas ref="workHoursChartRef" class="pie-chart-canvas"></canvas>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近工作紀錄 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>最近工作紀錄</span>
              <el-icon><Clock /></el-icon>
            </div>
          </template>
          
          <div v-if="recentWorkLogs.length === 0" class="empty-state">
            <el-icon size="48"><DocumentAdd /></el-icon>
            <p>暫無工作紀錄</p>
          </div>
          
          <div v-else>
            <el-table :data="recentWorkLogs.slice(0, 10)" style="width: 100%">
              <el-table-column prop="work_date" label="工作日期" width="120">
                <template #default="scope">
                  {{ formatDate(scope.row.work_date) }}
                </template>
              </el-table-column>
              <el-table-column prop="task_title" label="任務" min-width="200">
                <template #default="scope">
                  <div>
                    <div style="font-weight: 500;">{{ scope.row.task_title || '未指定任務' }}</div>
                    <div style="font-size: 12px; color: #606266;">
                      {{ scope.row.category_name || '未分類' }}
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="工作內容" min-width="250">
                <template #default="scope">
                  <div style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    {{ scope.row.description || '-' }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="hours" label="工時" width="80" align="center">
                <template #default="scope">
                  <el-tag type="primary" size="small">{{ scope.row.hours }}h</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="建立時間" width="150">
                <template #default="scope">
                  {{ formatDateTime(scope.row.created_at) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 工作統計 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>{{ dateRangeTitle }}</span>
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
                <div class="stat-number">{{ monthlyStats.totalWorkLogs }}</div>
                <div class="stat-label">工作紀錄</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="month-stat-item">
                <div class="stat-number">{{ monthlyStats.totalHours }}</div>
                <div class="stat-label">總工時</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="month-stat-item">
                <div class="stat-number">{{ monthlyStats.avgDailyHours }}</div>
                <div class="stat-label">平均日工時</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="month-stat-item">
                <div class="stat-number">{{ monthlyStats.workingDays }}</div>
                <div class="stat-label">工作天數</div>
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
  Timer, Document, TrendCharts, Pie, Clock,
  DocumentAdd, Refresh, Search
} from '@element-plus/icons-vue'
import { workLogApi, taskApi } from '../api'
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
  name: 'WorkDashboard',
  components: {
    Timer, Document, TrendCharts, Pie, Clock,
    DocumentAdd, Refresh, Search
  },
  setup() {
    const workLogs = ref([])
    const tasks = ref([])
    const workHoursChartRef = ref(null)
    
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
    let workHoursChartInstance = null
    
    const workStats = computed(() => {
      let filteredWorkLogs = workLogs.value
      
      // 如果有設定日期範圍，按工作日期過濾
      if (dateRange.value && dateRange.value.length === 2) {
        const startDate = new Date(dateRange.value[0])
        const endDate = new Date(dateRange.value[1] + ' 23:59:59')
        
        filteredWorkLogs = workLogs.value.filter(log => {
          if (!log.work_date) return false
          const workDate = new Date(log.work_date)
          return workDate >= startDate && workDate <= endDate
        })
      }
      
      const totalHours = filteredWorkLogs.reduce((sum, log) => sum + (log.hours || 0), 0)
      const totalLogs = filteredWorkLogs.length
      
      // 計算工作天數
      const workDates = new Set(filteredWorkLogs.map(log => log.work_date))
      const workingDays = workDates.size
      
      const avgDailyHours = workingDays > 0 ? (totalHours / workingDays).toFixed(1) : '0.0'
      
      return {
        totalHours: totalHours.toFixed(1),
        totalLogs,
        avgDailyHours
      }
    })
    
    const workHoursStats = computed(() => {
      let filteredWorkLogs = workLogs.value
      
      // 如果有設定日期範圍，按工作日期過濾
      if (dateRange.value && dateRange.value.length === 2) {
        const startDate = new Date(dateRange.value[0])
        const endDate = new Date(dateRange.value[1] + ' 23:59:59')
        
        filteredWorkLogs = workLogs.value.filter(log => {
          if (!log.work_date) return false
          const workDate = new Date(log.work_date)
          return workDate >= startDate && workDate <= endDate
        })
      }
      
      const categoryHours = {}
      
      filteredWorkLogs.forEach(log => {
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
    
    const recentWorkLogs = computed(() => {
      let filteredWorkLogs = workLogs.value
      
      // 如果有設定日期範圍，按工作日期過濾
      if (dateRange.value && dateRange.value.length === 2) {
        const startDate = new Date(dateRange.value[0])
        const endDate = new Date(dateRange.value[1] + ' 23:59:59')
        
        filteredWorkLogs = workLogs.value.filter(log => {
          if (!log.work_date) return false
          const workDate = new Date(log.work_date)
          return workDate >= startDate && workDate <= endDate
        })
      }
      
      return filteredWorkLogs
        .map(log => {
          const task = tasks.value.find(t => t.id === log.task_id)
          return {
            ...log,
            task_title: task?.title,
            category_name: task?.category_name
          }
        })
        .sort((a, b) => new Date(b.work_date) - new Date(a.work_date))
    })
    
    const monthlyStats = computed(() => {
      let startDate, endDate
      
      if (dateRange.value && dateRange.value.length === 2) {
        startDate = new Date(dateRange.value[0])
        endDate = new Date(dateRange.value[1] + ' 23:59:59')
      } else {
        const now = new Date()
        startDate = new Date(now.getFullYear(), now.getMonth(), 1)
        endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59)
      }
      
      const filteredWorkLogs = workLogs.value.filter(log => {
        if (!log.work_date) return false
        const workDate = new Date(log.work_date)
        return workDate >= startDate && workDate <= endDate
      })
      
      const totalWorkLogs = filteredWorkLogs.length
      const totalHours = filteredWorkLogs.reduce((sum, log) => sum + (log.hours || 0), 0)
      
      // 計算工作天數
      const workDates = new Set(filteredWorkLogs.map(log => log.work_date))
      const workingDays = workDates.size
      
      const avgDailyHours = workingDays > 0 ? (totalHours / workingDays).toFixed(1) : '0.0'
      
      return {
        totalWorkLogs,
        totalHours: totalHours.toFixed(1),
        avgDailyHours,
        workingDays
      }
    })
    
    const loadWorkLogs = async (startDate = null, endDate = null) => {
      try {
        const params = {}
        if (startDate && endDate) {
          params.start_date = startDate
          params.end_date = endDate
        }
        const response = await workLogApi.getAll(params)
        workLogs.value = response.data
      } catch (error) {
        ElMessage.error('載入工作紀錄失敗')
      }
    }
    
    const loadTasks = async () => {
      try {
        const response = await taskApi.getAll()
        tasks.value = response.data
      } catch (error) {
        ElMessage.error('載入任務資料失敗')
      }
    }
    
    const refreshData = async () => {
      loading.value = true
      try {
        const [startDate, endDate] = dateRange.value || []
        await Promise.all([
          loadWorkLogs(startDate, endDate), 
          loadTasks()
        ])
        await nextTick()
        initWorkHoursChart()
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
        return `${dateRange.value[0]} ~ ${dateRange.value[1]} 工作統計`
      }
      return '本月工作統計'
    })
    
    const initWorkHoursChart = () => {
      if (!workHoursChartRef.value) return
      
      if (workHoursChartInstance) {
        workHoursChartInstance.destroy()
      }
      
      if (workHoursStats.value.length === 0) return
      
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
    
    const getCategoryColor = (index) => {
      const colors = [
        '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', 
        '#909399', '#C45656', '#73767A', '#626AEF',
        '#53A8FF', '#85CE61'
      ]
      return colors[index % colors.length]
    }
    
    const formatDate = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleDateString('zh-TW')
    }
    
    const formatDateTime = (dateTime) => {
      if (!dateTime) return ''
      return new Date(dateTime).toLocaleString('zh-TW')
    }
    
    onMounted(async () => {
      await refreshData()
    })
    
    onUnmounted(() => {
      if (workHoursChartInstance) {
        workHoursChartInstance.destroy()
      }
    })
    
    return {
      workStats,
      workHoursStats,
      recentWorkLogs,
      monthlyStats,
      refreshData,
      handleDateRangeChange,
      dateRangeTitle,
      getCategoryColor,
      formatDate,
      formatDateTime,
      workHoursChartRef,
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

.status-card.work-hours {
  border-left: 4px solid #409EFF;
}

.status-card.work-logs {
  border-left: 4px solid #67C23A;
}

.status-card.avg-hours {
  border-left: 4px solid #E6A23C;
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