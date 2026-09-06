import json
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt

def analyze_json_data(json_file):
    """Анализирует данные из JSON файла"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 60)
    print("📊 АНАЛИЗ ДАННЫХ")
    print("=" * 60)
    
    # Базовая статистика
    print(f"\n📌 Общая информация:")
    print(f"  - Всего блоков: {len(data)}")
    
    if not data:
        print("  - Нет данных для анализа")
        return
    
    # Анализ атрибутов
    all_attrs = []
    for item in data:
        all_attrs.extend(item['attributes'].keys())
    
    attr_counter = Counter(all_attrs)
    print(f"\n📋 Атрибуты:")
    for attr, count in attr_counter.most_common():
        print(f"  - {attr}: встречается в {count} блоках")
    
    # Анализ позиций
    x_coords = [item['position']['x'] for item in data]
    y_coords = [item['position']['y'] for item in data]
    
    print(f"\n📍 Позиции:")
    print(f"  - X: мин={min(x_coords):.1f}, макс={max(x_coords):.1f}, сред={sum(x_coords)/len(x_coords):.1f}")
    print(f"  - Y: мин={min(y_coords):.1f}, макс={max(y_coords):.1f}, сред={sum(y_coords)/len(y_coords):.1f}")
    
    # Анализ мощностей (если есть)
    powers = []
    for item in data:
        if 'Мощность' in item['attributes']:
            power_str = item['attributes']['Мощность']
            # Извлекаем число из строки (например "50W" -> 50)
            import re
            num = re.findall(r'\d+', power_str)
            if num:
                powers.append(int(num[0]))
    
    if powers:
        print(f"\n⚡ Мощности:")
        print(f"  - Мин: {min(powers)}W")
        print(f"  - Макс: {max(powers)}W")
        print(f"  - Сред: {sum(powers)/len(powers):.1f}W")
        print(f"  - Сумма: {sum(powers)}W")
    
    # Анализ поворотов
    rotations = [item.get('rotation', 0) for item in data]
    if rotations:
        print(f"\n🔄 Повороты:")
        unique_rotations = set(rotations)
        for rot in sorted(unique_rotations):
            count = rotations.count(rot)
            print(f"  - {rot}°: {count} блоков")
    
    return data

def create_pandas_dataframe(data):
    """Создает DataFrame из данных для анализа"""
    
    rows = []
    for item in data:
        row = {
            'Handle': item['handle'],
            'X': item['position']['x'],
            'Y': item['position']['y'],
            'Z': item['position']['z'],
            'Rotation': item.get('rotation', 0),
            'Scale_X': item.get('scale', {}).get('x', 1),
            'Scale_Y': item.get('scale', {}).get('y', 1),
        }
        # Добавляем атрибуты
        for attr, value in item['attributes'].items():
            row[f'Attr_{attr}'] = value
        rows.append(row)
    
    df = pd.DataFrame(rows)
    return df

def create_visualizations(df):
    """Создает визуализации данных"""
    
    try:
        # Настройка стиля
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # 1. Распределение блоков по координатам
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Scatter plot позиций
        axes[0].scatter(df['X'], df['Y'], s=100, alpha=0.6)
        axes[0].set_title('Расположение блоков')
        axes[0].set_xlabel('X координата')
        axes[0].set_ylabel('Y координата')
        axes[0].grid(True, alpha=0.3)
        
        # Гистограмма по X
        axes[1].hist(df['X'], bins=10, alpha=0.7, color='blue')
        axes[1].set_title('Распределение по X')
        axes[1].set_xlabel('X координата')
        axes[1].set_ylabel('Количество')
        
        # Гистограмма по Y
        axes[2].hist(df['Y'], bins=10, alpha=0.7, color='green')
        axes[2].set_title('Распределение по Y')
        axes[2].set_xlabel('Y координата')
        axes[2].set_ylabel('Количество')
        
        plt.tight_layout()
        plt.savefig('visualizations.png', dpi=300, bbox_inches='tight')
        print("\n📊 Визуализация сохранена: visualizations.png")
        plt.show()
        
        # 2. Анализ атрибутов
        attr_cols = [col for col in df.columns if col.startswith('Attr_')]
        if attr_cols:
            fig, axes = plt.subplots(1, len(attr_cols), figsize=(5*len(attr_cols), 4))
            if len(attr_cols) == 1:
                axes = [axes]
            
            for i, attr in enumerate(attr_cols):
                values = df[attr].value_counts()
                axes[i].bar(values.index, values.values, alpha=0.7)
                axes[i].set_title(f'Распределение\n{attr.replace("Attr_", "")}')
                axes[i].set_xlabel('Значение')
                axes[i].set_ylabel('Количество')
                axes[i].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig('attributes_analysis.png', dpi=300, bbox_inches='tight')
            print("📊 Анализ атрибутов сохранен: attributes_analysis.png")
            plt.show()
            
    except Exception as e:
        print(f"⚠️ Ошибка при создании визуализаций: {e}")
        print("   (Возможно, не установлены matplotlib или pandas)")

if __name__ == "__main__":
    # Анализируем данные
    data = analyze_json_data('extracted_data.json')
    
    if data:
        # Создаем DataFrame для детального анализа
        df = create_pandas_dataframe(data)
        print("\n📊 DataFrame (первые 5 строк):")
        print(df.head())
        
        # Сохраняем DataFrame в Excel
        try:
            df.to_excel('analysis_report.xlsx', index=False)
            print("\n📊 Excel отчет сохранен: analysis_report.xlsx")
        except Exception as e:
            print(f"⚠️ Ошибка при создании Excel: {e}")
        
        # Создаем визуализации
        create_visualizations(df)