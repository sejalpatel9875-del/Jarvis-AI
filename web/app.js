const $=s=>document.querySelector(s),$$=s=>document.querySelectorAll(s),workspace='default';

// Background Particles System
(function(){
  const canvas = document.createElement('canvas');
  canvas.id = 'particle-canvas';
  Object.assign(canvas.style, {
    position: 'fixed',
    top: '0',
    left: '0',
    width: '100vw',
    height: '100vh',
    zIndex: '-1',
    pointerEvents: 'none'
  });
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');
  let particles = [];
  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();
  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.size = Math.random() * 2 + 0.5;
      this.speedX = (Math.random() - 0.5) * 0.25;
      this.speedY = (Math.random() - 0.5) * 0.25;
      this.opacity = Math.random() * 0.4 + 0.1;
    }
    update() {
      this.x += this.speedX;
      this.y += this.speedY;
      if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) {
        this.reset();
      }
    }
    draw() {
      ctx.fillStyle = `rgba(112, 169, 255, ${this.opacity})`;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }
  for (let i = 0; i < 60; i++) particles.push(new Particle());
  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => { p.update(); p.draw(); });
    requestAnimationFrame(animate);
  }
  animate();
})();

// Reactive Orb State Controller
function setOrbState(state) {
  const o = $('.orb-container');
  if (o) {
    o.className = `orb-container state-${state}`;
  }
}
window.setOrbState = setOrbState;
const titles={overview:'Command center',chat:'AI conversation',reasoning:'Deep reasoning',coding:'Coding studio',agents:'Agent hub',automation:'Automations',knowledge:'Knowledge intelligence',tasks:'Task engine',crm:'AI sales co-pilot',history:'Conversation history'};
const agentNav=document.createElement('button');agentNav.className='nav-item';agentNav.dataset.view='agents';agentNav.textContent='✦ Agent hub';$('.nav').insertBefore(agentNav,$('[data-view="automation"]'));
const agentView=document.createElement('section');agentView.className='view';agentView.id='agents';agentView.innerHTML=`<div class="section-head"><div><p class="eyebrow">MULTI-AGENT OPERATING SYSTEM</p><h2>Delegate real work to JARVIS agents.</h2></div><button class="secondary" id="refresh-agents">Refresh agents</button></div><div class="agent-layout"><section class="panel agent-workspace"><p class="eyebrow">AGENT COMMAND</p><div class="agent-selected" id="agent-selected">Select an agent below to begin.</div><textarea id="agent-request" class="large-input small" placeholder="What should this agent work on?"></textarea><button class="primary" id="run-agent">Run selected agent →</button><p class="form-note" id="agent-note"></p><div class="rich-output agent-output" id="agent-output">Choose an agent, describe the work, and JARVIS will route the request through its real backend capability.</div></section><section class="panel"><p class="eyebrow">READY AGENTS</p><div class="agent-grid" id="agent-grid"><span class="empty">Loading agent registry…</span></div></section></div>`;$('.main').append(agentView);
const toast=m=>{const t=$('#toast');t.textContent=m;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),3000)};
const esc=s=>{const d=document.createElement('div');d.textContent=s??'';return d.innerHTML};
const rich=s=>esc(s).replace(/\n/g,'<br>');
async function api(url,options={}){const r=await fetch(url,options);if(r.status===401){location.assign('/');throw Error('Session ended.')}const d=await r.json();if(!r.ok)throw Error(d.detail||d.error||'Request failed.');return d}
function show(view){$$('.view').forEach(v=>v.classList.toggle('active',v.id===view));$$('.nav-item').forEach(b=>b.classList.toggle('active',b.dataset.view===view));$('#page-title').textContent=titles[view];if(view==='tasks')loadTasks();if(view==='automation')loadWorkflows();if(view==='crm')loadLeads();if(view==='agents')loadAgents();if(view==='history')renderHistory();}
$$('[data-view]').forEach(b=>b.addEventListener('click',()=>show(b.dataset.view)));
let selectedAgent=null;function agentCard(a){return `<button class="agent-card${selectedAgent===a.id?' selected':''}" data-agent="${esc(a.id)}"><span>${esc(a.icon)}</span><b>${esc(a.name)}</b><small>${esc(a.capability)}</small><em>● ready</em></button>`}async function loadAgents(){try{const d=await api('/api/v1/agents');$('#agent-grid').innerHTML=d.agents.map(agentCard).join('');$$('[data-agent]').forEach(b=>b.onclick=()=>{selectedAgent=b.dataset.agent;const agent=(d.agents||[]).find(a=>a.id===selectedAgent);$('#agent-selected').innerHTML=`<b>${esc(agent.icon)} ${esc(agent.name)}</b><span>${esc(agent.role)}</span>`;$('#agent-grid').innerHTML=d.agents.map(agentCard).join('');$$('[data-agent]').forEach(x=>x.onclick=b.onclick)})}catch(e){$('#agent-grid').textContent=e.message}}$('#refresh-agents').onclick=loadAgents;$('#run-agent').onclick=async()=>{const request=$('#agent-request').value.trim(),output=$('#agent-output');if(!selectedAgent)return toast('Choose an agent first.');if(!request)return toast('Tell the agent what to work on.');output.textContent='Agent is working…';$('#agent-note').textContent=`${selectedAgent} agent is processing your request.`;try{const d=await api('/api/v1/agents/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({agent_id:selectedAgent,request,workspace_id:workspace})});output.innerHTML=rich(d.output);$('#agent-note').textContent='Completed and recorded in the activity feed.'}catch(e){output.textContent=e.message;$('#agent-note').textContent=''}};
$('#logout').onclick=async()=>{await fetch('/auth/web-logout',{method:'POST'});location.assign('/')};
const searchModal=$('#search-modal'),searchQuery=$('#search-query'),searchResults=$('#search-results');
function openSearch(){searchModal.classList.add('open');searchModal.setAttribute('aria-hidden','false');setTimeout(()=>searchQuery.focus(),0)}
function closeSearch(){searchModal.classList.remove('open');searchModal.setAttribute('aria-hidden','true')}
$('#global-search').onclick=openSearch;$('#close-search').onclick=closeSearch;
searchModal.onclick=e=>{if(e.target===searchModal)closeSearch()};
document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openSearch()}if(e.key==='Escape')closeSearch()});
function searchRows(label,items,render){return items?.length?`<section><p class="result-label">${label}</p>${items.map(render).join('')}</section>`:''}
const searchHistoryButton=document.createElement('button');searchHistoryButton.className='secondary search-history-button';searchHistoryButton.type='button';searchHistoryButton.textContent='Search history';$('#close-search').before(searchHistoryButton);async function renderSearchHistory(){searchResults.innerHTML='<span class="empty">Loading search history…</span>';try{const d=await api(`/api/v1/search/history?workspace_id=${workspace}&limit=20`),items=d.history||[];searchResults.innerHTML=items.length?`<section><p class="result-label">RECENT SEARCHES</p>${items.map(x=>`<button class="history-search" data-history-query="${esc(x.query)}"><b>${esc(x.query)}</b><span>${esc(x.searched_at)}</span></button>`).join('')}</section>`:'<span class="empty">No workspace searches yet.</span>';$$('[data-history-query]').forEach(b=>b.onclick=()=>{searchQuery.value=b.dataset.historyQuery;$('#search-form').requestSubmit()})}catch(e){searchResults.textContent=e.message}}searchHistoryButton.onclick=renderSearchHistory;$('#global-search').addEventListener('click',renderSearchHistory);
$('#search-form').onsubmit=async e=>{e.preventDefault();const q=searchQuery.value.trim();if(!q)return;searchResults.innerHTML='<span class="empty">Searching your workspace…</span>';try{const d=await api(`/api/v1/search?workspace_id=${workspace}&query=${encodeURIComponent(q)}`);const html=searchRows('Leads',d.leads,x=>`<article><b>${esc(x.name)}</b><span>${esc(x.company||x.email||'Lead')}</span></article>`)+searchRows('Deals',d.deals,x=>`<article><b>${esc(x.title)}</b><span>${esc(x.stage||'Deal')}</span></article>`)+searchRows('Workflows',d.workflows,x=>`<article><b>${esc(x.name)}</b><span>${esc(x.trigger_type)} → ${esc(x.action_type)}</span></article>`)+searchRows('Activity',d.activity_feed,x=>`<article><b>${esc(x.action||'Activity')}</b><span>${esc(x.details||x.actor_name||'')}</span></article>`);searchResults.innerHTML=html||`<span class="empty">No workspace results for “${esc(q)}”.</span>`}catch(err){searchResults.textContent=err.message}};
const storeKey='jarvis_chat_history_v1';const history=()=>JSON.parse(localStorage.getItem(storeKey)||'[]');const save=(role,text)=>localStorage.setItem(storeKey,JSON.stringify([...history(),{role,text,at:new Date().toLocaleString()}].slice(-100)));
function bubble(role,text,saveIt=true){const e=document.createElement('article');e.className=`message ${role}-message`;e.innerHTML=role==='user'?`<div><p class="message-label">YOU · NOW</p><div class="bubble">${rich(text)}</div></div><div class="message-avatar user-avatar">Y</div>`:`<div class="message-avatar">J</div><div><p class="message-label">JARVIS · NOW</p><div class="bubble">${rich(text)}</div></div>`;$('#chat-messages').append(e);$('#chat-messages').scrollTop=999999;if(saveIt)save(role,text);return e}
let voiceReplies=localStorage.getItem('jarvis_voice_replies')!=='off';
function updateVoiceToggle(){const b=$('#voice-replies');b.textContent=voiceReplies?'🔊 Voice on':'🔇 Voice off';b.setAttribute('aria-pressed',String(voiceReplies))}
$('#voice-replies').onclick=()=>{voiceReplies=!voiceReplies;localStorage.setItem('jarvis_voice_replies',voiceReplies?'on':'off');if(!voiceReplies&&'speechSynthesis' in window)window.speechSynthesis.cancel();updateVoiceToggle();toast(voiceReplies?'JARVIS spoken replies enabled.':'JARVIS spoken replies muted.')};updateVoiceToggle();
const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
if(Recognition){const recognition=new Recognition();recognition.continuous=false;recognition.interimResults=true;recognition.lang=navigator.language?.startsWith('hi')?'hi-IN':'en-IN';let finalTranscript='';const mic=$('#voice-command'),voiceStatus=$('#voice-status');recognition.onstart=()=>{finalTranscript='';mic.classList.add('listening');mic.textContent='◉';voiceStatus.textContent='Listening… speak your command';setOrbState('listening');};recognition.onresult=e=>{let interim='';for(let i=e.resultIndex;i<e.results.length;i++){if(e.results[i].isFinal)finalTranscript+=e.results[i][0].transcript;else interim+=e.results[i][0].transcript}$('#chat-prompt').value=finalTranscript||interim};recognition.onerror=e=>{const messages={not_allowed:'Microphone permission was blocked. Allow it in your browser settings.',service_not_allowed:'Speech recognition is unavailable in this browser.',no_speech:'I could not hear anything. Try again.'};setOrbState('error');setTimeout(()=>setOrbState('idle'),2000);toast(messages[e.error]||`Voice command error: ${e.error}`)};recognition.onend=()=>{mic.classList.remove('listening');mic.textContent='🎙';voiceStatus.textContent='Enter to send · Shift+Enter for newline';if(finalTranscript.trim()){setOrbState('thinking');$('#chat-form').requestSubmit()}else{setOrbState('idle')}};mic.onclick=()=>{if(document.querySelector('.mic-button.listening')){recognition.stop();return}try{recognition.start()}catch{toast('Voice recognition is already starting.')}}}else{$('#voice-command').disabled=true;$('#voice-command').title='Voice commands require Chrome or Edge';$('#voice-status').textContent='Voice commands work best in Chrome or Edge';}
async function ask(text,target){
    setOrbState('thinking');
    try {
        const response=await api('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
        const answer=response.assistant_reply||'No response returned.';
        if(target)target.innerHTML=rich(answer);
        setOrbState('success');
        setTimeout(()=>setOrbState('idle'), 1000);
        speak(answer);
        return answer
    } catch(err) {
        setOrbState('error');
        setTimeout(()=>setOrbState('idle'), 2000);
        throw err;
    }
}
$('#chat-form').onsubmit=async e=>{e.preventDefault();const input=$('#chat-prompt'),text=input.value.trim();if(!text)return;bubble('user',text);input.value='';const pending=bubble('assistant','Thinking…',false);try{const answer=await ask(text);pending.querySelector('.bubble').innerHTML=rich(answer);save('assistant',answer)}catch(err){pending.querySelector('.bubble').textContent=err.message}};
$('#chat-prompt').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('#chat-form').requestSubmit()}};
$$('[data-prompt]').forEach(b=>b.onclick=()=>{show('chat');$('#chat-prompt').value=b.dataset.prompt;$('#chat-form').requestSubmit()});
$('#run-reasoning').onclick=async()=>{const q=$('#reasoning-prompt').value.trim(),o=$('#reasoning-output');if(!q)return toast('Describe a problem first.');o.textContent='Analysing…';try{o.innerHTML=rich(await ask(`Use deep reasoning. Structure the answer with: problem framing, assumptions, options, tradeoffs, recommendation, and next actions. User problem: ${q}`))}catch(e){o.textContent=e.message}};
$('#run-code').onclick=async()=>{const q=$('#code-prompt').value.trim(),o=$('#code-output');if(!q)return toast('Describe the code task first.');o.textContent='Working through the code…';try{o.innerHTML=rich(await ask(`Act as an expert software engineer. Explain your reasoning, identify risks, and give practical code or a plan. Task: ${q}`))}catch(e){o.textContent=e.message}};
$('#workflow-form').onsubmit=async e=>{e.preventDefault();const f=new FormData(e.target),n=$('#workflow-note');try{const d=await api(`/api/v1/workflows/create?workspace_id=${workspace}&name=${encodeURIComponent(f.get('name'))}&trigger_type=${f.get('trigger_type')}&action_type=${f.get('action_type')}`,{method:'POST'});n.textContent=`Created “${d.name||f.get('name')}”. Run history is shown on the right.`;e.target.reset();loadWorkflows()}catch(err){n.textContent=err.message}};
async function loadWorkflows(){try{const d=await api(`/api/v1/workflows/history?workspace_id=${workspace}`),items=d.history||[];$('#metric-workflows').textContent=items.length;$('#workflow-history').innerHTML=items.length?items.map(x=>`<article><b>${esc(x.status)}</b><span>Workflow #${esc(x.workflow_id)} · ${esc(x.executed_at)}</span></article>`).join(''):'<span class="empty">No workflow runs yet. Create a workflow to begin.</span>'}catch(e){$('#workflow-history').textContent=e.message}}$('#refresh-workflows').onclick=loadWorkflows;
$('#upload-form').onsubmit=async e=>{e.preventDefault();try{const d=await api('/upload',{method:'POST',body:new FormData(e.target)});toast(d.message||'Document indexed.');e.target.reset()}catch(err){toast(err.message)}};
$('#ask-knowledge').onclick=async()=>{const q=$('#knowledge-query').value.trim(),o=$('#knowledge-output');if(!q)return;o.textContent='Searching knowledge…';try{const d=await api('/documents/query',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:q,top_k:5})});o.innerHTML=rich(d.formatted_answer||'No matching knowledge found.')}catch(e){o.textContent=e.message}};
$('#task-form').onsubmit=async e=>{e.preventDefault();const f=new FormData(e.target);try{await api(`/tasks?description=${encodeURIComponent(f.get('description'))}&steps=${encodeURIComponent(f.get('steps')||'Plan, execute, verify')}`,{method:'POST'});e.target.reset();loadTasks();toast('Task created.')}catch(err){toast(err.message)}};async function loadTasks(){try{const d=await api('/tasks'),items=d.tasks||[];$('#metric-tasks').textContent=items.length;$('#task-list').innerHTML=items.length?items.map(x=>`<article><b>${esc(x.description)}</b><span>${esc(x.status)} · ${esc(x.progress)}% · ${esc(x.current_step)}</span></article>`).join(''):'<span class="empty">No tasks in this active serverless session.</span>'}catch(e){$('#task-list').textContent=e.message}}$('#refresh-tasks').onclick=loadTasks;
$('#lead-form').onsubmit=async e=>{e.preventDefault();const f=new FormData(e.target),n=$('#lead-note');try{await api(`/api/v1/crm/leads?workspace_id=${workspace}&name=${encodeURIComponent(f.get('name'))}&email=${encodeURIComponent(f.get('email'))}&company=${encodeURIComponent(f.get('company'))}`,{method:'POST'});n.textContent='Lead added to your pipeline.';e.target.reset();loadLeads()}catch(err){n.textContent=err.message}};async function loadLeads(){try{const d=await api(`/api/v1/crm/leads?workspace_id=${workspace}`),items=d.leads||[];$('#lead-list').innerHTML=items.length?items.map(x=>`<article><b>${esc(x.name)}</b><span>${esc(x.company||x.email||'New lead')} · ${esc(x.status||'NEW')}</span></article>`).join(''):'<span class="empty">No leads yet.</span>'}catch(e){$('#lead-list').textContent=e.message}}$('#refresh-crm').onclick=loadLeads;
function renderHistory(){const items=history().slice().reverse();$('#history-list').innerHTML=items.length?items.map(x=>`<article><b>${x.role==='user'?'You':'JARVIS'}</b><span>${esc(x.at)}</span><p>${rich(x.text)}</p></article>`).join(''):'<span class="empty">Your conversations will appear here.</span>'}$('#clear-history').onclick=()=>{localStorage.removeItem(storeKey);renderHistory();toast('Local history cleared.')};
let agentCatalog=[];function renderAgentGrid(){const grid=$('#agent-grid');if(grid)grid.innerHTML=agentCatalog.map(agentCard).join('')}$('#agent-grid').onclick=e=>{const card=e.target.closest('[data-agent]');if(!card)return;selectedAgent=card.dataset.agent;const agent=agentCatalog.find(a=>a.id===selectedAgent);$('#agent-selected').innerHTML=`<b>${esc(agent.icon)} ${esc(agent.name)}</b><span>${esc(agent.role)}</span>`;renderAgentGrid()};async function loadAgents(){try{const d=await api('/api/v1/agents');agentCatalog=d.agents||[];renderAgentGrid()}catch(e){$('#agent-grid').textContent=e.message}};
let activeRecorder=null,recordingStream=null,voiceChunks=[];async function toggleRecordedVoice(){const mic=$('#voice-command'),status=$('#voice-status');if(activeRecorder?.state==='recording'){activeRecorder.stop();return}try{recordingStream=await navigator.mediaDevices.getUserMedia({audio:true});const mime=window.MediaRecorder.isTypeSupported?.('audio/webm;codecs=opus')?'audio/webm;codecs=opus':'';activeRecorder=new MediaRecorder(recordingStream,mime?{mimeType:mime}:undefined);voiceChunks=[];activeRecorder.ondataavailable=e=>{if(e.data.size)voiceChunks.push(e.data)};activeRecorder.onstart=()=>{mic.classList.add('listening');mic.textContent='■';status.textContent='Recording… tap again when you finish speaking';setOrbState('listening');};activeRecorder.onerror=()=>{setOrbState('error');setTimeout(()=>setOrbState('idle'),2000);toast('Microphone recording failed. Check microphone permission.')};activeRecorder.onstop=async()=>{mic.classList.remove('listening');mic.textContent='🎙';status.textContent='Transcribing your command…';setOrbState('thinking');recordingStream?.getTracks().forEach(track=>track.stop());const audio=new Blob(voiceChunks,{type:activeRecorder.mimeType||'audio/webm'});activeRecorder=null;if(!audio.size){status.textContent='Enter to send · Shift+Enter for newline';setOrbState('idle');return toast('No audio was captured.')}const form=new FormData();form.append('file',audio,'jarvis-command.webm');try{const d=await api('/api/v1/voice/transcribe',{method:'POST',body:form});$('#chat-prompt').value=d.text;status.textContent='Voice command transcribed. Sending to JARVIS…';$('#chat-form').requestSubmit()}catch(e){status.textContent='Enter to send · Shift+Enter for newline';setOrbState('error');setTimeout(()=>setOrbState('idle'),2000);toast(e.message)}};activeRecorder.start()}catch(e){const msg=e.name==='NotAllowedError'?'Microphone permission was blocked. Allow microphone access and try again.':'This browser cannot record audio. Open JARVIS in Chrome or Edge.';setOrbState('error');setTimeout(()=>setOrbState('idle'),2000);toast(msg);status.textContent=msg}}if(navigator.mediaDevices?.getUserMedia&&window.MediaRecorder){const mic=$('#voice-command');mic.disabled=false;mic.title='Record a voice command';mic.onclick=toggleRecordedVoice;$('#voice-status').textContent='Tap mic, speak, then tap again to send'}else{$('#voice-command').disabled=true;$('#voice-status').textContent='Voice recording needs a browser with microphone support'};
async function renderHistory(){const list=$('#history-list');list.innerHTML='<span class="empty">Loading JARVIS conversation history…</span>';try{const d=await api('/api/v1/conversations?limit=100');const turns=d.conversations||[];if(turns.length){list.innerHTML=turns.slice().reverse().map(x=>`<article><b>You</b><span>${esc(x.timestamp)}</span><p>${rich(x.user_message)}</p><b>JARVIS</b><span>${esc(x.provider||'Hybrid AI')}</span><p>${rich(x.assistant_reply)}</p></article>`).join('');return}}catch(e){}const items=history().slice().reverse();list.innerHTML=items.length?items.map(x=>`<article><b>${x.role==='user'?'You':'JARVIS'}</b><span>${esc(x.at)}</span><p>${rich(x.text)}</p></article>`).join(''):'<span class="empty">No conversations have been saved yet.</span>'}$('#clear-history').textContent='Clear local copy';
let neuralVoiceAudio=null;
const isDevanagari=text=>/[\u0900-\u097F]/.test(text);
async function speak(text){
    if(!voiceReplies)return;
    try{
        const response=await fetch('/api/v1/voice/synthesize',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
        if(!response.ok)throw Error('Neural voice unavailable');
        const audioUrl=URL.createObjectURL(await response.blob());
        if(neuralVoiceAudio){
            neuralVoiceAudio.pause();
            URL.revokeObjectURL(neuralVoiceAudio.src)
        }
        neuralVoiceAudio=new Audio(audioUrl);
        neuralVoiceAudio.onplay=()=>setOrbState('speaking');
        neuralVoiceAudio.onended=()=>{
            URL.revokeObjectURL(audioUrl);
            setOrbState('idle');
        };
        await neuralVoiceAudio.play()
    }catch(e){
        if(!('speechSynthesis' in window))return;
        window.speechSynthesis.cancel();
        const fallback=new SpeechSynthesisUtterance(text);
        fallback.lang=isDevanagari(text)?'hi-IN':'en-IN';
        fallback.rate=.94;
        const matching=window.speechSynthesis.getVoices().find(v=>v.lang.toLowerCase().startsWith(fallback.lang.toLowerCase()));
        if(matching)fallback.voice=matching;
        fallback.onstart=()=>setOrbState('speaking');
        fallback.onend=()=>setOrbState('idle');
        fallback.onerror=()=>setOrbState('idle');
        window.speechSynthesis.speak(fallback)
    }
}
loadTasks();loadWorkflows();
