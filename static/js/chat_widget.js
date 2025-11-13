// Chat widget frontend: abre una ventana en la esquina inferior izquierda y envía mensajes al endpoint /chat/send/
(function(){
  const toggle = document.getElementById('chat-toggle');
  const panel = document.getElementById('chat-panel');
  const closeBtn = document.getElementById('chat-close');
  const sendBtn = document.getElementById('chat-send');
  const input = document.getElementById('chat-input');
  const messages = document.getElementById('chat-messages');

  if(!toggle || !panel) return;

  const userIdAttr = toggle.getAttribute('data-user-id');
  const userId = userIdAttr ? parseInt(userIdAttr, 10) : null;
  const isAuthenticated = toggle.getAttribute('data-authenticated') === '1';
  // Toggle to allow anonymous users to request "Atención Personalizada".
  // Set to `false` to re-enable authentication check later.
  const ALLOW_ANONYMOUS_PERSONALIZADA = true;

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
    // Do NOT append here to avoid duplicate messages; handlers (sendOption/sendText)
    // will be responsible for appending the user's message once.
    setTimeout(() => {
      if (text === 'Atención Personalizada') {
        sendOption(text);
      } else {
        sendText(text);
      }
    }, 50);
  }

  // ==========================
  // Enviar mensaje o acción
  // ==========================
  async function sendText(text){
    if(!text) return;
    // Show user's message once when sending a plain text option
    appendMessage('me', text);
    try{
      const body = { message: text };
      if(userId) body.usuario_id = userId;
      console.log('Enviando mensaje:', body);
      const res = await fetch('/chat/send/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/)||[])[1] || ''
        },
        body: JSON.stringify(body)
      });
      
      console.log('Response status:', res.status, res.statusText);
      
      let payload;
      try {
        payload = await res.json();
      } catch (jsonErr) {
        console.error('Error parsing JSON response:', jsonErr);
        appendMessage('bot', '❌ Error: Respuesta inválida del servidor');
        return;
      }
      
      if(!res.ok){ 
        appendMessage('bot', `❌ Error (${res.status}): ${payload.error || 'Error desconocido'}`); 
        return; 
      }
      
      if(payload.ok){ 
        appendMessage('bot', payload.reply); 
      } else {
        appendMessage('bot', `❌ ${payload.error || 'Error desconocido'}`);
      }
    } catch(err){ 
      console.error('Chat send error', err); 
      appendMessage('bot', `❌ Error de conexión: ${err.message}`); 
    }
  }

  async function sendOption(optionText){
    // sendOption is responsible for showing the user's option once
    appendMessage('me', optionText);
    
    // Detectar si es "Atención Personalizada" y manejar especialmente
    if (optionText === 'Atención Personalizada') {
      await sendPersonalizado(optionText);
      return;
    }
    
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
      } else appendMessage('bot', payload.error || 'Error desconocido');
    } catch(err){ 
      console.error('Chat option error', err); 
      appendMessage('bot', 'Error de conexión'); 
    }
  }

  async function sendMessage(){
    const text = input.value && input.value.trim();
    if(!text) return;
    // Do NOT append message here - sendText will handle it
    input.value = '';
    await sendText(text);
  }

  // ==========================
  // Eventos del input
  // ==========================
  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', function(e){ if(e.key === 'Enter') sendMessage(); });

  // ==========================
  // Función para Atención Personalizada (M/M/1)
  // ==========================
  async function sendPersonalizado(text) {
    // Verificar autenticación SOLO si no está permitido acceso anónimo
    if (!ALLOW_ANONYMOUS_PERSONALIZADA && (!userId || !isAuthenticated)) {
      appendMessage('bot', '❌ Debes estar autenticado para solicitar atención personalizada. Por favor, inicia sesión.');
      return;
    }

    try {
      const body = { 
        message: text
      };
      
      // Agregar usuario_id si está disponible
      if (userId) {
        body.usuario_id = userId;
      }
      
      console.log('Enviando atención personalizada:', body);
      
      const res = await fetch('/chat/personalizado/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/)||[])[1] || ''
        },
        body: JSON.stringify(body)
      });
      
      console.log('Response status:', res.status, res.statusText);
      
      let payload;
      try {
        payload = await res.json();
      } catch (jsonErr) {
        console.error('Error parsing JSON response:', jsonErr);
        appendMessage('bot', '❌ Error: Respuesta inválida del servidor');
        return;
      }
      
      if (!res.ok) {
        appendMessage('bot', `❌ Error (${res.status}): ${payload.error || 'Error desconocido'}`);
        return;
      }
      
      if (payload.ok) {
        appendMessage('bot', payload.reply);
      } else {
        appendMessage('bot', `❌ Error: ${payload.error || 'Error desconocido'}`);
      }
    } catch (err) {
      console.error('Chat personalizado error:', err);
      appendMessage('bot', `❌ Error de conexión: ${err.message}`);
    }
  }

})();
