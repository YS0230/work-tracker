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


    <!-- 上週工作資訊 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>上週工作資訊 ({{ lastWeekRange }})</span>
              <div style="display: flex; gap: 10px; align-items: center;">
                <el-button @click="exportLastWeekData" size="small" type="success">
                  <el-icon><Download /></el-icon>
                  匯出 CSV
                </el-button>
                <el-icon><Document /></el-icon>
              </div>
            </div>
          </template>
          
          <div v-if="lastWeekWorkLogs.length === 0" class="empty-state">
            <el-icon size="48"><DocumentAdd /></el-icon>
            <p>上週暫無工作紀錄</p>
          </div>
          
          <div v-else>
            <el-table :data="lastWeekWorkLogs" style="width: 100%">
              <el-table-column prop="case_number" label="案件編號" width="120">
                <template #default="scope">
                  {{ scope.row.case_number }}
                </template>
              </el-table-column>
              <el-table-column prop="task_title" label="任務標題" min-width="200">
                <template #default="scope">
                  {{ scope.row.task_title }}
                </template>
              </el-table-column>
              <el-table-column prop="work_detail" label="工作明細" min-width="400">
                <template #default="scope">
                  <div style="line-height: 1.5; word-wrap: break-word; white-space: pre-wrap;">
                    {{ scope.row.work_detail }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="total_hours" label="總工時" width="80" align="center">
                <template #default="scope">
                  <el-tag type="primary" size="small">{{ scope.row.total_hours }}h</el-tag>
                </template>
              </el-table-column>
            </el-table>
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


  </div>
</template>

<script>
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Pie, Refresh, Search, Document, DocumentAdd, Download
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
    Pie, Refresh, Search, Document, DocumentAdd, Download
  },
  setup() {
    const workLogs = ref([])
    const tasks = ref([])
    const workHoursChartRef = ref(null)
    
    // 獲取上週日期範圍
    const getLastWeekRange = () => {
      const now = new Date()
      const currentDay = now.getDay() // 0 = Sunday, 1 = Monday, ...
      const daysToLastSunday = currentDay === 0 ? 7 : currentDay
      
      const lastWeekEnd = new Date(now)
      lastWeekEnd.setDate(now.getDate() - daysToLastSunday)
      
      const lastWeekStart = new Date(lastWeekEnd)
      lastWeekStart.setDate(lastWeekEnd.getDate() - 6)
      
      const formatDate = (date) => {
        const year = date.getFullYear()
        const month = String(date.getMonth() + 1).padStart(2, '0')
        const day = String(date.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
      }
      
      return {
        start: formatDate(lastWeekStart),
        end: formatDate(lastWeekEnd),
        display: `${formatDate(lastWeekStart)} ~ ${formatDate(lastWeekEnd)}`
      }
    }
    
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
    const lastWeekInfo = getLastWeekRange()
    
    
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
    
    // 上週工作紀錄（按任務標題和案件編號群組）
    const lastWeekWorkLogs = computed(() => {
      const lastWeek = getLastWeekRange()
      const startDate = new Date(lastWeek.start)
      const endDate = new Date(lastWeek.end + ' 23:59:59')
      
      const filteredWorkLogs = workLogs.value.filter(log => {
        if (!log.work_date) return false
        const workDate = new Date(log.work_date)
        return workDate >= startDate && workDate <= endDate
      })
      
      // 先加上任務資訊
      const logsWithTaskInfo = filteredWorkLogs.map(log => {
        const task = tasks.value.find(t => t.id === log.task_id)
        return {
          ...log,
          task_title: task?.title || '未指定任務',
          case_number: task?.case_number || log.case_number || '-'
        }
      })
      
      // 按任務標題和案件編號進行群組
      const groupedLogs = {}
      logsWithTaskInfo.forEach(log => {
        const groupKey = `${log.task_title}_${log.case_number}`
        if (!groupedLogs[groupKey]) {
          groupedLogs[groupKey] = {
            task_title: log.task_title,
            case_number: log.case_number,
            work_entries: {},
            total_hours: 0,
            date_descriptions: {}
          }
        }
        
        // 按日期記錄工時和描述
        const dateKey = log.work_date
        if (!groupedLogs[groupKey].work_entries[dateKey]) {
          groupedLogs[groupKey].work_entries[dateKey] = 0
          groupedLogs[groupKey].date_descriptions[dateKey] = []
        }
        groupedLogs[groupKey].work_entries[dateKey] += log.hours || 0
        groupedLogs[groupKey].total_hours += log.hours || 0
        
        if (log.description && log.description.trim()) {
          groupedLogs[groupKey].date_descriptions[dateKey].push(log.description.trim())
        }
      })
      
      // 轉換為陣列並格式化
      return Object.values(groupedLogs).map(group => {
        // 按日期排序並格式化工時和描述資訊
        const sortedEntries = Object.entries(group.work_entries)
          .sort(([dateA], [dateB]) => dateA.localeCompare(dateB))
        
        const workDetailLines = sortedEntries.map(([date, hours]) => {
          const descriptions = [...new Set(group.date_descriptions[date] || [])]
          const descText = descriptions.length > 0 ? `: ${descriptions.join(' | ')}` : ''
          return `${formatDate(date)} (${hours.toFixed(1)}h)${descText}`
        })
        
        return {
          task_title: group.task_title,
          case_number: group.case_number,
          work_detail: workDetailLines.join('\n'),
          total_hours: group.total_hours.toFixed(1)
        }
      }).sort((a, b) => a.task_title.localeCompare(b.task_title))
    })
    
    const lastWeekRange = computed(() => {
      return lastWeekInfo.display
    })
    
    const formatDate = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleDateString('zh-TW')
    }
    
    // 匯出上週工作資訊為 CSV
    const exportLastWeekData = () => {
      if (lastWeekWorkLogs.value.length === 0) {
        ElMessage.warning('上週無工作紀錄可匯出')
        return
      }
      
      // CSV 標題
      const headers = ['案件編號', '任務標題', '工作明細', '總工時']
      
      // 轉換數據為 CSV 格式
      const csvData = lastWeekWorkLogs.value.map(row => {
        // 處理工作明細，將換行符替換為分號隔開
        const workDetail = row.work_detail.replace(/\n/g, '; ')
        
        return [
          `"${row.case_number}"`,
          `"${row.task_title}"`,
          `"${workDetail}"`,
          `"${row.total_hours}h"`
        ]
      })
      
      // 組合 CSV 內容
      const csvContent = [
        headers.map(h => `"${h}"`).join(','),
        ...csvData.map(row => row.join(','))
      ].join('\n')
      
      // 加上 BOM 以支援中文顯示
      const bom = '\uFEFF'
      const csvWithBom = bom + csvContent
      
      // 建立下載連結
      const blob = new Blob([csvWithBom], { type: 'text/csv;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      
      const lastWeek = getLastWeekRange()
      const fileName = `上週工作資訊_${lastWeek.start}_${lastWeek.end}.csv`
      
      link.href = url
      link.download = fileName
      link.click()
      
      // 清理資源
      URL.revokeObjectURL(url)
      
      ElMessage.success(`已匯出 ${fileName}`)
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
      workHoursStats,
      lastWeekWorkLogs,
      lastWeekRange,
      refreshData,
      handleDateRangeChange,
      getCategoryColor,
      formatDate,
      exportLastWeekData,
      workHoursChartRef,
      dateRange,
      loading
    }
  }
}
</script>

<style scoped>
.chart-container {
  height: 300px;
  margin-top: 20px;
  position: relative;
}

.pie-chart-canvas {
  width: 100% !important;
  height: 100% !important;
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