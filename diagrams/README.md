# 📊 Діаграми Investment Portfolio Management System

Цей каталог містить всі PlantUML діаграми для документації системи управління інвестиційним портфелем.

## 📁 Структура файлів

| Файл | Назва діаграми | Опис |
|------|----------------|------|
| [01-class-diagram.md](01-class-diagram.md) | **UML-діаграма класів** | Структура класів, Repository Pattern, Layered Architecture |
| [02-er-diagram.md](02-er-diagram.md) | **ER-діаграма** | Структура баз даних, таблиці, зв'язки, Database per Service pattern |
| [03-system-context.md](03-system-context.md) | **Архітектурна схема взаємодії** | C4 System Context, актори, зовнішні системи |
| [04-microservices-architecture.md](04-microservices-architecture.md) | **Схема мікросервісної архітектури** | Container Diagram, внутрішня структура сервісів |
| [05-service-interactions.md](05-service-interactions.md) | **Взаємодія між сервісами** | Sequence Diagrams для BUY/SELL/Analytics/Caching |
| [06-docker-containers.md](06-docker-containers.md) | **Схема контейнерів** | Docker Compose, volumes, networks, lifecycle |
| [07-service-relationships.md](07-service-relationships.md) | **Зв'язки між сервісами** | Kubernetes deployment, traffic flow, rolling updates |

## 🚀 Як використовувати діаграми

### Метод 1: PlantUML Online Editor (найпростіший)

