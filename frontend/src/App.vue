<template>
  <el-container style="height: 100vh">
    <el-header style="background: #409EFF; color: white; padding: 0">
      <div style="display: flex; align-items: center; height: 100%; padding: 0 20px">
        <h2 style="margin: 0; margin-right: 40px">工作事項記錄系統</h2>
        <el-menu
          :default-active="$route.path"
          mode="horizontal"
          router
          background-color="#409EFF"
          text-color="white"
          active-text-color="#FFD700"
          style="flex: 1; border-bottom: none"
        >
          <el-menu-item index="/task-dashboard">
            <span>任務儀錶板</span>
          </el-menu-item>
          <el-menu-item index="/work-dashboard">
            <span>工作儀錶板</span>
          </el-menu-item>
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
      </div>
    </el-header>
    
    <el-main style="padding: 20px">
      <router-view />
    </el-main>
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