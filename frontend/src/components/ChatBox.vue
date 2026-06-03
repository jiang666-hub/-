<template>
  <div class="chat-container">
    <!-- 头部 -->
    <header class="chat-header">
      <div class="header-left">
        <div class="logo">📚</div>
        <div>
          <h1>智能问答</h1>
          <p>查书、推荐、规则问答，随时为你服务</p>
        </div>
      </div>
      <div class="header-right">
        <button class="back-home-btn" @click="$emit('go-home')">
          🏠 返回首页
        </button>
        <span class="status-dot"></span>
        在线
      </div>
    </header>

    <!-- 快捷功能区（始终显示） -->
    <div class="quick-panel">
      <!-- 功能按钮行 -->
      <div class="func-btns">
        <button
          :class="['func-btn', { active: activeMode === 'recommend' }]"
          @click="toggleMode('recommend')"
        >
          🎯 分类推荐
        </button>
        <button
          :class="['func-btn', { active: activeMode === 'opentime' }]"
          @click="handleOpenTime"
        >
          ⏰ 开放时间
        </button>
        <button
          :class="['func-btn', { active: activeMode === 'rules' }]"
          @click="handleBorrowRules"
        >
          📋 借阅规则
        </button>
        <button
          :class="['func-btn', { active: activeMode === 'search' }]"
          @click="toggleMode('search')"
        >
          🔍 查书
        </button>
      </div>

      <!-- 分类推荐展开区 -->
      <div class="category-panel" v-if="activeMode === 'recommend'">
        <p class="panel-hint">点击分类，随机推荐该类型好书：</p>
        <div class="category-tags">
          <button
            v-for="cat in quickCategories"
            :key="cat"
            :class="['cat-tag', { active: selectedCategory === cat }]"
            @click="recommendCategory(cat)"
          >{{ cat }}</button>
        </div>
      </div>

      <!-- 查书模式提示 -->
      <div class="search-panel" v-if="activeMode === 'search'">
        <p class="panel-hint">在下方输入书名、作者或关键词来查找图书：</p>
        <div class="search-suggestions">
          <button
            v-for="kw in searchSuggestions"
            :key="kw"
            class="suggestion-tag"
            @click="quickAsk(kw)"
          >{{ kw }}</button>
        </div>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="messages" ref="messagesRef">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        :class="['message', msg.role]"
      >
        <div class="avatar" v-if="msg.role === 'assistant'">🤖</div>
        <div class="bubble">
          <div class="content" v-html="formatContent(msg.content)"></div>
          <!-- 图书卡片 -->
          <div class="book-cards" v-if="msg.books && msg.books.length > 0">
            <div
              class="book-card"
              v-for="book in msg.books"
              :key="book.id"
              @click="showBookDetail(book)"
            >
              <div class="book-cover">
                <img
                  v-if="book.cover_url"
                  :src="book.cover_url"
                  :alt="book.title"
                  @error="handleImgError"
                />
                <div class="cover-placeholder" v-else>
                  {{ book.title[0] }}
                </div>
              </div>
              <div class="book-info">
                <h4>{{ book.title }}</h4>
                <p class="author">{{ book.author }}</p>
                <p class="location">📍 {{ book.location }}</p>
                <p class="stock" :class="{ low: book.available <= 2 }">
                  📦 可借 {{ book.available }}/{{ book.stock }} 本
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="avatar" v-if="msg.role === 'user'">👤</div>
      </div>

      <!-- 打字指示器 -->
      <div class="message assistant" v-if="loading">
        <div class="avatar">🤖</div>
        <div class="bubble typing">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="input-area">
      <div class="input-wrapper">
        <input
          v-model="input"
          @keydown.enter="send"
          :placeholder="inputPlaceholder"
          :disabled="loading"
          ref="inputRef"
        />
        <button @click="send" :disabled="!input.trim() || loading">
          <span v-if="!loading">发送</span>
          <span v-else>...</span>
        </button>
      </div>
    </div>

    <!-- 图书详情弹窗 -->
    <div class="modal-overlay" v-if="selectedBook" @click.self="selectedBook = null">
      <div class="modal">
        <button class="modal-close" @click="selectedBook = null">✕</button>
        <div class="modal-content">
          <div class="modal-cover">
            <img
              v-if="selectedBook.cover_url"
              :src="selectedBook.cover_url"
              :alt="selectedBook.title"
            />
            <div class="cover-placeholder large" v-else>
              {{ selectedBook.title[0] }}
            </div>
          </div>
          <div class="modal-info">
            <h2>{{ selectedBook.title }}</h2>
            <p><strong>作者：</strong>{{ selectedBook.author }}</p>
            <p><strong>出版社：</strong>{{ selectedBook.publisher }}</p>
            <p><strong>出版年份：</strong>{{ selectedBook.publish_year }}</p>
            <p><strong>分类：</strong>{{ selectedBook.category }}</p>
            <p><strong>位置：</strong>📍 {{ selectedBook.location }}</p>
            <p><strong>索书号：</strong>{{ selectedBook.shelf_number }}</p>
            <p><strong>馆藏状态：</strong>
              📦 共 {{ selectedBook.stock }} 本，可借 {{ selectedBook.available }} 本
            </p>
            <p class="description"><strong>简介：</strong>{{ selectedBook.description }}</p>
            <div class="tags">
              <span class="tag" v-for="tag in selectedBook.tags" :key="tag">
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick, onMounted, computed } from 'vue'
import { sendMessage } from '../api/index.js'