1. Відкрийте [PlantUML Online Editor](https://www.plantuml.com/plantuml/uml/)
2. Відкрийте потрібний `.md` файл
3. Скопіюйте код з блоку \`\`\`plantuml
4. Вставте в онлайн редактор
5. Натисніть "Submit" або `Ctrl+S`
6. Збережіть діаграму як PNG або SVG для звіту

**Переваги:**
- ✅ Не потрібно нічого встановлювати
- ✅ Працює в браузері
- ✅ Швидко для перегляду

**Недоліки:**
- ❌ Потрібен інтернет
- ❌ Немає автозбереження

### Метод 2: VS Code + PlantUML Extension (рекомендовано)

#### Встановлення

1. **Встановіть Java** (потрібно для PlantUML):
   ```powershell
   # Використайте chocolatey або завантажте з https://www.java.com
   choco install openjdk11
   ```

2. **Встановіть Graphviz** (потрібно для деяких діаграм):
   ```powershell
   choco install graphviz
   ```

3. **Встановіть VS Code Extension**:
   - Відкрийте VS Code
   - `Ctrl+Shift+X` → Пошук "PlantUML"
   - Встановіть "PlantUML" від jebbs

#### Використання

1. Створіть файл з розширенням `.puml` або `.plantuml`
2. Скопіюйте PlantUML код з `.md` файлу
3. Вставте в `.puml` файл
4. Натисніть `Alt+D` для Preview
5. Або клікніть правою кнопкою → "Export Current Diagram"

**Формати експорту:**
- PNG (для звіту)
- SVG (векторна графіка, масштабується)
- PDF (для документації)

**Переваги:**
- ✅ Живий preview під час редагування
- ✅ Підтримка auto-completion
- ✅ Зручний експорт в різні формати
- ✅ Працює офлайн

### Метод 3: Command Line (для автоматизації)

#### Встановлення

```powershell
# Завантажте PlantUML JAR
Invoke-WebRequest -Uri "https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar" -OutFile "plantuml.jar"
```

#### Використання

```powershell
# Конвертувати один файл
java -jar plantuml.jar diagram.puml

# Конвертувати всі файли в каталозі
java -jar plantuml.jar *.puml

# Експортувати в SVG
java -jar plantuml.jar -tsvg diagram.puml

# Експортувати в PDF
java -jar plantuml.jar -tpdf diagram.puml
```

## 📋 Швидкий старт для звіту

### Крок 1: Експортуйте всі діаграми

Створіть скрипт `export-diagrams.ps1`:

```powershell
# Створіть .puml файли з .md файлів
$mdFiles = Get-ChildItem -Path "diagrams" -Filter "*.md"

foreach ($mdFile in $mdFiles) {
    $content = Get-Content $mdFile.FullName -Raw
    
    # Extract all PlantUML code blocks
    $pattern = '```plantuml(.*?)```'
    $matches = [regex]::Matches($content, $pattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)
    
    $counter = 1
    foreach ($match in $matches) {
        $pumlCode = $match.Groups[1].Value.Trim()
        $baseName = $mdFile.BaseName
        $outputFile = "diagrams\exports\${baseName}-${counter}.puml"
        
        Set-Content -Path $outputFile -Value $pumlCode
        
        # Generate PNG
        java -jar plantuml.jar -tpng $outputFile
        
        $counter++
    }
}

Write-Host "Exported all diagrams to diagrams/exports/" -ForegroundColor Green
```

Запустіть:
```powershell
.\export-diagrams.ps1
```

### Крок 2: Вставте в звіт

Тепер у вас є PNG файли для вставки в Word/Google Docs звіт.

## 🎯 Які діаграми використовувати в звіті

### Для Lab #2 (REST API)
- ✅ [01-class-diagram.md](01-class-diagram.md) - показує Router, Service, Repository структуру
- ✅ [02-er-diagram.md](02-er-diagram.md) - показує структуру даних

### Для Lab #4 (Мікросервіси)
- ✅ [03-system-context.md](03-system-context.md) - високорівнева архітектура
- ✅ [04-microservices-architecture.md](04-microservices-architecture.md) - деталі мікросервісів
- ✅ [05-service-interactions.md](05-service-interactions.md) - як сервіси взаємодіють

### Для Lab #5 (Docker & Кешування)
- ✅ [06-docker-containers.md](06-docker-containers.md) - Docker Compose архітектура
- ✅ [05-service-interactions.md](05-service-interactions.md) - Діаграма 4 (Caching Flow)

### Для Lab #6 (Kubernetes)
- ✅ [07-service-relationships.md](07-service-relationships.md) - Kubernetes deployment
- ✅ [07-service-relationships.md](07-service-relationships.md) - Rolling Update strategy

## 🎨 Кастомізація діаграм

### Зміна кольорів

У PlantUML коді знайдіть секцію `skinparam` або `!define`:

```plantuml
' Змінити колір фону
skinparam componentBackgroundColor LightBlue

' Змінити колір ліній
skinparam componentBorderColor Black

' Кастомні кольори для конкретних елементів
rectangle "My Component" <<custom>> #FF6B6B
```

### Зміна макету

```plantuml
' Напрямок компонування
left to right direction  ' або top to bottom direction

' Використання lanes (swimlanes)
|Lane1|
:Activity;
|Lane2|
:Another Activity;
```

### Додавання нотаток

```plantuml
note right of ComponentName
  Ваш текст тут
  • Можна використовувати списки
  • **Жирний текст**
  • `Код`
end note
```

## 📚 Корисні посилання

### Офіційна документація
- [PlantUML Official Site](https://plantuml.com/)
- [PlantUML Language Reference](https://plantuml.com/guide)
- [PlantUML Stdlib](https://github.com/plantuml/plantuml-stdlib)

### Онлайн інструменти
- [PlantUML Online Editor](https://www.plantuml.com/plantuml/uml/)
- [PlantText (альтернативний editor)](https://www.planttext.com/)
- [Real-time PlantUML Editor](https://liveuml.com/)

### Приклади та бібліотеки
- [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) - C4 Model templates
- [AWS PlantUML](https://github.com/awslabs/aws-icons-for-plantuml) - AWS icons
- [Kubernetes PlantUML](https://github.com/dcasati/kubernetes-PlantUML) - K8s icons
- [Azure PlantUML](https://github.com/plantuml-stdlib/Azure-PlantUML) - Azure icons

### Туторіали
- [PlantUML Quick Start](https://plantuml.com/starting)
- [C4 Model](https://c4model.com/) - Software architecture diagrams
- [UML Diagrams Tutorial](https://www.uml-diagrams.org/)

## ⚙️ Troubleshooting

### Помилка: "Cannot find Java"

```powershell
# Перевірте Java
java -version

# Якщо не встановлено:
choco install openjdk11
# Або завантажте з https://www.java.com
```

### Помилка: "Graphviz not found"

Деякі діаграми потребують Graphviz:

```powershell
choco install graphviz

# Додайте до PATH
$env:PATH += ";C:\Program Files\Graphviz\bin"
```

### Діаграма не рендериться в VS Code

1. Перевірте, що PlantUML extension встановлено
2. Перевірте Java: `java -version`
3. Restart VS Code
4. Перевірте Output panel: View → Output → PlantUML

### Занадто великий розмір діаграми

```plantuml
' Додайте на початок файлу
skinparam dpi 150  ' Зменшити для меншого розміру
scale 0.8          ' Зменшити масштаб
```

## 🎓 Пояснення для преподавателя

### Чому PlantUML?

**Переваги:**
1. **Діаграми як код** - легко версіонувати в Git
2. **Автоматична компонування** - PlantUML сам розташовує елементи
3. **Консистентність** - всі діаграми в одному стилі
4. **Легко оновлювати** - змінити код → нова діаграма
5. **Не треба drag-and-drop** - швидше, ніж Visio/Draw.io

**Альтернативи:**
- Microsoft Visio (платний, GUI)
- Draw.io / diagrams.net (безкоштовний, GUI)
- Lucidchart (платний, online)
- Mermaid (схожий на PlantUML, менше функцій)

### Відповідність вимогам лабораторних

| Лабораторна | Діаграма | Що демонструє |
|-------------|----------|---------------|
| Lab #2 | Class Diagram, ER Diagram | REST API структура, Entity design |
| Lab #4 | Microservices Architecture, Service Interactions | Розділення на мікросервіси, HTTP communication |
| Lab #5 | Docker Containers, Caching Flow | Docker Compose, Redis caching |
| Lab #6 | Kubernetes Deployment, Rolling Updates | K8s manifests, HA, zero-downtime |

### Еволюція від монолітної до мікросервісної

Діаграми показують:
1. **Від 1 БД до 3 БД** - Database per Service pattern (02-er-diagram.md)
2. **Від 1 процесу до 4 процесів** - Service separation (04-microservices-architecture.md)
3. **Від SQL JOIN до HTTP запитів** - Inter-service communication (05-service-interactions.md)
4. **Від 1 deployment до 4 deployments** - Independent scaling (07-service-relationships.md)

## 📝 Checklist для здачі звіту

- [ ] Експортував всі потрібні діаграми в PNG/SVG
- [ ] Class Diagram показує всі основні класи
- [ ] ER Diagram показує 3 окремі бази даних
- [ ] System Context показує актори та зовнішні системи
- [ ] Microservices Architecture показує 4 сервіси
- [ ] Service Interactions показує BUY/SELL/Analytics flows
- [ ] Docker Containers показує docker-compose setup
- [ ] Kubernetes Deployment показує 2+ replicas
- [ ] Rolling Update показує zero-downtime strategy
- [ ] Додав підписи до діаграм в звіті
- [ ] Пояснив основні патерни (Repository, Cache-Aside, etc.)

## 🔍 Приклад використання в звіті

### Розділ: Архітектура системи

**Текст:**
> Система складається з 4 мікросервісів, кожен з яких має окрему відповідальність. 
> Asset Service управляє активами та використовує Redis для кешування (Lab #5 requirement).
> Transaction Service обробляє купівлю/продаж з валідацією через HTTP запити до інших сервісів.
> Portfolio Service управляє інвесторами та портфелями.
> Analytics Service агрегує дані з усіх сервісів для генерації звітів.

**Діаграма 1:** Вставте `04-microservices-architecture-1.png`

**Підпис:**
> Рис. 1. Мікросервісна архітектура системи з 4 сервісами та окремими базами даних

---

### Розділ: Взаємодія сервісів

**Текст:**
> При купівлі активу Transaction Service спочатку перевіряє існування активу через Asset Service,
> потім перевіряє баланс інвестора через Portfolio Service, і тільки після успішної валідації
> створює транзакцію в своїй базі даних.

**Діаграма 2:** Вставте `05-service-interactions-1.png` (BUY flow)

**Підпис:**
> Рис. 2. Sequence diagram процесу купівлі активу з міжсервісною взаємодією

---

## 💡 Поради

1. **Для швидкого перегляду** - використайте PlantUML Online Editor
2. **Для редагування** - використайте VS Code з PlantUML extension
3. **Для звіту** - експортуйте в PNG з високим DPI (300+)
4. **Для презентації** - експортуйте в SVG (векторна графіка)
5. **Не змінюйте кольори** - вони вже оптимізовані для друку та перегляду

## 📞 Підтримка

Якщо є проблеми з генерацією діаграм:
1. Перевірте, що Java встановлено: `java -version`
2. Перевірте синтаксис PlantUML: [PlantUML Online Editor](https://www.plantuml.com/plantuml/uml/)
3. Прочитайте коментарі в `.md` файлах - там є підказки
4. Перегляньте секцію Troubleshooting вище

---

**Успіхів з лабораторними роботами! 🚀**
