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
            <el-form-item label="案號">
              <el-input v-model="filters.case_number" placeholder="請輸入案號" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="案件類別">
              <el-select v-model="filters.category_id" placeholder="請選擇類別" clearable>
                <el-option
                  v-for="category in categories"
                  :key="category.id"
                  :label="category.name"
                  :value="category.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="表單名稱">
              <el-input v-model="filters.form_name" placeholder="請輸入表單名稱" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="任務標題">
              <el-input v-model="filters.title" placeholder="請輸入任務標題" clearable />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="描述">
              <el-input v-model="filters.description" placeholder="請輸入描述" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="聲請人">
              <el-input v-model="filters.requester" placeholder="請輸入聲請人" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="狀態">
              <el-select v-model="filters.status" placeholder="請選擇狀態" clearable>
                <el-option label="待處理" value="pending" />
                <el-option label="進行中" value="in_progress" />
                <el-option label="已完成" value="completed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="優先級">
              <el-select v-model="filters.priority" placeholder="請選擇優先級" clearable>
                <el-option label="低" value="low" />
                <el-option label="中" value="medium" />
                <el-option label="高" value="high" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="截止日期">
              <el-date-picker
                v-model="filters.due_date_range"
                type="daterange"
                range-separator="至"
                start-placeholder="開始日期"
                end-placeholder="結束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="建立時間">
              <el-date-picker
                v-model="filters.created_at_range"
                type="datetimerange"
                range-separator="至"
                start-placeholder="開始時間"
                end-placeholder="結束時間"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="異動時間">
              <el-date-picker
                v-model="filters.updated_at_range"
                type="datetimerange"
                range-separator="至"
                start-placeholder="開始時間"
                end-placeholder="結束時間"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row>
          <el-col :span="24" style="text-align: right">
            <el-button @click="resetFilters">重置</el-button>
            <el-button type="primary" @click="searchTasks">查詢</el-button>
          </el-col>
        </el-row>
      </div>
    </el-card>
    
    <el-row style="margin-bottom: 20px">
      <el-col :span="18">
        <el-input
          v-model="searchKeyword"
          placeholder="輸入關鍵字搜索任務（案號、案件類別、表單名稱、標題、描述、聲請人）"
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
          新增任務
        </el-button>
      </el-col>
    </el-row>

    <!-- 任務列表 -->
    <el-table :data="filteredTasks" border style="width: 100%">
      <el-table-column type="index" label="流水號" width="80" :index="(index) => index + 1" />
      <el-table-column prop="case_number" label="案號" width="120" />
      <el-table-column prop="category_name" label="案件類別" width="120" />
      <el-table-column prop="form_name" label="表單名稱" width="150" />
      <el-table-column prop="title" label="任務標題" width="200" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="requester" label="聲請人" width="100" />
      <el-table-column prop="status" label="狀態" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="priority" label="優先級" width="80">
        <template #default="scope">
          <el-tag :type="getPriorityType(scope.row.priority)" size="small">
            {{ getPriorityText(scope.row.priority) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="due_date" label="截止日期" width="120" />
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
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-button size="small" @click="editTask(scope.row)" circle>
            <el-icon><Edit /></el-icon>
          </el-button>
          <el-button size="small" type="danger" @click="deleteTask(scope.row.id)" circle>
            <el-icon><Delete /></el-icon>
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/編輯任務對話框 -->
    <el-dialog
      :title="isEdit ? '編輯任務' : '新增任務'"
      v-model="showAddDialog"
      width="600px"
    >
      <el-form :model="taskForm" :rules="taskRules" ref="taskFormRef" label-width="100px">
        <el-form-item label="案號" prop="case_number">
          <el-input v-model="taskForm.case_number" />
        </el-form-item>
        
        <el-form-item label="案件類別" prop="category_id">
          <el-select v-model="taskForm.category_id" placeholder="請選擇類別">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="表單名稱">
          <el-input v-model="taskForm.form_name" />
        </el-form-item>
        
        <el-form-item label="任務標題" prop="title">
          <el-input v-model="taskForm.title" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input type="textarea" v-model="taskForm.description" :rows="3" />
        </el-form-item>
        
        <el-form-item label="聲請人">
          <el-input v-model="taskForm.requester" />
        </el-form-item>
        
        <el-form-item label="狀態">
          <el-select v-model="taskForm.status">
            <el-option label="待處理" value="pending" />
            <el-option label="進行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="優先級">
          <el-select v-model="taskForm.priority">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="截止日期">
          <el-date-picker
            v-model="taskForm.due_date"
            type="date"
            placeholder="選擇日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitTask">確定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, ArrowUp, ArrowDown, Plus, Edit, Delete, Download } from '@element-plus/icons-vue'
import { taskApi, categoryApi } from '../api'

export default {
  name: 'TaskList',
  components: {
    Search,
    ArrowUp,
    ArrowDown,
    Plus,
    Edit,
    Delete,
    Download
  },
  setup() {
    const tasks = ref([])
    const categories = ref([])
    const showAddDialog = ref(false)
    const isEdit = ref(false)
    const taskFormRef = ref(null)
    const searchKeyword = ref('')
    const showFilters = ref(true)
    const filters = ref({
      case_number: '',
      category_id: '',
      form_name: '',
      title: '',
      description: '',
      requester: '',
      status: '',
      priority: '',
      due_date_range: [],
      created_at_range: [],
      updated_at_range: []
    })

    const taskForm = reactive({
      id: null,
      case_number: '',
      category_id: '',
      form_name: '',
      title: '',
      description: '',
      requester: '',
      status: 'pending',
      priority: 'medium',
      due_date: ''
    })

    const taskRules = {
      case_number: [{ required: true, message: '請輸入案號', trigger: 'blur' }],
      category_id: [{ required: true, message: '請選擇案件類別', trigger: 'change' }],
      title: [{ required: true, message: '請輸入任務標題', trigger: 'blur' }]
    }

    const resetForm = () => {
      Object.assign(taskForm, {
        id: null,
        case_number: '',
        category_id: '',
        form_name: '',
        title: '',
        description: '',
        requester: '',
        status: 'pending',
        priority: 'medium',
        due_date: ''
      })
    }

    const loadTasks = async (queryParams = {}) => {
      try {
        const response = await taskApi.getAll(queryParams)
        tasks.value = response.data
      } catch (error) {
        ElMessage.error('載入任務失敗')
      }
    }

    const loadCategories = async () => {
      try {
        const response = await categoryApi.getAll()
        categories.value = response.data
      } catch (error) {
        ElMessage.error('載入類別失敗')
      }
    }

    const submitTask = async () => {
      try {
        await taskFormRef.value.validate()
        
        const data = { ...taskForm }
        delete data.id

        if (isEdit.value) {
          await taskApi.update(taskForm.id, data)
          ElMessage.success('更新成功')
        } else {
          await taskApi.create(data)
          ElMessage.success('新增成功')
        }

        showAddDialog.value = false
        resetForm()
        loadTasks()
      } catch (error) {
        if (error.response) {
          ElMessage.error('操作失敗')
        }
      }
    }

    const editTask = (task) => {
      isEdit.value = true
      Object.assign(taskForm, task)
      showAddDialog.value = true
    }

    const deleteTask = async (taskId) => {
      try {
        await ElMessageBox.confirm('確定要刪除這個任務嗎？', '確認', {
          confirmButtonText: '確定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await taskApi.delete(taskId)
        ElMessage.success('刪除成功')
        loadTasks()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('刪除失敗')
        }
      }
    }

    const getStatusType = (status) => {
      const types = {
        pending: 'warning',
        in_progress: 'primary',
        completed: 'success'
      }
      return types[status] || 'info'
    }

    const getStatusText = (status) => {
      const texts = {
        pending: '待處理',
        in_progress: '進行中',
        completed: '已完成'
      }
      return texts[status] || status
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

    const formatDateTime = (dateTime) => {
      if (!dateTime) return ''
      return new Date(dateTime).toLocaleString('zh-TW')
    }

    const filteredTasks = computed(() => {
      if (!searchKeyword.value) {
        return tasks.value
      }
      
      const keyword = searchKeyword.value.toLowerCase()
      return tasks.value.filter(task => {
        return (
          task.case_number?.toLowerCase().includes(keyword) ||
          task.category_name?.toLowerCase().includes(keyword) ||
          task.form_name?.toLowerCase().includes(keyword) ||
          task.title?.toLowerCase().includes(keyword) ||
          task.description?.toLowerCase().includes(keyword) ||
          task.requester?.toLowerCase().includes(keyword)
        )
      })
    })

    const handleSearch = () => {
      // 搜索功能由 computed 屬性自動處理
    }

    const toggleFilters = () => {
      showFilters.value = !showFilters.value
    }

    const searchTasks = async () => {
      const queryParams = {}
      
      // 處理文字欄位
      if (filters.value.case_number) queryParams.case_number = filters.value.case_number
      if (filters.value.category_id) queryParams.category_id = filters.value.category_id
      if (filters.value.form_name) queryParams.form_name = filters.value.form_name
      if (filters.value.title) queryParams.title = filters.value.title
      if (filters.value.description) queryParams.description = filters.value.description
      if (filters.value.requester) queryParams.requester = filters.value.requester
      if (filters.value.status) queryParams.status = filters.value.status
      if (filters.value.priority) queryParams.priority = filters.value.priority
      
      // 處理日期範圍
      if (filters.value.due_date_range && filters.value.due_date_range.length === 2) {
        queryParams.due_date_start = filters.value.due_date_range[0]
        queryParams.due_date_end = filters.value.due_date_range[1]
      }
      
      if (filters.value.created_at_range && filters.value.created_at_range.length === 2) {
        queryParams.created_at_start = filters.value.created_at_range[0]
        queryParams.created_at_end = filters.value.created_at_range[1]
      }
      
      if (filters.value.updated_at_range && filters.value.updated_at_range.length === 2) {
        queryParams.updated_at_start = filters.value.updated_at_range[0]
        queryParams.updated_at_end = filters.value.updated_at_range[1]
      }
      
      await loadTasks(queryParams)
    }

    const resetFilters = () => {
      filters.value = {
        case_number: '',
        category_id: '',
        form_name: '',
        title: '',
        description: '',
        requester: '',
        status: '',
        priority: '',
        due_date_range: [],
        created_at_range: [],
        updated_at_range: []
      }
      loadTasks()
    }

    const exportCSV = () => {
      if (filteredTasks.value.length === 0) {
        ElMessage.warning('沒有資料可以匯出')
        return
      }

      // CSV 標頭
      const headers = [
        '流水號',
        '案號',
        '案件類別',
        '表單名稱',
        '任務標題',
        '描述',
        '聲請人',
        '狀態',
        '優先級',
        '截止日期',
        '建立時間',
        '異動時間'
      ]

      // 轉換資料
      const csvData = filteredTasks.value.map((task, index) => [
        index + 1,
        task.case_number || '',
        task.category_name || '',
        task.form_name || '',
        task.title || '',
        task.description || '',
        task.requester || '',
        getStatusText(task.status),
        getPriorityText(task.priority),
        task.due_date || '',
        formatDateTime(task.created_at),
        formatDateTime(task.updated_at)
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
      link.setAttribute('download', `任務清單_${timestamp}.csv`)
      
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      ElMessage.success(`已匯出 ${filteredTasks.value.length} 筆資料`)
    }

    onMounted(() => {
      loadTasks()
      loadCategories()
    })

    return {
      tasks,
      categories,
      showAddDialog,
      isEdit,
      taskForm,
      taskRules,
      taskFormRef,
      searchKeyword,
      filteredTasks,
      showFilters,
      filters,
      toggleFilters,
      searchTasks,
      resetFilters,
      exportCSV,
      resetForm,
      submitTask,
      editTask,
      deleteTask,
      getStatusType,
      getStatusText,
      getPriorityType,
      getPriorityText,
      formatDateTime,
      handleSearch
    }
  }
}
</script>