export default {
  name: 'ChatBox',
  emits: ['go-home'],
  setup() {
    const messages = ref([])
    const input = ref('')
    const loading = ref(false)
    const selectedBook = ref(null)
    const selectedCategory = ref(null)
    const activeMode = ref(null)
    const messagesRef = ref(null)
    const inputRef = ref(null)

    const quickCategories = [
      '计算机', '文学', '历史', '数学', '物理',
      '哲学', '经济', '科幻', '艺术', '心理',
      '教育', '法律', '医学', '自然科学'
    ]

    const searchSuggestions = [
      '《三体》', '《活着》', '《百年孤独》', 'Python', 'Java', '数据结构'
    ]

    const inputPlaceholder = computed(() => {
      if (activeMode.value === 'search') return '输入书名、作者或关键词查找...'
      return '输入你想问的问题...'
    })

    function scrollToBottom() {
      nextTick(() => {
        if (messagesRef.value) {
          messagesRef.value.scrollTop = messagesRef.value.scrollHeight
        }
      })
    }

    // 通用发送方法
    async function doSend(text, category = null) {
      loading.value = true
      scrollToBottom()

      try {
        const history = messages.value.slice(0, -1).map(m => ({
          role: m.role,
          content: m.content
        }))

        const res = await sendMessage(text, history, category)
        const data = res.data

        messages.value.push({
          role: 'assistant',
          content: data.answer,
          books: data.books || [],
          source: data.source
        })
      } catch (err) {
        messages.value.push({
          role: 'assistant',
          content: '抱歉，服务暂时不可用，请稍后再试。',
          books: [],
          source: 'error'
        })
      } finally {
        loading.value = false
        scrollToBottom()
      }
    }

    async function send() {
      const text = input.value.trim()
      if (!text || loading.value) return

      messages.value.push({ role: 'user', content: text })
      input.value = ''
      await doSend(text, selectedCategory.value)
    }

    function quickAsk(text) {
      messages.value.push({ role: 'user', content: text })
      doSend(text, selectedCategory.value)
    }

    // 切换功能模式
    function toggleMode(mode) {
      if (activeMode.value === mode) {
        activeMode.value = null
        selectedCategory.value = null
      } else {
        activeMode.value = mode
        if (mode === 'search') {
          inputRef.value?.focus()
        }
      }
    }

    // 点击分类标签 - 随机推荐
    function recommendCategory(cat) {
      selectedCategory.value = cat
      activeMode.value = 'recommend'

      messages.value.push({ role: 'user', content: `🎯 推荐 ${cat} 类的书` })
      doSend(`推荐 ${cat} 类的书`, cat)
    }

    // 开放时间
    function handleOpenTime() {
      activeMode.value = 'opentime'
      messages.value.push({ role: 'user', content: '⏰ 图书馆开放时间' })
      doSend('图书馆开放时间是几点到几点？')
    }

    // 借阅规则
    function handleBorrowRules() {
      activeMode.value = 'rules'
      messages.value.push({ role: 'user', content: '📋 借阅规则' })
      doSend('借书的规则是什么？能借多久？')
    }

    function showBookDetail(book) {
      selectedBook.value = book
    }

    function formatContent(text) {
      if (!text) return ''
      return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    }

    function handleImgError(e) {
      e.target.style.display = 'none'
      e.target.nextElementSibling.style.display = 'flex'
    }

    onMounted(() => {
      messages.value.push({
        role: 'assistant',
        content: '你好！我是图书馆智能助手 🤖\n\n点击上方按钮快速体验：\n🎯 **分类推荐** - 选分类，随机推荐好书\n⏰ **开放时间** - 查看图书馆开放时间\n📋 **借阅规则** - 了解借书规则\n🔍 **查书** - 按书名/作者查找\n\n也可以直接在下方输入任何问题！',
        books: [],
        source: 'welcome'
      })
    })

    return {
      messages, input, loading, selectedBook, selectedCategory, activeMode,
      messagesRef, inputRef, quickCategories, searchSuggestions, inputPlaceholder,
      send, quickAsk, toggleMode, recommendCategory, handleOpenTime, handleBorrowRules,
      showBookDetail, formatContent, handleImgError
    }
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 56px); /* 减去导航栏高度 */
  max-width: 800px;
  margin: 0 auto;
  background: #fff;
}

/* 头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  border-bottom: 1px solid #eee;
  background: #fff;
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.logo { font-size: 28px; }
.header-left h1 { font-size: 17px; color: #1a1a1a; }
.header-left p { font-size: 12px; color: #999; margin-top: 2px; }
.header-right { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #52c41a; }
.back-home-btn {
  padding: 5px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
  font-size: 12px;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.back-home-btn:hover {
  border-color: #4a90d9;
  color: #4a90d9;
  background: #f0f7ff;
}
.status-dot { width: 8px; height: 8px; background: #52c41a; border-radius: 50%; }

/* 快捷功能区 */
.quick-panel {
  padding: 12px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafbfc;
  flex-shrink: 0;
}

