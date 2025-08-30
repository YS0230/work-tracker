<template>
  <div>
    <!-- 篩選區域 -->
    <el-card style="margin-bottom: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>篩選條件</span>
          <el-button @click="toggleFilters" circle size="small">
            <el-icon>
              <ArrowUp v-if="showFilters" />
              <ArrowDown v-else />
            </el-icon>
          </el-button>
        </div>
      </template>
      
      <div v-show="showFilters">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="工作日期">
              <el-date-picker
                v-model="filters.work_date"
                type="date"
                placeholder="選擇日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                @change="searchWorkLogs"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="案件編號">
              <el-input v-model="filters.case_number" placeholder="請輸入案件編號" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="任務標題">
              <el-input v-model="filters.task_title" placeholder="請輸入任務標題" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="完成狀態">
              <el-select v-model="filters.completed" placeholder="請選擇狀態" clearable>
                <el-option label="已完成" :value="true" />
                <el-option label="未完成" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="工作時數範圍">
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-input-number
                    v-model="filters.hours_min"
                    :min="0"
                    :max="24"
                    :step="0.5"
                    :precision="1"
                    placeholder="最小時數"
                    style="width: 100%"
                  />
                </el-col>
                <el-col :span="12">
                  <el-input-number
                    v-model="filters.hours_max"
                    :min="0"
                    :max="24"
                    :step="0.5"
                    :precision="1"
                    placeholder="最大時數"
                    style="width: 100%"
                  />
                </el-col>
              </el-row>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="工作日期範圍">
              <el-date-picker
                v-model="filters.work_date_range"
                type="daterange"
                range-separator="至"
                start-placeholder="開始日期"
                end-placeholder="結束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row>
          <el-col :span="24" style="text-align: right">
            <el-button @click="resetFilters">重置</el-button>
            <el-button type="primary" @click="searchWorkLogs">查詢</el-button>
          </el-col>
        </el-row>
      </div>
    </el-card>
    
    <el-row style="margin-bottom: 20px">
      <el-col :span="18">
        <el-input
          v-model="searchKeyword"
          placeholder="輸入關鍵字搜索工作紀錄（案件編號、任務標題、工作描述）"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </el-col>
      <el-col :span="6" style="text-align: right">
        <el-button @click="exportCSV" style="margin-right: 10px">
          <el-icon><Download /></el-icon>
          匯出CSV
        </el-button>
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          新增工作紀錄
        </el-button>
      </el-col>
    </el-row>

    <!-- 工作紀錄列表 -->
    <el-table :data="filteredWorkLogs" border style="width: 100%">
      <el-table-column type="index" label="流水號" width="80" :index="(index) => index + 1" />
      <el-table-column prop="work_date" label="工作日期" width="100" />
      <el-table-column label="案件編號" width="120">
        <template #default="scope">
          {{ scope.row.task?.case_number }}
        </template>
      </el-table-column>
      <el-table-column label="任務標題" min-width="200">
        <template #default="scope">
          <div>
            <div>{{ scope.row.task?.title }}</div>
            <div v-if="scope.row.task?.description" style="color: #999; font-size: 12px; margin-top: 2px;">
              ({{ scope.row.task?.description }})
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="hours" label="工時" width="60" />
      <el-table-column prop="description" label="工作描述" min-width="200">
        <template #default="scope">
          <div style="line-height: 1.4; word-wrap: break-word; white-space: pre-wrap;">
            {{ scope.row.description || '-' }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="completed" label="完成狀態" width="100" align="center">
        <template #default="scope">
          <el-tag :type="scope.row.completed ? 'success' : 'warning'">
            {{ scope.row.completed ? '已完成' : '未完成' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="建立時間" width="150">
        <template #default="scope">
          {{ formatDateTime(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="異動時間" width="150">
        <template #default="scope">
          {{ formatDateTime(scope.row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="editWorkLog(scope.row)" circle>
            <el-icon><Edit /></el-icon>
          </el-button>
          <el-button size="small" type="danger" @click="deleteWorkLog(scope.row.id)" circle>
            <el-icon><Delete /></el-icon>
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/編輯對話框 -->
    <el-dialog
      :title="isEditing ? '編輯工作紀錄' : '新增工作紀錄'"
      v-model="showAddDialog"
      width="600px"
    >
      <el-form :model="workLogForm" :rules="formRules" ref="workLogFormRef" label-width="100px">
        <el-form-item label="任務" prop="task_id">
          <el-select v-model="workLogForm.task_id" placeholder="請選擇任務" filterable>
            <el-option
              v-for="task in incompleteTasks"
              :key="task.id"
              :label="`${task.category_name} - ${task.form_name} - ${task.title}`"
              :value="task.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="工作日期" prop="work_date">
          <el-date-picker
            v-model="workLogForm.work_date"
            type="date"
            placeholder="選擇日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="工作時數" prop="hours">
          <el-input-number
            v-model="workLogForm.hours"
            :min="0.5"
            :max="24"
            :step="0.5"
            :precision="1"
            style="width: 100%"
          />
        </el-form-item>
        
        <!-- 顯示選中任務的描述 -->
        <el-form-item v-if="selectedTaskDescription" label="任務描述">
          <div style="padding: 10px; background: #f5f5f5; border: 1px solid #dcdfe6; border-radius: 4px; color: #606266; width: 100%;">
            {{ selectedTaskDescription }}
          </div>
        </el-form-item>
        
        <el-form-item label="工作描述" prop="description">
          <el-input
            v-model="workLogForm.description"
            type="textarea"
            :rows="4"
            placeholder="請輸入工作描述"
          />
        </el-form-item>
        
        <el-form-item label="任務完成">
          <el-switch
            v-model="workLogForm.completed"
            active-text="完成"
            inactive-text="未完成"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveWorkLog">確定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, ArrowUp, ArrowDown, Plus, Edit, Delete, Download } from '@element-plus/icons-vue'
import { workLogApi, taskApi } from '@/api'

// 響應式數據
const workLogs = ref([])
const incompleteTasks = ref([])
const showAddDialog = ref(false)
const isEditing = ref(false)
const workLogFormRef = ref()
const searchKeyword = ref('')
const showFilters = ref(true)

// 篩選條件
const filters = reactive({
  work_date: new Date().toISOString().slice(0, 10), // 預設今天
  case_number: '',
  task_title: '',
  completed: null,
  hours_min: null,
  hours_max: null,
  work_date_range: []
})

// 表單數據
const workLogForm = reactive({
  id: null,
  task_id: null,
  work_date: new Date().toISOString().slice(0, 10),
  hours: 1,
  description: '',
  completed: false
})

// 表單驗證規則
const formRules = {
  task_id: [{ required: true, message: '請選擇任務', trigger: 'change' }],
  work_date: [{ required: true, message: '請選擇工作日期', trigger: 'change' }],
  hours: [{ required: true, message: '請輸入工作時數', trigger: 'blur' }]
}

// 載入工作紀錄
const loadWorkLogs = async () => {
  try {
    const response = await workLogApi.getAll()
    workLogs.value = response.data
  } catch (error) {
    ElMessage.error('載入工作紀錄失敗')
    console.error(error)
  }
}

// 搜尋工作紀錄
const searchWorkLogs = async () => {
  try {
    const params = {}
    
    // 處理單一日期篩選
    if (filters.work_date) {
      params.work_date = filters.work_date
    }
    
    // 處理日期範圍篩選（如果有範圍則優先使用範圍）
    if (filters.work_date_range && filters.work_date_range.length === 2) {
      params.start_date = filters.work_date_range[0]
      params.end_date = filters.work_date_range[1]
      delete params.work_date // 移除單一日期參數
    }
    
    const response = await workLogApi.getAll(params)
    workLogs.value = response.data
  } catch (error) {
    ElMessage.error('搜尋工作紀錄失敗')
    console.error(error)
  }
}

// 載入未完成任務
const loadIncompleteTasks = async () => {
  try {
    const response = await taskApi.getIncomplete()
    incompleteTasks.value = response.data
  } catch (error) {
    ElMessage.error('載入任務失敗')
    console.error(error)
  }
}

// 重置篩選條件
const resetFilters = () => {
  Object.assign(filters, {
    work_date: '',
    case_number: '',
    task_title: '',
    completed: null,
    hours_min: null,
    hours_max: null,
    work_date_range: []
  })
  searchWorkLogs()
}

// 切換篩選區域顯示狀態
const toggleFilters = () => {
  showFilters.value = !showFilters.value
}

// 關鍵字搜尋的計算屬性
const filteredWorkLogs = computed(() => {
  let result = workLogs.value
  
  // 關鍵字搜尋
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(log => {
      return (
        log.task?.case_number?.toLowerCase().includes(keyword) ||
        log.task?.title?.toLowerCase().includes(keyword) ||
        log.description?.toLowerCase().includes(keyword)
      )
    })
  }
  
  // 案件編號篩選
  if (filters.case_number) {
    const caseNumber = filters.case_number.toLowerCase()
    result = result.filter(log => 
      log.task?.case_number?.toLowerCase().includes(caseNumber)
    )
  }
  
  // 任務標題篩選
  if (filters.task_title) {
    const taskTitle = filters.task_title.toLowerCase()
    result = result.filter(log => 
      log.task?.title?.toLowerCase().includes(taskTitle)
    )
  }
  
  // 完成狀態篩選
  if (filters.completed !== null) {
    result = result.filter(log => log.completed === filters.completed)
  }
  
  // 工時範圍篩選
  if (filters.hours_min !== null) {
    result = result.filter(log => log.hours >= filters.hours_min)
  }
  if (filters.hours_max !== null) {
    result = result.filter(log => log.hours <= filters.hours_max)
  }
  
  return result
})

// 處理搜尋輸入
const handleSearch = () => {
  // 搜索功能由 computed 屬性自動處理
}

// 計算選中任務的描述
const selectedTaskDescription = computed(() => {
  if (!workLogForm.task_id) return ''
  const selectedTask = incompleteTasks.value.find(task => task.id === workLogForm.task_id)
  return selectedTask?.description || ''
})

// 編輯工作紀錄
const editWorkLog = (workLog) => {
  Object.assign(workLogForm, workLog)
  isEditing.value = true
  showAddDialog.value = true
  loadIncompleteTasks() // 重新載入任務選項
}

// 儲存工作紀錄
const saveWorkLog = async () => {
  if (!workLogFormRef.value) return
  
  try {
    await workLogFormRef.value.validate()
    
    const data = { ...workLogForm }
    delete data.id
    
    if (isEditing.value) {
      await workLogApi.update(workLogForm.id, data)
      ElMessage.success('更新工作紀錄成功')
    } else {
      await workLogApi.create(data)
      ElMessage.success('新增工作紀錄成功')
    }
    
    showAddDialog.value = false
    resetForm()
    searchWorkLogs() // 重新載入列表
    
  } catch (error) {
    if (error.errors) return // 表單驗證錯誤
    ElMessage.error('儲存工作紀錄失敗')
    console.error(error)
  }
}

// 刪除工作紀錄
const deleteWorkLog = async (id) => {
  try {
    await ElMessageBox.confirm('確定要刪除這筆工作紀錄嗎？', '確認刪除', {
      type: 'warning'
    })
    
    await workLogApi.delete(id)
    ElMessage.success('刪除工作紀錄成功')
    searchWorkLogs() // 重新載入列表
    
  } catch (error) {
    if (error === 'cancel') return
    ElMessage.error('刪除工作紀錄失敗')
    console.error(error)
  }
}

// 重置表單
const resetForm = () => {
  Object.assign(workLogForm, {
    id: null,
    task_id: null,
    work_date: new Date().toISOString().slice(0, 10),
    hours: 1,
    description: '',
    completed: false
  })
  isEditing.value = false
}

// 格式化日期時間
const formatDateTime = (dateTime) => {
  if (!dateTime) return ''
  return new Date(dateTime).toLocaleString('zh-TW')
}

// CSV 匯出功能
const exportCSV = () => {
  if (filteredWorkLogs.value.length === 0) {
    ElMessage.warning('沒有資料可以匯出')
    return
  }

  // CSV 標頭
  const headers = [
    '流水號',
    '工作日期',
    '案件編號',
    '任務標題',
    '工時',
    '工作描述',
    '完成狀態',
    '建立時間',
    '異動時間'
  ]

  // 轉換資料
  const csvData = filteredWorkLogs.value.map((log, index) => [
    index + 1,
    log.work_date || '',
    log.task?.case_number || '',
    log.task?.title || '',
    log.hours || '',
    log.description || '',
    log.completed ? '已完成' : '未完成',
    formatDateTime(log.created_at),
    formatDateTime(log.updated_at)
  ])

  // 建立 CSV 內容
  const csvContent = [headers, ...csvData]
    .map(row => row.map(field => `"${field}"`).join(','))
    .join('\n')

  // 加上 BOM 以支持中文
  const BOM = '\uFEFF'
  const csvWithBOM = BOM + csvContent

  // 建立並下載檔案
  const blob = new Blob([csvWithBOM], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  
  const now = new Date()
  const timestamp = now.toISOString().slice(0, 19).replace(/:/g, '-')
  link.setAttribute('download', `工作紀錄_${timestamp}.csv`)
  
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  ElMessage.success(`已匯出 ${filteredWorkLogs.value.length} 筆資料`)
}

// 初始化
onMounted(async () => {
  await searchWorkLogs() // 使用搜尋功能，預設載入今天的紀錄
  await loadIncompleteTasks()
})

</script>

<style scoped>
/* 樣式與 TaskList 保持一致 */
</style>