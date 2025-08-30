<template>
  <div class="work-log">
    <div class="header">
      <h2>每日工作紀錄</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        新增工作紀錄
      </el-button>
    </div>

    <!-- 篩選區域 -->
    <div class="filter-section">
      <el-form :model="filters" inline>
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
        <el-form-item>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 工作紀錄列表 -->
    <div class="table-section">
      <el-table :data="workLogs" border stripe>
        <el-table-column prop="work_date" label="工作日期" width="120" />
        <el-table-column prop="task_case_number" label="案件編號" width="120" />
        <el-table-column prop="task_title" label="任務標題" min-width="200" />
        <el-table-column prop="hours" label="工時" width="80" />
        <el-table-column prop="description" label="工作描述" min-width="200" />
        <el-table-column prop="completed" label="完成狀態" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.completed ? 'success' : 'warning'">
              {{ scope.row.completed ? '已完成' : '未完成' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="editWorkLog(scope.row)">編輯</el-button>
            <el-button size="small" type="danger" @click="deleteWorkLog(scope.row.id)">刪除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/編輯對話框 -->
    <el-dialog
      :title="isEditing ? '編輯工作紀錄' : '新增工作紀錄'"
      v-model="showAddDialog"
      width="600px"
    >
      <el-form :model="workLogForm" :rules="formRules" ref="workLogFormRef" label-width="100px">
        <el-form-item label="任務" prop="task_id">
          <el-select
            v-model="workLogForm.task_id"
            placeholder="請選擇任務"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="task in incompleteTasks"
              :key="task.id"
              :label="`${task.case_number} - ${task.title}`"
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { workLogApi, taskApi } from '@/api'

// 響應式數據
const workLogs = ref([])
const incompleteTasks = ref([])
const showAddDialog = ref(false)
const isEditing = ref(false)
const workLogFormRef = ref()

// 篩選條件
const filters = reactive({
  work_date: new Date().toISOString().slice(0, 10) // 預設今天
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
    if (filters.work_date) {
      params.work_date = filters.work_date
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
  filters.work_date = ''
  searchWorkLogs()
}

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

// 初始化
onMounted(async () => {
  await searchWorkLogs() // 使用搜尋功能，預設載入今天的紀錄
  await loadIncompleteTasks()
})

// 監聽對話框關閉
const handleDialogClose = () => {
  resetForm()
  workLogFormRef.value?.clearValidate()
}
</script>

<style scoped>
.work-log {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-section {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.table-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}
</style>