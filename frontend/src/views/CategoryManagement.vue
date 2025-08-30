<template>
  <div>
    <el-row style="margin-bottom: 20px">
      <el-col :span="24">
        <el-button type="primary" @click="showAddDialog = true">新增類別</el-button>
      </el-col>
    </el-row>

    <!-- 類別列表 -->
    <el-table :data="categories" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="類別名稱" />
      <el-table-column prop="active" label="狀態" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.active ? 'success' : 'danger'">
            {{ scope.row.active ? '啟用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="建立時間" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新時間" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button size="small" @click="editCategory(scope.row)">編輯</el-button>
          <el-button 
            size="small" 
            :type="scope.row.active ? 'warning' : 'success'"
            @click="toggleCategory(scope.row)"
          >
            {{ scope.row.active ? '停用' : '啟用' }}
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="deleteCategory(scope.row.id)"
            :disabled="scope.row.active"
          >
            刪除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/編輯類別對話框 -->
    <el-dialog
      :title="isEdit ? '編輯類別' : '新增類別'"
      v-model="showAddDialog"
      width="400px"
    >
      <el-form :model="categoryForm" :rules="categoryRules" ref="categoryFormRef" label-width="100px">
        <el-form-item label="類別名稱" prop="name">
          <el-input v-model="categoryForm.name" />
        </el-form-item>
        
        <el-form-item label="狀態" v-if="isEdit">
          <el-switch
            v-model="categoryForm.active"
            active-text="啟用"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitCategory">確定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { categoryApi } from '../api'

export default {
  name: 'CategoryManagement',
  setup() {
    const categories = ref([])
    const showAddDialog = ref(false)
    const isEdit = ref(false)
    const categoryFormRef = ref(null)

    const categoryForm = reactive({
      id: null,
      name: '',
      active: true
    })

    const categoryRules = {
      name: [{ required: true, message: '請輸入類別名稱', trigger: 'blur' }]
    }

    const resetForm = () => {
      Object.assign(categoryForm, {
        id: null,
        name: '',
        active: true
      })
      isEdit.value = false
    }

    const loadCategories = async () => {
      try {
        const response = await categoryApi.getAll()
        categories.value = response.data
      } catch (error) {
        ElMessage.error('載入類別失敗')
      }
    }

    const submitCategory = async () => {
      try {
        await categoryFormRef.value.validate()
        
        const data = {
          name: categoryForm.name,
          active: categoryForm.active
        }

        if (isEdit.value) {
          await categoryApi.update(categoryForm.id, data)
          ElMessage.success('更新成功')
        } else {
          await categoryApi.create(data)
          ElMessage.success('新增成功')
        }

        showAddDialog.value = false
        resetForm()
        loadCategories()
      } catch (error) {
        if (error.response) {
          ElMessage.error('操作失敗')
        }
      }
    }

    const editCategory = (category) => {
      isEdit.value = true
      Object.assign(categoryForm, category)
      showAddDialog.value = true
    }

    const toggleCategory = async (category) => {
      try {
        const action = category.active ? '停用' : '啟用'
        await ElMessageBox.confirm(`確定要${action}這個類別嗎？`, '確認', {
          confirmButtonText: '確定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await categoryApi.update(category.id, { 
          name: category.name,
          active: !category.active 
        })
        
        ElMessage.success(`${action}成功`)
        loadCategories()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('操作失敗')
        }
      }
    }

    const deleteCategory = async (categoryId) => {
      try {
        await ElMessageBox.confirm('確定要刪除這個類別嗎？', '確認', {
          confirmButtonText: '確定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await categoryApi.delete(categoryId)
        ElMessage.success('刪除成功')
        loadCategories()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('刪除失敗')
        }
      }
    }

    const formatDateTime = (dateTime) => {
      if (!dateTime) return ''
      return new Date(dateTime).toLocaleString('zh-TW')
    }

    onMounted(() => {
      loadCategories()
    })

    return {
      categories,
      showAddDialog,
      isEdit,
      categoryForm,
      categoryRules,
      categoryFormRef,
      resetForm,
      submitCategory,
      editCategory,
      toggleCategory,
      deleteCategory,
      formatDateTime
    }
  }
}
</script>