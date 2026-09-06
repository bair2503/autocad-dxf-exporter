import ezdxf
import json
from pathlib import Path
import os
from datetime import datetime

def load_config():
    """Загружает конфигурацию из файла"""
    config_file = "config.json"
    if Path(config_file).exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "target_block": "Lamp",
        "input_file": "test_drawing.dxf",
        "output_file": "extracted_data.json",
        "export_format": "json"
    }

def extract_blocks_from_dxf(dxf_path, target_block=None):
    """
    Извлекает информацию о блоках из DXF файла
    """
    try:
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        blocks_data = []
        all_blocks = []

        # Получаем все блоки в чертеже
        for block in doc.blocks:
            if not block.name.startswith('*'):
                all_blocks.append(block.name)

        print(f"📁 Файл: {dxf_path}")
        print(f"📦 Найдены блоки в чертеже: {all_blocks}")

        # Если target_block не указан, используем первый найденный блок
        if target_block is None and all_blocks:
            target_block = all_blocks[0]
            print(f"🎯 Блок не указан, использую первый: {target_block}")

        if target_block not in all_blocks:
            print(f"⚠️ Блок '{target_block}' не найден в чертеже")
            return []

        # Ищем все вхождения блоков
        for insert in msp.query(f'INSERT[name=="{target_block}"]'):
            attribs = {}
            for attrib in insert.attribs:
                attribs[attrib.dxf.tag] = attrib.dxf.text

            # Получаем координаты
            pos = insert.dxf.insert
            x, y = pos.x, pos.y
            
            # Если есть Z координата
            z = pos.z if hasattr(pos, 'z') else 0

            block_info = {
                "handle": insert.dxf.handle,
                "position": {
                    "x": round(x, 3),
                    "y": round(y, 3),
                    "z": round(z, 3)
                },
                "attributes": attribs,
                "rotation": round(insert.dxf.rotation if hasattr(insert.dxf, 'rotation') else 0, 2),
                "scale": {
                    "x": round(insert.dxf.xscale if hasattr(insert.dxf, 'xscale') else 1.0, 2),
                    "y": round(insert.dxf.yscale if hasattr(insert.dxf, 'yscale') else 1.0, 2)
                }
            }
            blocks_data.append(block_info)

        return blocks_data

    except IOError:
        print(f"❌ Не удалось прочитать файл: {dxf_path}")
    except ezdxf.DXFStructureError:
        print("❌ Файл поврежден или имеет неверную структуру DXF.")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
    return []

def export_to_csv(data, filename):
    """Экспортирует данные в CSV файл"""
    if not data:
        print("Нет данных для экспорта в CSV")
        return
    
    import csv
    
    # Собираем все возможные атрибуты
    all_attrs = set()
    for item in data:
        all_attrs.update(item['attributes'].keys())
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Заголовки
        headers = ['Handle', 'X', 'Y', 'Z', 'Rotation'] + sorted(all_attrs)
        writer.writerow(headers)
        
        # Данные
        for item in data:
            row = [
                item['handle'],
                item['position']['x'],
                item['position']['y'],
                item['position']['z'],
                item['rotation']
            ]
            for attr in sorted(all_attrs):
                row.append(item['attributes'].get(attr, ''))
            writer.writerow(row)
    
    print(f"✅ Данные экспортированы в CSV: {filename}")