/* 功能按钮行 */
.func-btns {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.func-btn {
  padding: 8px 16px;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px;
  background: #fff;
  font-size: 13px;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.func-btn:hover {
  border-color: #4a90d9;
  color: #4a90d9;
  background: #f5f9ff;
}
.func-btn.active {
  border-color: #4a90d9;
  background: #4a90d9;
  color: #fff;
  font-weight: 600;
}

/* 分类面板 */
.category-panel {
  margin-top: 12px;
  padding: 12px 14px;
  background: #fff;
  border: 1px solid #e8ecf1;
  border-radius: 10px;
  animation: slideDown 0.2s ease;
}
.panel-hint {
  font-size: 12px;
  color: #999;
  margin-bottom: 10px;
}
.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.cat-tag {
  padding: 6px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 18px;
  background: #fafafa;
  font-size: 13px;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.cat-tag:hover {
  border-color: #4a90d9;
  color: #4a90d9;
  background: #f0f7ff;
}
.cat-tag.active {
  border-color: #4a90d9;
  color: #fff;
  background: #4a90d9;
}

/* 查书面板 */
.search-panel {
  margin-top: 12px;
  padding: 12px 14px;
  background: #fff;
  border: 1px solid #e8ecf1;
  border-radius: 10px;
  animation: slideDown 0.2s ease;
}
.search-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}
.suggestion-tag {
  padding: 5px 12px;
  border: 1px dashed #d0d5dd;
  border-radius: 16px;
  background: #fafafa;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}
.suggestion-tag:hover {
  border-color: #4a90d9;
  border-style: solid;
  color: #4a90d9;
  background: #f5f9ff;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 消息区域 */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}
.message {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: flex-start;
}
.message.user { flex-direction: row-reverse; }
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background: #f5f5f5;
  flex-shrink: 0;
}
.bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.7;
}
.message.user .bubble {
  background: #4a90d9;
  color: #fff;
  border-bottom-right-radius: 4px;
}
.message.assistant .bubble {
  background: #f5f7fa;
  color: #333;
  border-bottom-left-radius: 4px;
}
.content strong {
  font-weight: 600;
}

/* 打字指示器 */
.typing {
  display: flex;
  gap: 4px;
  padding: 14px 16px !important;
}
.typing span {
  width: 6px;
  height: 6px;
  background: #bbb;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: scale(1); }
  30% { opacity: 1; transform: scale(1.2); }
}

/* 图书卡片 */
.book-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
}
.book-card {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #fff;
  border: 1px solid #eee;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}
.book-card:hover {
  border-color: #4a90d9;
  box-shadow: 0 2px 8px rgba(74, 144, 217, 0.15);
}
.book-cover {
  width: 60px;
  height: 80px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f0f0f0;
}
.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  color: #4a90d9;
  background: #e8f0fe;
}
.cover-placeholder.large {
  width: 140px;
  height: 190px;
  font-size: 48px;
  border-radius: 8px;
}
.book-info h4 {
  font-size: 14px;
  color: #1a1a1a;
  margin-bottom: 4px;
}
.book-info .author {
  font-size: 12px;
  color: #888;
  margin-bottom: 4px;
}
.book-info .location {
  font-size: 12px;
  color: #666;
  margin-bottom: 2px;
}
.book-info .stock {
  font-size: 12px;
  color: #52c41a;
}
.book-info .stock.low { color: #faad14; }

/* 输入框 */
.input-area {
  padding: 12px 24px 16px;
  border-top: 1px solid #eee;
  background: #fff;
  flex-shrink: 0;
}
.input-wrapper {
  display: flex;
  gap: 10px;
}
.input-wrapper input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}
.input-wrapper input:focus {
  border-color: #4a90d9;
}
.input-wrapper button {
  padding: 10px 22px;
  border: none;
  border-radius: 24px;
  background: #4a90d9;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}
.input-wrapper button:hover { background: #357abd; }
.input-wrapper button:disabled { background: #ccc; cursor: not-allowed; }

/* 弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
.modal {
  background: #fff;
  border-radius: 16px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}
.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: #f0f0f0;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content {
  display: flex;
  gap: 20px;
  padding: 30px;
}
.modal-cover {
  flex-shrink: 0;
}
.modal-cover img {
  width: 140px;
  height: 190px;
  object-fit: cover;
  border-radius: 8px;
}
.modal-info h2 { font-size: 18px; margin-bottom: 12px; }
.modal-info p { font-size: 13px; color: #555; margin-bottom: 6px; line-height: 1.6; }
.modal-info .description { color: #333; margin-top: 8px; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.tag {
  padding: 3px 10px;
  background: #e8f0fe;
  color: #4a90d9;
  border-radius: 12px;
  font-size: 12px;
}

/* 响应式 */
@media (max-width: 640px) {
  .func-btns { gap: 6px; }
  .func-btn { padding: 6px 12px; font-size: 12px; }
}
</style>
