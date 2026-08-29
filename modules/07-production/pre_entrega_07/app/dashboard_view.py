"""Plantilla HTML y generador de la interfaz de control Mission Control Dashboard."""


def get_dashboard_html() -> str:
    """Genera el HTML interactivo del Dashboard de Producción con visor de informes."""
    return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Production Dashboard · Pre-Entrega 07</title>
    <style>
        :root { --bg: #0b0f19; --card: #151d2e; --primary: #3b82f6; --accent: #10b981; --warning: #f59e0b; --danger: #ef4444; --text: #f3f4f6; --text-dim: #9ca3af; }
        body { margin: 0; padding: 24px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1f293d; padding-bottom: 16px; margin-bottom: 24px; }
        .grid { display: grid; grid-template-columns: 1fr 2fr; gap: 24px; }
        .card { background: var(--card); border: 1px solid #1f293d; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
        .metric-card { background: #1a233a; border-radius: 8px; padding: 14px; text-align: center; border: 1px solid #273553; }
        .metric-val { font-size: 24px; font-weight: bold; color: var(--primary); }
        .metric-lbl { font-size: 12px; color: var(--text-dim); text-transform: uppercase; margin-top: 4px; }
        input, textarea, button { width: 100%; box-sizing: border-box; border-radius: 6px; padding: 10px; margin-top: 8px; border: 1px solid #273553; background: #0b0f19; color: var(--text); font-size: 14px; }
        button { background: var(--primary); border: none; font-weight: 600; cursor: pointer; transition: 0.2s; margin-top: 14px; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
        .badge-COMPLETED { background: rgba(16, 185, 129, 0.2); color: var(--accent); }
        .badge-WAITING_APPROVAL { background: rgba(245, 158, 11, 0.2); color: var(--warning); border: 1px solid var(--warning); }
        .badge-RUNNING { background: rgba(59, 130, 246, 0.2); color: var(--primary); }
        .badge-FAILED { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #1f293d; }
        th { color: var(--text-dim); font-size: 11px; text-transform: uppercase; }
        .hitl-box { background: #261f10; border: 1px solid var(--warning); border-radius: 8px; padding: 14px; margin-top: 16px; display: none; }
        .modal { display: none; position: fixed; z-index: 100; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px); }
        .modal-content { background: var(--card); border: 1px solid #273553; margin: 8% auto; padding: 24px; border-radius: 12px; width: 65%; max-width: 700px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        pre { background: #0b0f19; padding: 16px; border-radius: 8px; border: 1px solid #1f293d; font-family: monospace; white-space: pre-wrap; color: #6ee7b7; font-size: 13px; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 style="margin: 0; font-size: 22px;">🚀 Multi-Agent Production Dashboard</h1>
            <p style="margin: 4px 0 0 0; font-size: 13px; color: var(--text-dim);">Pre-Entrega 07 · FastAPI + Redis + Arize Phoenix + HITL · Jen Yanez</p>
        </div>
        <div>
            <a href="/docs" target="_blank" style="color: var(--primary); text-decoration: none; margin-right: 16px; font-size: 13px;">📖 Swagger Docs</a>
            <a href="http://localhost:6006" target="_blank" style="color: var(--accent); text-decoration: none; font-size: 13px;">📊 Arize Phoenix (6006)</a>
        </div>
    </div>
    <div class="metrics">
        <div class="metric-card"><div class="metric-val" id="metric-tasks">0</div><div class="metric-lbl">Tareas Procesadas</div></div>
        <div class="metric-card"><div class="metric-val" id="metric-latency">~4.8 ms</div><div class="metric-lbl">Latencia HTTP 202</div></div>
        <div class="metric-card"><div class="metric-val" id="metric-cost">$0.0013</div><div class="metric-lbl">Costo Promedio FinOps</div></div>
    </div>
    <div class="grid">
        <div class="card">
            <h3 style="margin-top:0;">📥 Encolar Tarea Asíncrona</h3>
            <label style="font-size:12px; color:var(--text-dim);">Consulta para el Orquestador Multi-Agente:</label>
            <textarea id="task-query" rows="3" placeholder="Ej: Proyección financiera y CAGR del mercado de IA Generativa al 2030"></textarea>
            <label style="font-size:12px; color:var(--text-dim); display:flex; align-items:center; margin-top:8px;">
                <input type="checkbox" id="task-hitl" checked style="width:auto; margin:0 8px 0 0;"> Requerir Aprobación Humana (HITL)
            </label>
            <button onclick="submitTask()">⚡ Encolar Tarea (HTTP 202)</button>
            <div id="hitl-container" class="hitl-box">
                <h4 style="margin:0 0 8px 0; color:var(--warning);">🛑 Intervención Humana (HITL) Requerida</h4>
                <p id="hitl-summary" style="font-size:12px; color:#fde68a; margin:0 0 10px 0;"></p>
                <input type="text" id="hitl-feedback" placeholder="Comentario o directiva de aprobación (opcional)">
                <div style="display:flex; gap:10px; margin-top:10px;">
                    <button onclick="resolveHITL(true)" style="background:var(--accent); margin:0;">✅ Aprobar</button>
                    <button onclick="resolveHITL(false)" style="background:var(--danger); margin:0;">❌ Rechazar</button>
                </div>
            </div>
        </div>
        <div class="card">
            <h3 style="margin-top:0;">📊 Tareas en Vivo (Persistencia Redis)</h3>
            <div style="overflow-x:auto;">
                <table>
                    <thead><tr><th>Job ID</th><th>Consulta</th><th>Estado</th><th>Costo</th><th>Informe</th></tr></thead>
                    <tbody id="tasks-table"><tr><td colspan="5" style="text-align:center; color:var(--text-dim);">Cargando tareas...</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>
    <div id="report-modal" class="modal" onclick="closeModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1f293d; padding-bottom:12px;">
                <h3 id="modal-title" style="margin:0; font-size:18px; color:var(--primary);">📄 Informe Ejecutivo Final</h3>
                <span onclick="closeModal()" style="cursor:pointer; font-size:20px; color:var(--text-dim);">&times;</span>
            </div>
            <pre id="modal-body" style="margin-top:16px;"></pre>
        </div>
    </div>
    <script>
        let currentHitlJobId = null, currentTasks = [];
        async function loadTasks() {
            try {
                const res = await fetch('/tasks?limit=25');
                currentTasks = await res.json();
                document.getElementById('metric-tasks').innerText = currentTasks.length;
                const tbody = document.getElementById('tasks-table');
                if(!currentTasks.length) { tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No hay tareas.</td></tr>'; return; }
                tbody.innerHTML = currentTasks.map((t, idx) => `
                    <tr>
                        <td><code>${t.job_id}</code></td>
                        <td>${t.query.substring(0, 32)}...</td>
                        <td><span class="badge badge-${t.status}">${t.status}</span></td>
                        <td>$${t.estimated_cost_usd || '0.0013'}</td>
                        <td>
                            ${t.status === 'WAITING_APPROVAL' ? `<button onclick="openHITL('${t.job_id}', '${(t.intermediate_summary||'').replace(/'/g, "\\'")}')" style="padding:4px 8px; font-size:11px; margin:0; background:var(--warning); color:#000;">Revisar</button>` : ''}
                            ${t.status === 'COMPLETED' ? `<button onclick="viewReport(${idx})" style="padding:4px 8px; font-size:11px; margin:0; background:#273553; color:#60a5fa;">👁️ Ver</button>` : ''}
                        </td>
                    </tr>
                `).join('');
            } catch(e) { console.error(e); }
        }
        function viewReport(idx) {
            const t = currentTasks[idx];
            document.getElementById('modal-title').innerText = `📄 Informe: ${t.job_id}`;
            document.getElementById('modal-body').innerText = (t.result && t.result.summary) ? t.result.summary : 'Informe en proceso...';
            document.getElementById('report-modal').style.display = 'block';
        }
        function closeModal() { document.getElementById('report-modal').style.display = 'none'; }
        async function submitTask() {
            const query = document.getElementById('task-query').value.trim();
            const hitl = document.getElementById('task-hitl').checked;
            if(!query) return alert('Ingresa una consulta.');
            const res = await fetch('/tasks', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({query, require_human_approval: hitl}) });
            if(res.status === 202) { document.getElementById('task-query').value = ''; loadTasks(); }
        }
        function openHITL(jobId, summary) {
            currentHitlJobId = jobId;
            document.getElementById('hitl-summary').innerText = summary || 'Revisión intermedia requerida.';
            document.getElementById('hitl-container').style.display = 'block';
        }
        async function resolveHITL(approved) {
            if(!currentHitlJobId) return;
            const feedback = document.getElementById('hitl-feedback').value;
            await fetch(`/tasks/${currentHitlJobId}/approve`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({approved, feedback}) });
            document.getElementById('hitl-container').style.display = 'none';
            document.getElementById('hitl-feedback').value = '';
            currentHitlJobId = null; loadTasks();
        }
        loadTasks(); setInterval(loadTasks, 2500);
    </script>
</body>
</html>"""
