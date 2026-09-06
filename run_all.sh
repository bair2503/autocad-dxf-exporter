#!/bin/bash

echo "🚀 Запуск AutoCAD DXF Exporter"
echo "================================"

# Активируем виртуальное окружение
source .venv/bin/activate

# Запускаем основной скрипт
echo "1️⃣ Извлечение данных из DXF..."
python extract_blocks.py

echo ""
echo "✅ Все готово!"
echo "📁 Результаты:"
echo "  - extracted_data.json - данные в JSON"
echo "  - extracted_data.csv - данные в CSV"