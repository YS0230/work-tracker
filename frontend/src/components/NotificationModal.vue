<template>
  <div v-if="showBirthdayAnimation" class="birthday-overlay" @click="closeBirthday">
    <div class="birthday-container">
      <div class="balloons">
        <div class="balloon balloon1">🎈</div>
        <div class="balloon balloon2">🎈</div>
        <div class="balloon balloon3">🎈</div>
        <div class="balloon balloon4">🎈</div>
        <div class="balloon balloon5">🎈</div>
      </div>
      
      <div class="birthday-message">
        <h1 class="birthday-title">🎉 生日快樂！🎉</h1>
        <p class="birthday-subtitle">Happy Birthday!</p>
        <div class="cake">🎂</div>
        <p class="birthday-wish">願你今天充滿歡樂，未來充滿希望！</p>
        <button @click="closeBirthday" class="close-button">感謝祝福 ❤️</button>
      </div>
      
      <div class="confetti">
        <div class="confetti-piece" v-for="n in 50" :key="n"></div>
      </div>
      
      <div class="fireworks">
        <div class="firework" v-for="n in 6" :key="n"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotificationModal',
  data() {
    return {
      showBirthdayAnimation: false,
      birthdayDate: '01-27' // 設定生日日期 (MM-DD格式，忽略年份)
    }
  },
  mounted() {
    // 重新整理時清除顯示紀錄
    this.clearTodayDisplayRecord()
    
    // 監聽路由變化
    this.$router.afterEach(() => {
      this.checkBirthdayOnNavigation()
    })
    
    // 初始檢查（如果直接訪問首頁）
    this.checkBirthdayOnNavigation()
  },
  methods: {
    checkBirthdayOnNavigation() {
      const today = new Date()
      const todayString = today.toISOString().split('T')[0] // YYYY-MM-DD格式
      const todayMonthDay = String(today.getMonth() + 1).padStart(2, '0') + '-' + String(today.getDate()).padStart(2, '0')
      
      // 檢查是否為設定的生日日期（忽略年份）
      if (todayMonthDay === this.birthdayDate) {
        // 檢查今天是否已經顯示過
        if (!this.hasShownToday(todayString)) {
          this.showBirthdayAnimation = true
          this.playBirthdaySound()
          this.markShownToday(todayString)
        }
      }
    },
    hasShownToday(dateString) {
      const shownDates = JSON.parse(localStorage.getItem('birthdayShown') || '[]')
      return shownDates.includes(dateString)
    },
    markShownToday(dateString) {
      let shownDates = JSON.parse(localStorage.getItem('birthdayShown') || '[]')
      if (!shownDates.includes(dateString)) {
        shownDates.push(dateString)
        localStorage.setItem('birthdayShown', JSON.stringify(shownDates))
      }
    },
    clearTodayDisplayRecord() {
      // 重新整理時清除今天的顯示紀錄
      const today = new Date().toISOString().split('T')[0]
      let shownDates = JSON.parse(localStorage.getItem('birthdayShown') || '[]')
      shownDates = shownDates.filter(date => date !== today)
      localStorage.setItem('birthdayShown', JSON.stringify(shownDates))
    },
    closeBirthday() {
      this.showBirthdayAnimation = false
    },
    playBirthdaySound() {
      // 如果需要音效，可以在這裡加入
      console.log('🎵 生日快樂歌開始播放！')
    }
  }
}
</script>

<style scoped>
.birthday-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24, #f0932b);
  background-size: 400% 400%;
  animation: gradientShift 3s ease infinite;
  z-index: 10000;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

.birthday-container {
  position: relative;
  text-align: center;
  max-width: 600px;
  padding: 40px;
}

.birthday-message {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: bounceIn 1s ease-out;
  position: relative;
  z-index: 2;
}

