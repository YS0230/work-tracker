<template>
  <el-container style="height: 100vh">
    <el-header style="background: #409EFF; color: white; line-height: 60px">
      <h2 style="margin: 0">工作事項記錄系統</h2>
    </el-header>
    
    <el-container>
      <el-aside width="200px" style="background: #f5f5f5">
        <el-menu
          :default-active="$route.path"
          router
          background-color="#f5f5f5"
        >
          <el-menu-item index="/tasks">
            <span>任務管理</span>
          </el-menu-item>
          <el-menu-item index="/work-logs">
            <span>工作紀錄</span>
          </el-menu-item>
          <el-menu-item index="/categories">
            <span>類別維護</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Microsoft JhengHei', sans-serif;
  font-size: 13px;
}

.el-table {
  font-size: 13px;
}

.el-form-item__label {
  font-size: 13px;
}

.el-input__inner,
.el-textarea__inner,
.el-select .el-input__inner,
.el-date-editor.el-input {
  font-size: 13px;
}
</style>