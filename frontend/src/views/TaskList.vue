<template>
  <div>
    <el-row style="margin-bottom: 20px">
      <el-col :span="24">
        <el-button type="primary" @click="showAddDialog = true">新增任務</el-button>
      </el-col>
    </el-row>

    <!-- 任務列表 -->
    <el-table :data="tasks" border style="width: 100%">
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
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button size="small" @click="editTask(scope.row)">編輯</el-button>
          <el-button size="small" type="danger" @click="deleteTask(scope.row.id)">刪除</el-button>
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
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { taskApi, categoryApi } from '../api'

export default {
  name: 'TaskList',
  setup() {
    const tasks = ref([])
    const categories = ref([])
    const showAddDialog = ref(false)
    const isEdit = ref(false)
    const taskFormRef = ref(null)

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

    const loadTasks = async () => {
      try {
        const response = await taskApi.getAll()
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
      resetForm,
      submitTask,
      editTask,
      deleteTask,
      getStatusType,
      getStatusText,
      getPriorityType,
      getPriorityText
    }
  }
}
</script>