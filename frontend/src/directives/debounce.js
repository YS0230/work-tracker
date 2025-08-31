// Vue 3 防連點指令
const vDebounce = {
  mounted(el, binding) {
    let timeoutId = null
    let isProcessing = false
    const delay = binding.value || 1000 // 預設防連點時間 1 秒
    
    // 創建防連點處理器
    const debounceHandler = function(event) {
      // 如果正在處理中，阻止執行
      if (isProcessing) {
        event.preventDefault()
        event.stopPropagation()
        return false
      }
      
      // 設置處理狀態
      isProcessing = true
      
      // 添加視覺反饋
      const isElementPlusButton = el.classList.contains('el-button')
      let originalDisabled = el.disabled
      let originalOpacity = el.style.opacity
      let originalCursor = el.style.cursor
      
      if (isElementPlusButton) {
        // Element Plus 按鈕添加 loading 狀態
        el.classList.add('is-loading')
      } else {
        // 普通按鈕禁用狀態
        el.disabled = true
        el.style.opacity = '0.6'
        el.style.cursor = 'not-allowed'
      }
      
      // 恢復按鈕狀態的函數
      const restoreButton = () => {
        if (isElementPlusButton) {
          el.classList.remove('is-loading')
        } else {
          el.disabled = originalDisabled
          el.style.opacity = originalOpacity
          el.style.cursor = originalCursor
        }
        isProcessing = false
      }
      
      // 設置冷卻時間
      timeoutId = setTimeout(restoreButton, delay)
      
      // 保存恢復函數供外部調用
      el._debounceRestore = restoreButton
    }
    
    // 添加事件監聽器
    el.addEventListener('click', debounceHandler, true)
    
    // 保存配置到元素上
    el._debounceConfig = {
      handler: debounceHandler,
      timeoutId: () => timeoutId,
      isProcessing: () => isProcessing
    }
  },
  
  unmounted(el) {
    // 清理定時器
    if (el._debounceConfig && el._debounceConfig.timeoutId()) {
      clearTimeout(el._debounceConfig.timeoutId())
    }
    
    // 移除事件監聽器
    if (el._debounceConfig && el._debounceConfig.handler) {
      el.removeEventListener('click', el._debounceConfig.handler, true)
    }
    
    // 恢復按鈕狀態
    if (el._debounceRestore) {
      el._debounceRestore()
      delete el._debounceRestore
    }
    
    // 清理配置
    delete el._debounceConfig
  },
  
  updated(el, binding) {
    // 如果延遲時間發生變化，更新配置
    if (el._debounceConfig) {
      el._debounceConfig.delay = binding.value || 1000
    }
  }
}

// 創建一個更簡單的防連點工具函數
export const createDebounce = (fn, delay = 1000) => {
  let timeoutId = null
  let isProcessing = false
  
  return function(...args) {
    if (isProcessing) {
      console.log('防連點：操作正在進行中，請稍候')
      return false
    }
    
    isProcessing = true
    
    // 執行原函數
    const result = fn.apply(this, args)
    
    // 設置冷卻期
    timeoutId = setTimeout(() => {
      isProcessing = false
      timeoutId = null
    }, delay)
    
    return result
  }
}

// 按鈕防連點 Composable
export const useDebounceButton = (delay = 1000) => {
  let timeoutId = null
  let isProcessing = false
  
  const execute = (fn, ...args) => {
    if (isProcessing) {
      console.log('按鈕防連點：請等待操作完成')
      return false
    }
    
    isProcessing = true
    
    try {
      const result = fn.apply(null, args)
      
      // 如果返回 Promise，等待完成後再解除限制
      if (result && typeof result.then === 'function') {
        result.finally(() => {
          timeoutId = setTimeout(() => {
            isProcessing = false
            timeoutId = null
          }, delay)
        })
      } else {
        timeoutId = setTimeout(() => {
          isProcessing = false
          timeoutId = null
        }, delay)
      }
      
      return result
    } catch (error) {
      // 發生錯誤時立即解除限制
      isProcessing = false
      throw error
    }
  }
  
  const isDisabled = () => isProcessing
  
  // 手動重置狀態
  const reset = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
    isProcessing = false
  }
  
  return {
    execute,
    isDisabled,
    reset
  }
}

export default vDebounce