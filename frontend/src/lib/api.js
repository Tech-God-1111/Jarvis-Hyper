// API helpers for JARVIS-HYPER

const getApiBase = () => {
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000/api';
  }
  return `http://${window.location.hostname}:8000/api`;
};

const API_BASE = getApiBase();
console.log('📍 API URL:', API_BASE);

/**
 * Stream chat with JARVIS - with voice + attachment support
 */
export async function streamChat({ message, attachment, onDelta, onVoice, onDone, onError }) {
  try {
    console.log('🔊 Sending:', message, attachment ? `(+file: ${attachment.name})` : '');

    const response = await fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        speak: true,
        attachment: attachment || null,   // ← SEND THE FILE!
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
    }

    if (!response.body) throw new Error('No response body received');

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.startsWith('data:')) continue;
        const payload = line.slice(5).trim();
        if (!payload) continue;

        try {
          const event = JSON.parse(payload);
          switch (event.type) {
            case 'session':
              console.log('📡 Session:', event.session_id);
              break;
            case 'delta':
              if (onDelta) onDelta(event.content);
              break;
            case 'voice':
              if (onVoice && event.audio) onVoice(event.audio);
              break;
            case 'done':
              if (onDone) onDone();
              break;
            case 'error':
              if (onError) onError(new Error(event.message));
              break;
          }
        } catch (e) {
          console.warn('⚠️ Parse error:', payload);
        }
      }
    }
    if (onDone) onDone();
  } catch (err) {
    console.error('💥 Chat error:', err);
    if (onError) onError(err);
  }
}

export function playAudio(buffer) {
  try {
    const blob = new Blob([buffer], { type: 'audio/mpeg' });
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
    return audio;
  } catch (err) {
    console.error('Audio playback error:', err);
    throw err;
  }
}

export async function checkHealth() {
  try {
    const r = await fetch(`${API_BASE.replace('/api', '')}/health`);
    if (!r.ok) throw new Error('Backend unhealthy');
    return r.json();
  } catch (err) {
    console.error('Health check error:', err);
    throw err;
  }
}