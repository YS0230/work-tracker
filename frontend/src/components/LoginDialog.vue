<template>
  <div v-if="showDialog" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>系統登入</h3>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">帳號：</label>
          <input
            id="username"
            v-model="credentials.username"
            type="text"
            required
            :disabled="loading"
            placeholder="請輸入帳號"
          />
        </div>
        
        <div class="form-group">
          <label for="password">密碼：</label>
          <input
            id="password"
            v-model="credentials.password"
            type="password"
            required
            :disabled="loading"
            placeholder="請輸入密碼"
          />
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <div class="form-actions">
          <button type="submit" :disabled="loading" v-debounce="3000" class="btn-primary">
            {{ loading ? '登入中...' : '登入' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { authApi, setAuthToken } from '../api.js'

export default {
  name: 'LoginDialog',
  data() {
    return {
      showDialog: false,
      credentials: {
        username: '',
        password: ''
      },
      loading: false,
      errorMessage: ''
    }
  },
  mounted() {
    window.addEventListener('auth-required', this.showLoginDialog)
  },
  beforeUnmount() {
    window.removeEventListener('auth-required', this.showLoginDialog)
  },
  methods: {
    showLoginDialog() {
      this.showDialog = true
      this.errorMessage = ''
      this.credentials.username = ''
      this.credentials.password = ''
    },
    hideLoginDialog() {
      this.showDialog = false
      this.errorMessage = ''
    },
    handleOverlayClick() {
      // 防止點擊外層關閉對話框，強制登入
    },
    async handleLogin() {
      if (this.loading) return
      
      this.loading = true
      this.errorMessage = ''
      
      try {
        const response = await authApi.login(
          this.credentials.username,
          this.credentials.password
        )
        
        const { token } = response.data
        setAuthToken(token)
        
        this.hideLoginDialog()
        this.$emit('login-success')
        
        // 通知其他組件登入成功
        window.dispatchEvent(new CustomEvent('auth-success'))
        
      } catch (error) {
        console.error('登入失敗:', error)
        
        if (error.response?.status === 401) {
          this.errorMessage = '帳號或密碼錯誤'
        } else {
          this.errorMessage = '登入失敗，請稍後再試'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-content {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 400px;
  max-width: 90vw;
}

.modal-header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 19px;
  font-weight: 600;
}

.login-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #2c3e50;
  font-weight: 600;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  margin-bottom: 16px;
  font-size: 14px;
  text-align: center;
  padding: 8px;
  background-color: #f8d7da;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
}

.form-actions {
  text-align: center;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-primary:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
</style>