// Chat widget frontend: abre una ventana en la esquina inferior izquierda y envía mensajes al endpoint /chat/send/
(function(){
  const toggle = document.getElementById('chat-toggle');
  const panel = document.getElementById('chat-panel');
  const closeBtn = document.getElementById('chat-close');
  const sendBtn = document.getElementById('chat-send');
  const input = document.getElementById('chat-input');
  const messages = document.getElementById('chat-messages');

  if(!toggle || !panel) return;

  function appendMessage(author, text){
    const el = document.createElement('div');
    el.className = 'mb-2';
    if(author === 'me'){
      el.innerHTML = `<div class="text-end"><div class="d-inline-block p-2 bg-primary text-white rounded">${escapeHtml(text)}</div></div>`;
    } else {
      el.innerHTML = `<div class="text-start"><div class="d-inline-block p-2 bg-light rounded">${escapeHtml(text)}</div></div>`;
    }
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
  }

  function escapeHtml(unsafe) {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  toggle.addEventListener('click', function(){
    panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
  });
  closeBtn.addEventListener('click', function(){ panel.style.display = 'none'; });

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', function(e){ if(e.key === 'Enter') sendMessage(); });

  async function sendMessage(){
    const text = input.value && input.value.trim();
    if(!text) return;
    appendMessage('me', text);
    input.value = '';

    try{
      const res = await fetch('/chat/send/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/)||[])[1] },
        body: JSON.stringify({ message: text })
      });
      if(!res.ok) {
        appendMessage('bot', 'Error al enviar mensaje.');
        return;
      }
      const payload = await res.json();
      if(payload.ok){
        appendMessage('bot', payload.reply);
      } else {
        appendMessage('bot', payload.error || 'Error desconocido');
      }
    } catch(err){
      console.error('Chat send error', err);
      appendMessage('bot', 'Error de conexión');
    }
  }
})();
