// Chat widget frontend: abre una ventana en la esquina inferior izquierda y envía mensajes al endpoint /chat/send/
(function(){
  const toggle = document.getElementById('chat-toggle');
  const panel = document.getElementById('chat-panel');
  const closeBtn = document.getElementById('chat-close');
  const sendBtn = document.getElementById('chat-send');
  const input = document.getElementById('chat-input');
  const messages = document.getElementById('chat-messages');
  const optionsBox = document.getElementById('chat-options');

  if(!toggle || !panel) return;

  const userId = toggle.getAttribute('data-user-id') || null;
  const isAuthenticated = toggle.getAttribute('data-authenticated') === '1';

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
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function renderOptions(list){
    if(!optionsBox) return;
    optionsBox.innerHTML = '';
    if(!list || !list.length) return;
    list.forEach(opt => {
      const btn = document.createElement('button');
      btn.className = 'btn btn-sm btn-outline-secondary me-1 mb-1';
      btn.textContent = opt;
      btn.addEventListener('click', function(){ sendOption(opt); });
      optionsBox.appendChild(btn);
    });
  }

  toggle.addEventListener('click', function(){
    const show = panel.style.display !== 'block';
    panel.style.display = show ? 'block' : 'none';
    if(show){
      // Always request greeting from backend so it can provide DB-driven options
      try{
        const body = { message: 'hola' };
        if(userId) body.usuario_id = userId;
        fetch('/chat/send/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/)||[])[1] },
          body: JSON.stringify(body)
        })
        .then(r => r.json())
        .then(payload => {
          if(payload && payload.ok){ appendMessage('bot', payload.reply); renderOptions(payload.suggested || []); }
          else { appendMessage('bot', '¡Hola! Soy el asistente de Adonai. Haz clic en una opción o escríbeme.'); renderOptions(['Productos','Categorías','Delivery','Información','Promociones']); }
        }).catch(()=>{
          appendMessage('bot', '¡Hola! Soy el asistente de Adonai. Haz clic en una opción o escríbeme.'); renderOptions(['Productos','Categorías','Delivery','Información','Promociones']);
        });
      } catch(e){
        appendMessage('bot', '¡Hola! Soy el asistente de Adonai. Haz clic en una opción o escríbeme.'); renderOptions(['Productos','Categorías','Delivery','Información','Promociones']);
      }
    }
  });
  closeBtn.addEventListener('click', function(){ panel.style.display = 'none'; });

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', function(e){ if(e.key === 'Enter') sendMessage(); });

  async function sendOption(optionText){
    appendMessage('me', optionText);
    renderOptions([]);
    try{
      const body = { option: optionText };
      if(userId) body.usuario_id = userId;
      const res = await fetch('/chat/send/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/)||[])[1] },
        body: JSON.stringify(body)
      });
      if(!res.ok){ appendMessage('bot', 'Error al enviar opción.'); return; }
      const payload = await res.json();
      if(payload.ok){ appendMessage('bot', payload.reply); renderOptions(payload.suggested || []); }
      else appendMessage('bot', payload.error || 'Error desconocido');
    } catch(err){ console.error('Chat option error', err); appendMessage('bot', 'Error de conexión'); }
  }

  async function sendMessage(){
    const text = input.value && input.value.trim();
    if(!text) return;
    appendMessage('me', text);
    input.value = '';
    renderOptions([]);

    try{
      const body = { message: text };
      if(userId) body.usuario_id = userId;
      const res = await fetch('/chat/send/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/)||[])[1] },
        body: JSON.stringify(body)
      });
      if(!res.ok){ appendMessage('bot', 'Error al enviar mensaje.'); return; }
      const payload = await res.json();
      if(payload.ok){ appendMessage('bot', payload.reply); renderOptions(payload.suggested || []); }
      else appendMessage('bot', payload.error || 'Error desconocido');
    } catch(err){ console.error('Chat send error', err); appendMessage('bot', 'Error de conexión'); }
  }
})();
