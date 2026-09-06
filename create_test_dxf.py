import ezdxf

# Создаем новый DXF документ (формат R2010)
doc = ezdxf.new('R2010')

# Получаем пространство модели (model space)
msp = doc.modelspace()

# Добавляем различные примитивы для тестирования

# 1. Линия
msp.add_line((0, 0), (100, 100))

# 2. Окружность
msp.add_circle((50, 50), 30)

# 3. Прямоугольник (полилиния)
points = [(0, 0), (50, 0), (50, 30), (0, 30), (0, 0)]
msp.add_lwpolyline(points)

# 4. Текст
msp.add_text("Тестовый DXF файл", 
             dxfattribs={'height': 5, 'insert': (10, 80)})

# 5. Дуга
msp.add_arc((50, 50), 40, 0, 180)

# 6. Точки
msp.add_point((20, 20))
msp.add_point((30, 30))

# 7. Сплайн
points = [(10, 10), (20, 30), (40, 20), (50, 40), (70, 30)]
msp.add_spline(points)

# Сохраняем файл
doc.saveas('test_drawing.dxf')
print("DXF файл успешно создан: test_drawing.dxf")