import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class DXFDataHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/viewer.html'
        return SimpleHTTPRequestHandler.do_GET(self)

def create_viewer_html():
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>DXF Data Viewer</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: #007bff;
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card .number {
            font-size: 2em;
            font-weight: bold;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #007bff;
            color: white;
        }
        tr:hover {
            background: #f5f5f5;
        }
        .json-view {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow: auto;
            max-height: 500px;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            background: #28a745;
            color: white;
            border-radius: 3px;
            font-size: 0.8em;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        .tab {
            padding: 10px 20px;
            background: #e9ecef;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .tab.active {
            background: #007bff;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 AutoCAD DXF Data Viewer</h1>
        <div id="stats"></div>
        <div class="tabs">
            <button class="tab active" onclick="showTab('table')">📋 Таблица</button>
            <button class="tab" onclick="showTab('json')">💾 JSON</button>
        </div>
        <div id="table-tab" class="tab-content active">
            <div id="table-container"></div>
        </div>
        <div id="json-tab" class="tab-content">
            <div id="json-container" class="json-view"></div>
        </div>
    </div>
    <script>
        let data = [];
        
        function showTab(tab) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tab + '-tab').classList.add('active');
            document.querySelector(`.tab[onclick="showTab('${tab}')"]`).classList.add('active');
        }
        
        fetch('extracted_data.json')
            .then(response => response.json())
            .then(jsonData => {
                data = jsonData;
                renderStats(data);
                renderTable(data);
                renderJSON(data);
            })
            .catch(error => {
                document.getElementById('stats').innerHTML = 
                    '<div class="stat-card" style="background: #dc3545;">❌ Ошибка загрузки данных</div>';
            });
        
        function renderStats(data) {
            if (!data || data.length === 0) {
                document.getElementById('stats').innerHTML = '<div class="stat-card">Нет данных</div>';
                return;
            }
            
            const total = data.length;
            const attrs = new Set();
            data.forEach(item => {
                Object.keys(item.attributes).forEach(attr => attrs.add(attr));
            });
            
            document.getElementById('stats').innerHTML = `
                <div class="stats">
                    <div class="stat-card">
                        <div class="number">${total}</div>
                        <div>Всего блоков</div>
                    </div>
                    <div class="stat-card" style="background: #28a745;">
                        <div class="number">${attrs.size}</div>
                        <div>Уникальных атрибутов</div>
                    </div>
                    <div class="stat-card" style="background: #ffc107; color: #333;">
                        <div class="number">${new Set(data.map(item => item.handle)).size}</div>
                        <div>Уникальных хендлов</div>
                    </div>
                </div>
            `;
        }
        
        function renderTable(data) {
            if (!data || data.length === 0) {
                document.getElementById('table-container').innerHTML = '<p>Нет данных</p>';
                return;
            }
            
            const attrKeys = new Set();
            data.forEach(item => {
                Object.keys(item.attributes).forEach(key => attrKeys.add(key));
            });
            
            let html = '<table>';
            html += '<tr><th>#</th><th>Handle</th><th>X</th><th>Y</th><th>Z</th><th>Rotation</th>';
            attrKeys.forEach(key => {
                html += `<th>${key}</th>`;
            });
            html += '</tr>';
            
            data.forEach((item, index) => {
                html += `<tr>
                    <td>${index + 1}</td>
                    <td><span class="badge">${item.handle}</span></td>
                    <td>${item.position.x}</td>
                    <td>${item.position.y}</td>
                    <td>${item.position.z || 0}</td>
                    <td>${item.rotation || 0}°</td>`;
                
                attrKeys.forEach(key => {
                    html += `<td>${item.attributes[key] || ''}</td>`;
                });
                
                html += '</tr>';
            });
            
            html += '</table>';
            document.getElementById('table-container').innerHTML = html;
        }
        
        function renderJSON(data) {
            document.getElementById('json-container').textContent = 
                JSON.stringify(data, null, 2);
        }
    </script>
</body>
</html>"""
    
    with open('viewer.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("✅ Создан viewer.html")

if __name__ == "__main__":
    create_viewer_html()
    
    port = 8000
    print(f"\n🌐 Веб-интерфейс запущен на http://localhost:{port}")
    print("Нажмите Ctrl+C для остановки")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    httpd = HTTPServer(('localhost', port), DXFDataHandler)
    httpd.serve_forever()
