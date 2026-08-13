document.addEventListener('DOMContentLoaded', () => {
  // Navigation Tabs
  const navItems = document.querySelectorAll('.nav-item');
  const tabContents = document.querySelectorAll('.tab-content');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetTab = item.getAttribute('data-tab');

      navItems.forEach(i => i.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      item.classList.add('active');
      document.getElementById(`tab-${targetTab}`).classList.add('active');
    });
  });

  // Fetch Stats & Initial Data
  loadStats();
  loadReels();
  loadJobs();
  loadSettings();

  // Poll jobs & reels every 3 seconds
  setInterval(() => {
    loadJobs();
    loadStats();
  }, 3000);

  // Trigger Button Click
  document.getElementById('trigger-btn').addEventListener('click', triggerPipeline);
  document.getElementById('custom-job-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const topic = document.getElementById('input-topic').value;
    const format = document.getElementById('input-format').value;
    triggerPipeline(topic, format);
  });

  // Modal handlers
  document.getElementById('modal-close-btn').addEventListener('click', closeModal);
});

async function loadStats() {
  try {
    const res = await fetch('/api/analytics/summary');
    const data = await res.json();

    document.getElementById('stat-reels').innerText = data.reels_published || '0';
    document.getElementById('stat-views').innerText = data.total_views ? (data.total_views / 1000).toFixed(1) + 'K' : '0';
    document.getElementById('stat-followers').innerText = '+' + (data.followers_gained || 0);
    document.getElementById('stat-qa').innerText = data.qa_pass_rate || '100%';
  } catch (err) {
    console.error('Error loading stats:', err);
  }
}

async function loadReels() {
  try {
    const res = await fetch('/api/reels');
    const reels = await res.json();

    const overviewGrid = document.getElementById('reels-list-overview');
    const fullGrid = document.getElementById('reels-list-full');

    if (!reels || reels.length === 0) {
      const emptyHtml = '<p class="loading-state">No Reels generated yet. Click "Trigger Reel Pipeline" to generate your first Reel!</p>';
      overviewGrid.innerHTML = emptyHtml;
      fullGrid.innerHTML = emptyHtml;
      return;
    }

    const cardsHtml = reels.map(r => `
      <div class="reel-card" onclick="openModal('${r.topic_title.replace(/'/g, "\\'")}', '${r.video_url}', \`${r.caption.replace(/`/g, "\\`")}\`)">
        <img class="reel-cover" src="${r.cover_url || '/static/style.css'}" alt="Reel Cover" onerror="this.src='https://via.placeholder.com/300x533/131822/00E696?text=Flow+Tech+Reel'">
        <div class="reel-info">
          <div class="reel-title">${r.topic_title}</div>
          <div class="reel-meta">
            <span>🛡️ QA: ${r.qa_score}%</span>
            <span>✨ ${r.status}</span>
          </div>
        </div>
      </div>
    `).join('');

    overviewGrid.innerHTML = cardsHtml;
    fullGrid.innerHTML = cardsHtml;
  } catch (err) {
    console.error('Error loading reels:', err);
  }
}

async function loadJobs() {
  try {
    const res = await fetch('/api/jobs');
    const jobs = await res.json();

    if (!jobs || jobs.length === 0) return;

    const latestJob = jobs[0];
    updatePipelineUI(latestJob);
  } catch (err) {
    console.error('Error loading jobs:', err);
  }
}

function updatePipelineUI(job) {
  const badge = document.getElementById('job-status-badge');
  const topicDisplay = document.getElementById('job-topic-display');
  const percentDisplay = document.getElementById('job-progress-percent');
  const progressBar = document.getElementById('job-progress-bar');
  const logsEl = document.getElementById('pipeline-logs');

  badge.innerText = job.status;
  topicDisplay.innerText = job.topic_title ? `Current Topic: "${job.topic_title}"` : 'Autonomous AI Topic Discovery...';
  percentDisplay.innerText = `${job.progress}%`;
  progressBar.style.width = `${job.progress}%`;

  // Update step boxes
  const progressMap = [
    { id: 'step-topic', threshold: 10 },
    { id: 'step-research', threshold: 20 },
    { id: 'step-script', threshold: 30 },
    { id: 'step-code', threshold: 40 },
    { id: 'step-visual', threshold: 50 },
    { id: 'step-voice', threshold: 60 },
    { id: 'step-video', threshold: 75 },
    { id: 'step-qa', threshold: 90 },
    { id: 'step-publish', threshold: 100 }
  ];

  progressMap.forEach(step => {
    const el = document.getElementById(step.id);
    if (!el) return;
    el.classList.remove('completed', 'active');
    if (job.progress > step.threshold) {
      el.classList.add('completed');
    } else if (job.progress === step.threshold) {
      el.classList.add('active');
    }
  });

  // Display logs
  if (job.state && job.state.logs && job.state.logs.length > 0) {
    logsEl.innerText = job.state.logs.join('\n');
    logsEl.scrollTop = logsEl.scrollHeight;
  }
}

async function triggerPipeline(topic = null, format = null) {
  try {
    const payload = {};
    if (topic && typeof topic === 'string') payload.topic = topic;
    if (format && typeof format === 'string') payload.format = format;

    const res = await fetch('/api/jobs/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    alert('🚀 ReelForge AI Multi-Agent Pipeline Triggered Successfully!');
    loadJobs();
  } catch (err) {
    alert('Error triggering pipeline: ' + err.message);
  }
}

async function loadSettings() {
  try {
    const res = await fetch('/api/settings');
    const settings = await res.json();

    const container = document.getElementById('settings-container');
    container.innerHTML = Object.entries(settings).map(([k, v]) => `
      <div style="margin-bottom: 12px; font-size: 14px;">
        <strong>${k.toUpperCase()}:</strong> <span style="color: var(--accent-green);">${v}</span>
      </div>
    `).join('');
  } catch (err) {
    console.error('Error loading settings:', err);
  }
}

function openModal(title, videoUrl, caption) {
  document.getElementById('modal-title').innerText = title;
  const player = document.getElementById('modal-video-player');
  player.src = videoUrl;
  document.getElementById('modal-caption-text').innerText = caption;
  document.getElementById('video-modal').style.display = 'flex';
}

function closeModal() {
  const player = document.getElementById('modal-video-player');
  player.pause();
  document.getElementById('video-modal').style.display = 'none';
}
