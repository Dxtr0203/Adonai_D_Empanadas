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

  // ==========================
  // Funciones auxiliares
  // ==========================
  function appendMessage(author, text){
    const el = document.createElement('div');
    el.className = 'mb-2';
    const safeText = escapeHtml(text);
    if(author === 'me'){
      el.innerHTML = `<div class="text-end"><div class="d-inline-block p-2 bg-primary text-white rounded">${safeText}</div></div>`;
    } else {
      el.innerHTML = `<div class="text-start"><div class="d-inline-block p-2 bg-light rounded">${safeText}</div></div>`;
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

  // ==========================
  // Abrir / cerrar panel
  // ==========================
  toggle.addEventListener('click', function(){
    const show = panel.style.display !== 'block';
    panel.style.display = show ? 'block' : 'none';
    if(show) onOpen();
  });
  closeBtn.addEventListener('click', function(){ panel.style.display = 'none'; });

  // ==========================
  // Saludo inicial y quick actions
  // ==========================
  function onOpen(){
    const greeted = sessionStorage.getItem('adonai_chat_greeted');
    if(!greeted){
      appendMessage('bot', '¡Hola! 👋 Soy el asistente de Adonai. Puedes escoger una opción rápida o escribir tu pregunta.');
      renderOptions(['Productos','Categorías','Delivery','Información','Promociones']);
      sessionStorage.setItem('adonai_chat_greeted', '1');
    }

    document.querySelectorAll('.quick-action').forEach(btn => {
      btn.removeEventListener('click', quickHandler);
      btn.addEventListener('click', quickHandler);
    });

    input.focus();
  }

  function quickHandler(e){
    const text = e.currentTarget.textContent.trim();
    appendMessage('me', text);
    renderOptions([]);
    setTimeout(() => sendText(text), 50);
  }

  // ==========================
  // Enviar mensaje o acción
  // ==========================
  async function sendText(text){
    if(!text) return;
    try{
      const body = { message: text };
      if(userId) body.usuario_id = userId;
      const res = await fetch('/chat/send/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/)||[])[1] 
        },
        body: JSON.stringify(body)
      });
      if(!res.ok){ appendMessage('bot', 'Error al enviar mensaje.'); return; }
      const payload = await res.json();
      if(payload.ok){ 
        appendMessage('bot', payload.reply); 
        renderOptions(payload.suggested || []); 
      } else appendMessage('bot', payload.error || 'Error desconocido');
    } catch(err){ 
      console.error('Chat send error', err); 
      appendMessage('bot', 'Error de conexión'); 
    }
  }

  async function sendOption(optionText){
    appendMessage('me', optionText);
    renderOptions([]);
    try{
      const body = { option: optionText };
      if(userId) body.usuario_id = userId;
      const res = await fetch('/chat/send/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/)||[])[1] 
        },
        body: JSON.stringify(body)
      });
      if(!res.ok){ appendMessage('bot', 'Error al enviar opción.'); return; }
      const payload = await res.json();
      if(payload.ok){ 
        appendMessage('bot', payload.reply); 
        renderOptions(payload.suggested || []); 
      } else appendMessage('bot', payload.error || 'Error desconocido');
    } catch(err){ 
      console.error('Chat option error', err); 
      appendMessage('bot', 'Error de conexión'); 
    }
  }

  async function sendMessage(){
    const text = input.value && input.value.trim();
    if(!text) return;
    appendMessage('me', text);
    input.value = '';
    renderOptions([]);
    await sendText(text);
  }

  // ==========================
  // Eventos del input
  // ==========================
  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', function(e){ if(e.key === 'Enter') sendMessage(); });

})();