.birthday-title {
  font-size: 3rem;
  color: #e74c3c;
  margin-bottom: 20px;
  animation: pulse 2s ease-in-out infinite;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.birthday-subtitle {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
  font-weight: 300;
}

.cake {
  font-size: 4rem;
  margin: 20px 0;
  animation: spin 3s linear infinite;
  display: inline-block;
}

.birthday-wish {
  font-size: 1.2rem;
  color: #34495e;
  margin-bottom: 30px;
  line-height: 1.6;
}

.close-button {
  background: linear-gradient(45deg, #e74c3c, #f39c12);
  color: white;
  border: none;
  padding: 15px 30px;
  font-size: 1.1rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(231, 76, 60, 0.4);
}

.close-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(231, 76, 60, 0.6);
}

.balloons {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.balloon {
  position: absolute;
  font-size: 2rem;
  animation: float 6s ease-in-out infinite;
}

.balloon1 { top: 10%; left: 10%; animation-delay: 0s; }
.balloon2 { top: 20%; right: 15%; animation-delay: 1s; }
.balloon3 { top: 15%; left: 20%; animation-delay: 2s; }
.balloon4 { top: 30%; right: 10%; animation-delay: 3s; }
.balloon5 { top: 10%; left: 50%; animation-delay: 4s; }

.confetti {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.confetti-piece {
  position: absolute;
  width: 8px;
  height: 8px;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24, #f0932b);
  animation: confettiFall 3s linear infinite;
}

.confetti-piece:nth-child(odd) { background: #e74c3c; }
.confetti-piece:nth-child(even) { background: #f39c12; }
.confetti-piece:nth-child(3n) { background: #3498db; }
.confetti-piece:nth-child(4n) { background: #2ecc71; }
.confetti-piece:nth-child(5n) { background: #9b59b6; }

.fireworks {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.firework {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #fff;
  border-radius: 50%;
  animation: fireworkExplode 2s ease-out infinite;
}

.firework:nth-child(1) { top: 20%; left: 20%; animation-delay: 0s; }
.firework:nth-child(2) { top: 30%; right: 25%; animation-delay: 0.5s; }
.firework:nth-child(3) { top: 40%; left: 60%; animation-delay: 1s; }
.firework:nth-child(4) { top: 25%; right: 40%; animation-delay: 1.5s; }
.firework:nth-child(5) { top: 35%; left: 30%; animation-delay: 2s; }
.firework:nth-child(6) { top: 45%; right: 30%; animation-delay: 2.5s; }

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3) translateY(-100px);
  }
  50% {
    opacity: 1;
    transform: scale(1.05) translateY(0);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

@keyframes confettiFall {
  0% {
    top: -10px;
    transform: rotateZ(0deg);
    opacity: 1;
  }
  100% {
    top: 100vh;
    transform: rotateZ(720deg);
    opacity: 0;
  }
}

@keyframes fireworkExplode {
  0% {
    opacity: 1;
    transform: scale(0);
    box-shadow: 0 0 0 0 #fff;
  }
  50% {
    opacity: 1;
    transform: scale(1);
    box-shadow: 0 0 20px 10px rgba(255, 255, 255, 0.5);
  }
  100% {
    opacity: 0;
    transform: scale(1.5);
    box-shadow: 0 0 50px 25px rgba(255, 255, 255, 0);
  }
}

/* 為每個五彩紙屑設定隨機位置 */
.confetti-piece:nth-child(1) { left: 5%; animation-delay: 0s; }
.confetti-piece:nth-child(2) { left: 10%; animation-delay: 0.1s; }
.confetti-piece:nth-child(3) { left: 15%; animation-delay: 0.2s; }
.confetti-piece:nth-child(4) { left: 20%; animation-delay: 0.3s; }
.confetti-piece:nth-child(5) { left: 25%; animation-delay: 0.4s; }
.confetti-piece:nth-child(6) { left: 30%; animation-delay: 0.5s; }
.confetti-piece:nth-child(7) { left: 35%; animation-delay: 0.6s; }
.confetti-piece:nth-child(8) { left: 40%; animation-delay: 0.7s; }
.confetti-piece:nth-child(9) { left: 45%; animation-delay: 0.8s; }
.confetti-piece:nth-child(10) { left: 50%; animation-delay: 0.9s; }
.confetti-piece:nth-child(11) { left: 55%; animation-delay: 1s; }
.confetti-piece:nth-child(12) { left: 60%; animation-delay: 1.1s; }
.confetti-piece:nth-child(13) { left: 65%; animation-delay: 1.2s; }
.confetti-piece:nth-child(14) { left: 70%; animation-delay: 1.3s; }
.confetti-piece:nth-child(15) { left: 75%; animation-delay: 1.4s; }
.confetti-piece:nth-child(16) { left: 80%; animation-delay: 1.5s; }
.confetti-piece:nth-child(17) { left: 85%; animation-delay: 1.6s; }
.confetti-piece:nth-child(18) { left: 90%; animation-delay: 1.7s; }
.confetti-piece:nth-child(19) { left: 95%; animation-delay: 1.8s; }
.confetti-piece:nth-child(20) { left: 8%; animation-delay: 1.9s; }
.confetti-piece:nth-child(21) { left: 12%; animation-delay: 2s; }
.confetti-piece:nth-child(22) { left: 18%; animation-delay: 2.1s; }
.confetti-piece:nth-child(23) { left: 22%; animation-delay: 2.2s; }
.confetti-piece:nth-child(24) { left: 28%; animation-delay: 2.3s; }
.confetti-piece:nth-child(25) { left: 32%; animation-delay: 2.4s; }
.confetti-piece:nth-child(26) { left: 38%; animation-delay: 2.5s; }
.confetti-piece:nth-child(27) { left: 42%; animation-delay: 2.6s; }
.confetti-piece:nth-child(28) { left: 48%; animation-delay: 2.7s; }
.confetti-piece:nth-child(29) { left: 52%; animation-delay: 2.8s; }
.confetti-piece:nth-child(30) { left: 58%; animation-delay: 2.9s; }
.confetti-piece:nth-child(31) { left: 62%; animation-delay: 0.5s; }
.confetti-piece:nth-child(32) { left: 68%; animation-delay: 0.6s; }
.confetti-piece:nth-child(33) { left: 72%; animation-delay: 0.7s; }
.confetti-piece:nth-child(34) { left: 78%; animation-delay: 0.8s; }
.confetti-piece:nth-child(35) { left: 82%; animation-delay: 0.9s; }
.confetti-piece:nth-child(36) { left: 88%; animation-delay: 1.0s; }
.confetti-piece:nth-child(37) { left: 92%; animation-delay: 1.1s; }
.confetti-piece:nth-child(38) { left: 3%; animation-delay: 1.2s; }
.confetti-piece:nth-child(39) { left: 7%; animation-delay: 1.3s; }
.confetti-piece:nth-child(40) { left: 13%; animation-delay: 1.4s; }
.confetti-piece:nth-child(41) { left: 17%; animation-delay: 1.5s; }
.confetti-piece:nth-child(42) { left: 23%; animation-delay: 1.6s; }
.confetti-piece:nth-child(43) { left: 27%; animation-delay: 1.7s; }
.confetti-piece:nth-child(44) { left: 33%; animation-delay: 1.8s; }
.confetti-piece:nth-child(45) { left: 37%; animation-delay: 1.9s; }
.confetti-piece:nth-child(46) { left: 43%; animation-delay: 2.0s; }
.confetti-piece:nth-child(47) { left: 47%; animation-delay: 2.1s; }
.confetti-piece:nth-child(48) { left: 53%; animation-delay: 2.2s; }
.confetti-piece:nth-child(49) { left: 57%; animation-delay: 2.3s; }
.confetti-piece:nth-child(50) { left: 63%; animation-delay: 2.4s; }

@media (max-width: 768px) {
  .birthday-title {
    font-size: 2rem;
  }
  
  .birthday-message {
    padding: 20px;
    margin: 20px;
  }
  
  .cake {
    font-size: 3rem;
  }
}
</style>