def create_demo_dxf():
    """Создает демонстрационный DXF файл с блоком "Lamp" и дополнительной информацией"""
    print("🔄 Создаю тестовый DXF файл...")
    
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # Создаем определение блока
    block = doc.blocks.new(name="Lamp")
    
    # Добавляем геометрию блока (круг с крестом - как лампа)
    block.add_circle(center=(0, 0), radius=1.5)
    block.add_line(start=(-1.5, 0), end=(1.5, 0))
    block.add_line(start=(0, -1.5), end=(0, 1.5))
    
    # Добавляем несколько вставок блока
    lamps = [
        {"pos": (5, 5), "mark": "L-001", "power": "50W", "note": "Светильник 1", "rotation": 0},
        {"pos": (15, 5), "mark": "L-002", "power": "100W", "note": "Светильник 2", "rotation": 45},
        {"pos": (10, 15), "mark": "L-003", "power": "75W", "note": "Светильник 3", "rotation": 90},
        {"pos": (25, 15), "mark": "L-004", "power": "60W", "note": "Светильник 4", "rotation": -30},
        {"pos": (20, 25), "mark": "L-005", "power": "150W", "note": "Светильник 5", "rotation": 180},
    ]
    
    for lamp in lamps:
        insert = msp.add_blockref("Lamp", insert=lamp["pos"])
        insert.dxf.rotation = lamp["rotation"]
        insert.add_attrib("Марка", lamp["mark"], insert=(0, 1.8))
        insert.add_attrib("Мощность", lamp["power"], insert=(0, 0))
        insert.add_attrib("Примечание", lamp["note"], insert=(0, -1.8))
    
    # Добавляем рамку и подпись
    msp.add_lwpolyline([(0, 0), (30, 0), (30, 30), (0, 30), (0, 0)])
    msp.add_text("Тестовый чертеж с блоками Lamp", 
                 dxfattribs={'height': 2, 'insert': (2, 32)})
    
    # Добавляем легенду
    legend_y = 28
    for i, lamp in enumerate(lamps):
        msp.add_text(f"{lamp['mark']}: {lamp['power']} ({lamp['note']})", 
                     dxfattribs={'height': 1.2, 'insert': (2, legend_y - i*1.5)})
    
    filename = "test_drawing_advanced.dxf"
    doc.saveas(filename)
    print(f"✅ Создан файл: {filename}")
    return filename

def main():
    print("=" * 60)
    print("🚀 AutoCAD DXF Exporter v2.0")
    print("=" * 60)
    
    # Загружаем конфигурацию
    config = load_config()
    
    # Получаем параметры из конфига
    input_file = config.get("input_file", "test_drawing.dxf")
    target_block = config.get("target_block", "Lamp")
    output_file = config.get("output_file", "extracted_data.json")
    
    # Если файл не существует, создаем демо-файл
    if not Path(input_file).exists():
        input_file = create_demo_dxf()
        # Обновляем конфиг
        config["input_file"] = input_file
        with open("config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    
    # Извлекаем данные из DXF
    print(f"\n🔍 Поиск блоков '{target_block}'...")
    blocks_data = extract_blocks_from_dxf(input_file, target_block)
    
    if blocks_data:
        print(f"\n✅ Найдено {len(blocks_data)} блоков")
        
        # Сохраняем в JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(blocks_data, f, indent=4, ensure_ascii=False)
        print(f"💾 Данные сохранены в JSON: {output_file}")
        
        # Экспорт в CSV для Excel
        csv_file = output_file.replace('.json', '.csv')
        export_to_csv(blocks_data, csv_file)
        
        # Показываем краткую статистику
        print("\n📊 Статистика:")
        print(f"  - Количество блоков: {len(blocks_data)}")
        print(f"  - Уникальные атрибуты: {set().union(*[list(b['attributes'].keys()) for b in blocks_data])}")
        print(f"  - Диапазон X: {min(b['position']['x'] for b in blocks_data):.1f} - {max(b['position']['x'] for b in blocks_data):.1f}")
        print(f"  - Диапазон Y: {min(b['position']['y'] for b in blocks_data):.1f} - {max(b['position']['y'] for b in blocks_data):.1f}")
        
        # Показываем пример данных
        print("\n📝 Пример данных:")
        print(json.dumps(blocks_data[0], indent=2, ensure_ascii=False))
        
    else:
        print("\n❌ Блоки не найдены или произошла ошибка")
    
    print("\n" + "=" * 60)
    print("✅ Готово!")

if __name__ == "__main__":
    main()