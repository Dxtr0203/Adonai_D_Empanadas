// Chat widget frontend: abre una ventana en la esquina inferior izquierda y envía mensajes al endpoint /chat/send/
document.addEventListener('DOMContentLoaded', function(){
  (function(){
    const toggle = document.getElementById('chat-toggle');
    const panel = document.getElementById('chat-panel');
  const closeBtn = document.getElementById('chat-close');
  const sendBtn = document.getElementById('chat-send');
  const input = document.getElementById('chat-input');
  const messages = document.getElementById('chat-messages');

  if(!toggle || !panel) return;

  function appendMessage(author, text){
    try{
      const el = document.createElement('div');
      el.className = 'mb-2';
      const safe = (typeof text === 'string') ? escapeHtml(text) : String(text);
      if(author === 'me'){
        el.innerHTML = `<div class="text-end"><div class="d-inline-block p-2 bg-primary text-white rounded">${safe}</div></div>`;
      } else {
        el.innerHTML = `<div class="text-start"><div class="d-inline-block p-2 bg-light rounded">${safe}</div></div>`;
      }
      messages.appendChild(el);
      messages.scrollTop = messages.scrollHeight;
    } catch(err){
      // Fallback simple append to avoid silent failures
      console.error('appendMessage error:', err, 'author:', author, 'text:', text);
      const el = document.createElement('div');
      el.className = 'mb-2';
      el.textContent = (author === 'me' ? 'Tú: ' : 'Bot: ') + (text === undefined ? '' : String(text));
      messages.appendChild(el);
      messages.scrollTop = messages.scrollHeight;
    }
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
    const show = panel.style.display !== 'block';
    panel.style.display = show ? 'block' : 'none';
    if (show) onOpen();
    console.debug('chat toggle clicked, show=', show);
  });
  closeBtn.addEventListener('click', function(){ panel.style.display = 'none'; });

  sendBtn.addEventListener('click', sendMessage);
  input.addEventListener('keydown', function(e){ if(e.key === 'Enter'){ e.preventDefault(); sendMessage(); } });

  // Normalizar texto: quitar acentos y pasar a minúsculas
  function normalize(s){
    return s.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase();
  }

  // Procesa el texto (coincidencias locales y fallback al servidor)
  async function processText(text){
    console.debug('processText start:', text);
    if(!text) return;
    const lc = normalize(text);
    const localResponses = [
      {keys: ['hola','buenos','buenas','saludo'], reply: '¡Hola! 👋 Soy el asistente de Adonai. ¿En qué puedo ayudarte? Puedes preguntar por "información de la tienda", "productos", "servicios" o "horarios".'},
      {keys: ['informacion','datos tienda','info tienda'], reply: 'Nuestra tienda está en La Paz, ofrecemos alimentos y accesorios para mascotas. ¿Quieres ver el catálogo? Visita la sección Catálogo.'},
      {keys: ['productos','catalogo','catalogo productos','productos disponibles'], reply: 'Tenemos alimentos para perros y gatos, accesorios y juguetes. Puedes navegar el catálogo en la pestaña "Catálogo".'},
      {keys: ['servicios','servicio','servicios disponibles'], reply: 'Ofrecemos delivery en la ciudad, asesoría para mascotas y pedidos por mayor. ¿Deseas más detalle sobre algún servicio?'},
      {keys: ['horario','horarios','abrimos','cerramos'], reply: 'Nuestro horario es Lunes a Sábado de 9:00 a 19:00. Domingos 10:00 a 14:00.'},
      {keys: ['gracias','muchas gracias','thank'], reply: '¡Con gusto! Si necesitas algo más, aquí estoy.'},
    ];

    // Usar regex con \b para evitar coincidencias parciales y normalizar claves
    for(const r of localResponses){
      for(const k of r.keys){
        const nk = normalize(k);
        const re = new RegExp('\\b' + nk.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&') + '\\b','i');
        if(re.test(lc)){
          console.debug('processText matched local key:', k, 'reply:', r.reply);
          appendMessage('bot', r.reply);
          // local response handled; ensure input is enabled and typing indicator removed if any
          try{ sendBtn.disabled = false; input.disabled = false; } catch(e){}
          const t = messages.querySelector('[data-typing="1"]'); if(t) t.remove();
          return; // respuesta local tomada
        }
      }
    }

    // si no se responde localmente, llamar al servidor
    // Mostrar indicador de 'escribiendo' y desactivar input
    const typingEl = document.createElement('div');
    typingEl.className = 'mb-2';
    typingEl.setAttribute('data-typing', '1');
    typingEl.innerHTML = `<div class="text-start"><div class="d-inline-block p-2 bg-light rounded"><em>Escribiendo...</em></div></div>`;
    messages.appendChild(typingEl);
    messages.scrollTop = messages.scrollHeight;
    sendBtn.disabled = true;
    input.disabled = true;

  try{
      const res = await fetch('/chat/send/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': (document.cookie.match(/csrftoken=([^;]+)/)||[])[1] },
        body: JSON.stringify({ message: text })
      });
      if(!res.ok) {
        removeTyping();
        appendMessage('bot', 'Error al enviar mensaje.');
        return;
      }
      const payload = await res.json();
      removeTyping();
      if(payload.ok){
        appendMessage('bot', payload.reply);
      } else {
        appendMessage('bot', payload.error || 'Error desconocido');
      }
    } catch(err){
      console.error('Chat send error', err);
      removeTyping();
      appendMessage('bot', 'Error de conexión');
    }
    finally{
      sendBtn.disabled = false;
      input.disabled = false;
      input.focus();
    }
    function removeTyping(){
      const t = messages.querySelector('[data-typing="1"]');
      if(t) t.remove();
    }
  }

  // Envío desde el input (mensaje del usuario visible ya mostrado)
  async function sendMessage(){
    const text = input.value && input.value.trim();
    if(!text) return;
    appendMessage('me', text);
    input.value = '';
    await processText(text);
  }

  // Envío programático sin añadir el mensaje del usuario (útil para quick actions)
  async function sendText(text){
    await processText(text);
  }

  // Al abrir el panel, mostrar saludo y acciones
  function onOpen(){
    // Mostrar saludo una vez por sesión
    try{
      console.debug('processText calling server fallback for:', text);
      const greeted = sessionStorage.getItem('adonai_chat_greeted');
      if(!greeted){
        appendMessage('bot', '¡Hola! 👋 Soy el asistente de Adonai. Puedes escoger una opción rápida o escribir tu pregunta.');
        sessionStorage.setItem('adonai_chat_greeted', '1');
      }
      // Mensaje de depuración visible una sola vez para confirmar que appendMessage funciona
      try{
        const dbg = sessionStorage.getItem('adonai_chat_debug_shown');
        if(!dbg){
          appendMessage('bot', '[DEBUG] Widget inicializado correctamente — este mensaje solo aparece una vez.');
          sessionStorage.setItem('adonai_chat_debug_shown', '1');
        }
      } catch(e){}
    } catch(e){
      // si sessionStorage falla, usar fallback simple
      if(messages.children.length === 0) appendMessage('bot', '¡Hola! 👋 Soy el asistente de Adonai. Puedes escoger una opción rápida o escribir tu pregunta.');
    }
  
    // Hookear botones rápidos
    document.querySelectorAll('.quick-action').forEach(btn => {
      btn.removeEventListener('click', quickHandler);
      btn.addEventListener('click', quickHandler);
    });
    // Focus al input
    try{ input.focus(); } catch(e){ /* ignore */ }
    console.debug('chat onOpen: greeted=', sessionStorage.getItem('adonai_chat_greeted'));
  }

  function quickHandler(e){
    const text = e.currentTarget.textContent.trim();
    console.debug('quickHandler clicked:', text);
    // Simular envío: mostrar mensaje del usuario y luego procesar
    appendMessage('me', text);
    // Llamar al procesamiento local directamente (evita doble append en sendText)
    // Reuse normalized matching from sendMessage by calling sendText but with small delay to allow UI update
    setTimeout(() => sendText(text), 50);
  }
  })();
});
