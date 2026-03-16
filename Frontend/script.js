
// ══════════════════════════════════════════════════
// CONFIG
// ══════════════════════════════════════════════════
const API_BASE   = 'http://localhost:5000';
const SESSION_ID = 'agro_' + Math.random().toString(36).slice(2, 10);
let   isLoading  = false;

// ══════════════════════════════════════════════════
// INTENT META
// ══════════════════════════════════════════════════
const INTENT_META = {
  crop:        { label: '🌾 Crop Advice',       cls: 'intent-crop' },
  fertilizer:  { label: '🧪 Fertilizer',        cls: 'intent-fertilizer' },
  disease:     { label: '🔬 Disease Alert',      cls: 'intent-disease' },
  weather:     { label: '🌦️ Weather',            cls: 'intent-weather' },
  irrigation:  { label: '💧 Irrigation',         cls: 'intent-irrigation' },
  sustainable: { label: '♻️ Eco Farming',        cls: 'intent-sustainable' },
  general:     { label: '🤝 General Help',       cls: 'intent-general' },
};

// ══════════════════════════════════════════════════
// SEND MESSAGE
// ══════════════════════════════════════════════════
async function sendMessage() {
  const input = document.getElementById('userInput');
  const msg   = input.value.trim();
  if (!msg || isLoading) return;

  hideWelcome();
  addUserMessage(msg);
  input.value = '';
  autoResize(input);
  setLoading(true);

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, session_id: SESSION_ID })
    });

    const data = await res.json();

    if (!res.ok) {
      addBotMessage('❌ ' + (data.error || 'Something went wrong. Please try again.'), 'general', null);
      return;
    }

    addBotMessage(data.reply, data.intent || 'general', data.context);

  } catch (err) {
    addBotMessage(
      '🔌 Cannot connect to AgroMind server. Please make sure the Python backend is running on port 5000.\n\nRun: <strong>cd backend && python app.py</strong>',
      'general', null
    );
  } finally {
    setLoading(false);
  }
}

function sendQuick(text) {
  document.getElementById('userInput').value = text;
  sendMessage();
}

// ══════════════════════════════════════════════════
// MESSAGE RENDERERS
// ══════════════════════════════════════════════════
function hideWelcome() {
  const w = document.getElementById('welcomeState');
  if (w) w.remove();
}

function addUserMessage(text) {
  const chatArea = document.getElementById('chatArea');
  const time = formatTime();
  chatArea.insertAdjacentHTML('beforeend', `
    <div class="message-row user">
      <div class="avatar user-av">You</div>
      <div class="msg-col">
        <div class="bubble user-bubble">${escapeHtml(text)}</div>
        <div class="msg-time">${time}</div>
      </div>
    </div>
  `);
  scrollToBottom();
}

function addBotMessage(text, intent, contextData) {
  removeTyping();
  const chatArea = document.getElementById('chatArea');
  const time  = formatTime();
  const meta  = INTENT_META[intent] || INTENT_META.general;
  const badge = `<div class="intent-tag ${meta.cls}">${meta.label}</div>`;
  const body  = formatMarkdown(text);
  const card  = contextData ? buildDataCard(contextData, intent) : '';

  chatArea.insertAdjacentHTML('beforeend', `
    <div class="message-row bot">
      <div class="avatar bot-av">🌿</div>
      <div class="msg-col">
        ${badge}
        <div class="bubble bot-bubble">${body}${card}</div>
        <div class="msg-time">${time}</div>
      </div>
    </div>
  `);
  scrollToBottom();
}

function showTyping() {
  const chatArea = document.getElementById('chatArea');
  chatArea.insertAdjacentHTML('beforeend', `
    <div class="typing-row" id="typingIndicator">
      <div class="avatar bot-av">🌿</div>
      <div class="typing-bubble">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
  `);
  scrollToBottom();
}

function removeTyping() {
  const t = document.getElementById('typingIndicator');
  if (t) t.remove();
}

// ══════════════════════════════════════════════════
// DATA CARD BUILDER
// ══════════════════════════════════════════════════
function buildDataCard(ctx, intent) {
  if (!ctx || ctx.error) return '';
  let rows = [];

  if (intent === 'crop' || ctx.recommended_crops) {
    if (ctx.season)           rows.push(['Season',    ctx.season]);
    if (ctx.soil_type)        rows.push(['Soil Type', ctx.soil_type]);
    if (ctx.recommended_crops) rows.push(['Top Crops', ctx.recommended_crops.slice(0,4).join(', ')]);
  }

  if (intent === 'fertilizer' && ctx.npk_requirement) {
    const npk = ctx.npk_requirement;
    rows.push(['Crop',       ctx.crop]);
    rows.push(['Area',       ctx.area_hectare + ' ha']);
    rows.push(['Nitrogen',   npk.N_kg + ' kg']);
    rows.push(['Phosphorus', npk.P_kg + ' kg']);
    rows.push(['Potassium',  npk.K_kg + ' kg']);
  }

  if (intent === 'disease' && ctx.disease) {
    rows.push(['Disease',   ctx.disease]);
    if (ctx.commonly_affects) rows.push(['Affects',  ctx.commonly_affects.join(', ')]);
  }

  if (intent === 'irrigation' && ctx.irrigation_interval) {
    rows.push(['Crop',      ctx.crop]);
    rows.push(['Interval',  ctx.irrigation_interval]);
    rows.push(['Method',    ctx.recommended_method]);
    rows.push(['Water/Season', ctx.total_water_requirement]);
  }

  if (!rows.length) return '';

  const rowsHtml = rows.map(([k,v]) =>
    `<div class="data-row"><span class="dk">${k}</span><span class="dv">${v}</span></div>`
  ).join('');

  return `<div class="data-card"><div class="data-card-title">📊 Quick Facts</div>${rowsHtml}</div>`;
}

// ══════════════════════════════════════════════════
// HELPERS
// ══════════════════════════════════════════════════
function setLoading(state) {
  isLoading = state;
  document.getElementById('sendBtn').disabled = state;
  if (state) showTyping();
  else removeTyping();
}

function scrollToBottom() {
  const ca = document.getElementById('chatArea');
  setTimeout(() => { ca.scrollTop = ca.scrollHeight; }, 50);
}

function formatTime() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function formatMarkdown(text) {
  // Escape HTML first, then apply formatting
  let s = text
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

  // Bold **text**
  s = s.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Italic *text*
  s = s.replace(/\*(.*?)\*/g, '<em>$1</em>');
  // Code `text`
  s = s.replace(/`([^`]+)`/g, '<code style="background:rgba(245,200,66,0.12);padding:1px 5px;border-radius:4px;font-size:12px;">$1</code>');
  // Bullet lines
  s = s.replace(/^[•\-] (.+)$/gm, '<li>$1</li>');
  s = s.replace(/(<li>.*<\/li>)+/gs, (m) => '<ul>' + m + '</ul>');
  // Line breaks
  s = s.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
  return '<p>' + s + '</p>';
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 100) + 'px';
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

// ══════════════════════════════════════════════════
// INIT — Welcome bot message after short delay
// ══════════════════════════════════════════════════
window.addEventListener('load', () => {
  document.getElementById('userInput').focus();
});