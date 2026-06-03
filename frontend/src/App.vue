<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-inner">
        <div class="nav-brand" @click="goHome">
          <span class="nav-logo">📚</span>
          <span class="nav-title">图书馆智能助手</span>
        </div>
        <div class="nav-links">
          <button
            :class="['nav-link', { active: currentView === 'home' }]"
            @click="goHome"
          >
            🏠 首页
          </button>
          <button
            :class="['nav-link', { active: currentView === 'chat' }]"
            @click="goChat"
          >
            💬 智能问答
          </button>
        </div>
      </div>
    </nav>

    <!-- 页面内容 -->
    <main class="main-content">
      <!-- 首页 -->
      <div v-if="currentView === 'home'" class="home-page">
        <div class="hero">
          <div class="hero-icon">📚</div>
          <h1>欢迎来到图书馆智能助手</h1>
          <p>馆藏 2000+ 本图书，覆盖 14 个分类，智能查书、推荐、规则问答一站式服务</p>
          <button class="hero-btn" @click="goChat">💬 开始对话</button>
        </div>

        <div class="features">
          <div class="feature-card" @click="goChat">
            <div class="feature-icon">🔍</div>
            <h3>智能查书</h3>
            <p>按书名、作者、分类快速查找馆藏图书，支持模糊搜索</p>
          </div>
          <div class="feature-card" @click="goChat">
            <div class="feature-icon">🎯</div>
            <h3>分类推荐</h3>
            <p>14 个分类，一键推荐精选好书，找到你的下一本阅读目标</p>
          </div>
          <div class="feature-card" @click="goChat">
            <div class="feature-icon">📋</div>
            <h3>规则问答</h3>
            <p>借阅规则、开放时间、罚款政策，随时为你解答</p>
          </div>
        </div>

        <div class="stats">
          <div class="stat-item">
            <span class="stat-num">2,000+</span>
            <span class="stat-label">馆藏图书</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">14</span>
            <span class="stat-label">分类覆盖</span>
          </div>
          <div class="stat-item">
            <span class="stat-num">24/7</span>
            <span class="stat-label">智能服务</span>
          </div>
        </div>
      </div>

      <!-- 问答页 -->
      <ChatBox v-if="currentView === 'chat'" @go-home="goHome" />
    </main>
  </div>
</template>

<script>
import ChatBox from './components/ChatBox.vue'

export default {
  name: 'App',
  components: { ChatBox },
  data() {
    return {
      currentView: 'home'
    }
  },
  methods: {
    goHome() {
      this.currentView = 'home'
    },
    goChat() {
      this.currentView = 'chat'
    }
  }
}
</script>

<style>
/* 全局重置 */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #f5f7fa; color: #333; }

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 导航栏 */
.navbar {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.nav-inner {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 56px;
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
  transition: opacity 0.2s;
}
.nav-brand:hover { opacity: 0.8; }
.nav-logo { font-size: 26px; }
.nav-title {
  font-size: 17px;
  font-weight: 600;
  color: #1a1a1a;
}
.nav-links {
  display: flex;
  gap: 4px;
}
.nav-link {
  padding: 8px 18px;
  border: none;
  border-radius: 8px;
  background: transparent;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.nav-link:hover {
  background: #f0f4ff;
  color: #4a90d9;
}
.nav-link.active {
  background: #e8f0fe;
  color: #4a90d9;
  font-weight: 600;
}

/* 主内容 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 首页 */
.home-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 24px 60px;
}

.hero {
  text-align: center;
  padding: 60px 20px 40px;
  max-width: 600px;
}
.hero-icon { font-size: 64px; margin-bottom: 16px; }
.hero h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 12px;
}
.hero p {
  font-size: 15px;
  color: #777;
  line-height: 1.7;
  margin-bottom: 28px;
}
.hero-btn {
  padding: 14px 36px;
  border: none;
  border-radius: 28px;
  background: #4a90d9;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 14px rgba(74, 144, 217, 0.3);
}
.hero-btn:hover {
  background: #357abd;
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(74, 144, 217, 0.4);
}

/* 功能卡片 */
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  max-width: 800px;
  width: 100%;
  margin-bottom: 48px;
}
.feature-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 16px;
  padding: 28px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s;
}
.feature-card:hover {
  border-color: #4a90d9;
  box-shadow: 0 4px 16px rgba(74, 144, 217, 0.12);
  transform: translateY(-2px);
}
.feature-icon { font-size: 40px; margin-bottom: 12px; }
.feature-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}
.feature-card p {
  font-size: 13px;
  color: #999;
  line-height: 1.6;
}

/* 统计 */
.stats {
  display: flex;
  gap: 40px;
}
.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.stat-num {
  font-size: 32px;
  font-weight: 700;
  color: #4a90d9;
}
.stat-label {
  font-size: 13px;
  color: #999;
}

/* 响应式 */
@media (max-width: 640px) {
  .features {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .hero h1 { font-size: 22px; }
  .hero { padding: 30px 12px 24px; }
  .stats { gap: 24px; }
  .stat-num { font-size: 26px; }
  .nav-title { font-size: 15px; }
  .nav-link { padding: 6px 12px; font-size: 13px; }
}
</style>
