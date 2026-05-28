# Карта дизайн-кода соседнего Dashboard

Источник анализа: `/opt/dashboard` на сервере.

Цель: зафиксировать визуальную систему соседнего сервиса, чтобы переиспользовать ее в Django-сервисе тестирования VPN и мессенджеров без слепого копирования всей кодовой базы.

## 1. Ключевые файлы дизайна

| Файл | Роль |
| --- | --- |
| `/opt/dashboard/app/templates/base.html` | Базовый layout: sidebar, навигация, пользовательский блок, контентная область |
| `/opt/dashboard/app/static/app.css` | Основная дизайн-система: токены, layout, карточки, таблицы, формы, кнопки, login |
| `/opt/dashboard/app/static/app.js` | UI-поведение: поиск навигации, ресайз sidebar, таблицы, графики, кнопки-иконки |
| `/opt/dashboard/app/templates/auth/login.html` | Страница входа с премиальной анимацией |
| `/opt/dashboard/LoginPage.module.css` | Альтернативная React-версия дизайна login-страницы |
| `/opt/dashboard/LoginPage.tsx` | React-логика анимированного login flow |
| `/opt/dashboard/app/static/mintsifry.svg` | Брендовый SVG-логотип |

## 2. Дизайн-токены

Основные CSS-переменные находятся в `app/static/app.css`.

```css
:root {
  --sidebar-width: 320px;
  --bg: #ffffff;
  --bg-soft: #e8eaf0;
  --bg-soft-2: #d7e1fb;
  --line: #cfd8ee;
  --line-strong: #97ace6;
  --text: #050505;
  --muted: #5d6785;
  --brand: #3207ff;
  --brand-dark: #2812b1;
  --brand-deep: #0e0066;
  --danger: #bf1736;
  --radius: 26px;
  --radius-sm: 16px;
  --shadow: 0 24px 60px rgba(14, 0, 102, 0.08);
  --accent: #3207ff;
}
```

### Визуальный характер

- Светлый интерфейс.
- Основной акцент: насыщенный сине-фиолетовый `#3207ff`.
- Фон: белый + мягкие холодные серо-голубые зоны.
- Скругления крупные: 16-36px.
- Карточки с тонкой голубой рамкой и мягкой тенью.
- Активные элементы часто имеют градиент `brand -> brand-dark`.
- Шрифт: `"TT Firs Neue", "Inter", "Segoe UI", sans-serif`.

## 3. Layout

### Основная сетка

```css
.layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
}

.layout--with-sidebar {
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
}
```

### Sidebar

Ключевые классы:

- `.sidebar`
- `.sidebar-frame`
- `.brand`
- `.brand-logo`
- `.sidebar-search`
- `.nav`
- `.nav-tree`
- `.nav-tree__group`
- `.nav-tree__summary`
- `.nav-tree__link`
- `.nav-tree__link.is-active`
- `.sidebar-user`
- `.sidebar-logout`

Характер sidebar:

- Левый sticky sidebar на всю высоту экрана.
- Внутри отдельная скругленная рамка `.sidebar-frame`.
- Фон sidebar: вертикальный светлый градиент.
- Навигация древовидная через `<details>/<summary>`.
- Активный пункт выделяется сине-фиолетовым градиентом.
- Есть поиск по пунктам меню.
- Есть ручка ресайза ширины sidebar.

Для нашего сервиса можно переиспользовать:

- общий layout с левой навигацией;
- активное состояние пункта меню;
- поиск по меню, если разделов станет много;
- блок пользователя внизу sidebar.

## 4. Header / Hero

Ключевые классы:

- `.page-header`
- `.hero-banner`
- `.hero-copy`
- `.eyebrow`
- `.hero-aside`
- `.hero-aside__label`
- `.hero-aside__meta`

Паттерн:

```html
<section class="page-header">
  <div class="hero-copy">
    <div class="eyebrow">Раздел</div>
    <h1>Название<br>экрана</h1>
  </div>
  <aside class="hero-aside">
    <div class="hero-aside__label">Назначение</div>
    <p>Короткое описание экрана.</p>
  </aside>
</section>
```

Особенности:

- Большой скругленный блок.
- Левая часть залита brand-градиентом.
- Справа белая информационная вставка.
- H1 крупный, часто с переносом строки.

Для нашего сервиса этот паттерн лучше использовать только на крупных разделах:

- Контроль анкет.
- Экспорт.
- Справочники.
- Главная / каталог разделов.

Для рабочих форм заполнения анкет лучше оставить более спокойный интерфейс, чтобы не перегружать тестировщика.

## 5. Карточки и панели

Ключевые классы:

- `.panel`
- `.panel-compact`
- `.panel-heading`
- `.metric-card`
- `.cards-grid`
- `.dashboard-card-group`
- `.dashboard-cards-grid`
- `.dashboard-card`
- `.dashboard-card__description`
- `.dashboard-card__footer`

Паттерн панели:

```html
<section class="panel">
  <h2>Заголовок</h2>
  ...
</section>
```

Паттерн карточки:

```html
<a class="dashboard-card" href="#">
  <div class="eyebrow">Тип</div>
  <h3>Название</h3>
  <p class="dashboard-card__description">Описание</p>
  <div class="dashboard-card__footer">
    <span class="dashboard-card__label">Дата данных</span>
    <strong>26.05.2026</strong>
  </div>
</a>
```

Характер:

- Карточки крупные.
- Радиус 28px.
- Фон: белый с мягким вертикальным серо-голубым градиентом.
- Hover: легкий подъем `translateY(-2px)`.

Для нашего сервиса:

- Подходит для главной страницы и раздела “Контроль”.
- В таблицах анкет лучше не заменять строки карточками, чтобы не потерять плотность.

## 6. Формы

Ключевые классы:

- `.filter-form`
- `.inline-form`
- `.form-grid`
- `.stack`
- `.wide`
- `.form-actions`
- `.search-field`
- `.search-field__label`
- `.toggle-field`

Базовые стили input/select/textarea:

```css
input,
select,
textarea {
  width: 100%;
  padding: 11px 14px;
  border-radius: 14px;
  border: 1px solid rgba(151, 172, 230, 0.75);
  background: #fff;
  color: var(--text);
}

input:focus,
select:focus,
textarea:focus {
  outline: 2px solid rgba(50, 7, 255, 0.18);
  border-color: var(--brand);
}
```

Сетка формы:

```css
.form-grid {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.wide {
  grid-column: 1 / -1;
}
```

Для нашего сервиса:

- Можно заменить текущие Bootstrap-поля на общий класс `form-grid`.
- Для фильтров анкет использовать `.filter-form`: flex-wrap, компактно, кнопки в конце.
- Focus-состояние мягкое и приятное, стоит перенести.

## 7. Кнопки

Ключевые классы:

- `.button`
- `.button.ghost`
- `.button.danger`
- `.button.small`
- `.emoji-icon-button`
- `.emoji-icon-button--danger`
- `.emoji-icon-button--subtle`

Базовая кнопка:

```css
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px;
  padding: 11px 18px;
  border: 1px solid transparent;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--brand) 0%, var(--brand-dark) 100%);
  color: white;
  cursor: pointer;
}

.button.ghost {
  background: white;
  color: var(--text);
  border-color: rgba(151, 172, 230, 0.8);
}

.button.danger {
  background: var(--danger);
}
```

Icon-button система:

- Размер: 46x46px.
- Радиус: 13px.
- Border: `#C8D4F8`.
- Hover: светло-голубой фон.
- Active: темно-синий фон `#243B8F`.

В `app/static/app.js` есть единая карта emoji-иконок:

```js
const dashboardEmojiIcons = {
  settings: "⚙️",
  download: "⬇️",
  search: "🔍",
  refresh: "🔄",
  edit: "✏️",
  delete: "🗑️",
  add: "＋",
  save: "💾",
  close: "✕",
  back: "←",
  forward: "→",
  sortUp: "↑",
  sortDown: "↓",
};
```

Для нашего сервиса:

- Можно оставить текстовые кнопки для основных действий.
- Иконки использовать осторожно: скачать Excel, очистить фильтр, удалить, назад.
- Лучше не тащить emoji-систему полностью, а сделать небольшую карту на нужные действия.

## 8. Таблицы

Ключевые классы:

- `.table-wrap`
- `.sortable-th`
- `.draggable-th`
- `.column-resize-handle`
- `.table-actions`
- `.table-pagination`

Базовая таблица:

```css
table {
  width: 100%;
  min-width: 840px;
  border-collapse: collapse;
}

th,
td {
  padding: 14px 12px;
  border-bottom: 1px solid rgba(207, 216, 238, 0.9);
  vertical-align: top;
  text-align: left;
}

th {
  color: var(--muted);
  font-size: 0.92rem;
  font-weight: 500;
}
```

Сортировка:

```css
.sortable-th {
  cursor: pointer;
  user-select: none;
}

.sortable-th::after {
  content: " ↕";
  color: rgba(93, 103, 133, 0.55);
}

.sortable-th.is-sorted-asc::after {
  content: " ↑";
  color: var(--accent);
}

.sortable-th.is-sorted-desc::after {
  content: " ↓";
  color: var(--accent);
}
```

Для нашего сервиса:

- Очень подходит для списков VPN-анкет, мессенджеров и контроля.
- Стоит перенести:
  - `.table-wrap`;
  - плотные строки с `border-bottom`;
  - сортируемые заголовки;
  - `table-actions` для кнопок справа.

## 9. Alerts / сообщения

Класс:

- `.alert`
- `.login-alert`

Стиль:

```css
.alert {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(191, 23, 54, 0.08);
  color: var(--danger);
}
```

Login alert:

- фон `rgba(191, 23, 54, 0.08)`;
- border `rgba(191, 23, 54, 0.2)`;
- радиус 18px.

Для нашего сервиса:

- Ошибки форм можно сделать компактнее в этом стиле.
- Предупреждения лучше добавить отдельным токеном warning, потому что в Dashboard основной alert — красный.

## 10. Login-страница

Есть два варианта:

1. Реальный используемый Jinja login:
   - `/opt/dashboard/app/templates/auth/login.html`
   - стили в `/opt/dashboard/app/static/app.css`, начиная с блока `Премиальная анимация входа`.

2. React-прототип:
   - `/opt/dashboard/LoginPage.tsx`
   - `/opt/dashboard/LoginPage.module.css`

### Jinja login визуально

Ключевые классы:

- `.login-page`
- `.login-bg`
- `.login-bg__grid`
- `.login-bg__grid-dots`
- `.login-bg__emblem`
- `.login-bg__glow`
- `.login-bg__pulses`
- `.login-card`
- `.login-logo-wrap`
- `.login-logo`
- `.login-form`
- `.login-form__group`
- `.login-form__label`
- `.login-form__input`
- `.login-alert`
- `.login-button`
- `.login-statuses`
- `.login-progress`

Характер:

- Full-screen страница.
- Светлый фон с тонкой сеткой.
- Водяной знак логотипа.
- Центральная карточка 468px.
- Большие скругления 36-42px.
- Анимации: дыхание карточки, линии вокруг логотипа, прогресс.

Для нашего сервиса:

- Можно переиспользовать фон/карточку login.
- Не обязательно переносить сложную SVG-анимацию целиком.
- Лучше сделать упрощенную версию:
  - светлый grid background;
  - центральная карточка;
  - logo;
  - те же input/button.

## 11. Адаптив

Breakpoint-ы:

- `1200px`
- `1024px`
- `820px`
- `680px`
- `480px`
- `prefers-reduced-motion: reduce`

Основная логика:

- До 1024px sidebar перестает быть sticky-сайдбаром и становится верхним горизонтальным блоком.
- Навигация на планшете становится горизонтально прокручиваемой.
- На 820px формы и карточки переходят в одну колонку.
- Таблицы остаются широкими и скроллятся внутри `.table-wrap`.
- На 680px уменьшаются радиусы и отступы.
- Есть отдельная поддержка `prefers-reduced-motion`.

Для нашего сервиса:

- Можно использовать те же breakpoint-ы.
- Таблицы не пытаться ужимать до мобильных карточек сразу; достаточно `.table-wrap`.
- Пошаговые анкеты лучше оставить одноэкранными и вертикальными.

## 12. JS-поведение, которое можно переиспользовать

В `app/static/app.js` есть:

- автоматическая подстановка CSRF-токена в mutating fetch;
- поиск по навигации;
- сохранение scroll позиции sidebar;
- сохранение ширины sidebar по пользователю;
- сортировка таблиц;
- настройки графиков;
- управление popover-ами;
- resize колонок таблиц;
- экспорт таблиц;
- drag/drop порядка карточек.

Для нашего сервиса первыми стоит переносить:

1. Активное состояние меню.
2. Поиск/фильтрация навигации, если меню станет длинным.
3. Сортировку таблиц.
4. Сохранение ширины sidebar, если перейдем на sidebar-layout.

Графики, drag/drop и сложные popover-ы пока не нужны.

## 13. Что переносить в наш Django-сервис в первую очередь

### Приоритет 1

- CSS-токены `:root`.
- Общий фон и типографика.
- `.button`, `.button.ghost`, `.button.danger`, `.button.small`.
- Стили input/select/textarea.
- `.panel`, `.panel-heading`, `.form-grid`, `.filter-form`.
- `.table-wrap`, базовые table/th/td.
- `.sortable-th`.

### Приоритет 2

- Sidebar layout вместо текущего верхнего меню.
- `.page-header` для крупных разделов.
- `.dashboard-card` для главной страницы.
- Login page в стиле Dashboard.

### Приоритет 3

- Emoji icon button система.
- Resizable sidebar.
- Поиск по меню.
- Анимированный login flow.

## 14. Что не стоит переносить напрямую

- Chart.js-логику, потому что у нас пока нет аналитики.
- Drag/drop порядка карточек.
- Большие dashboard-специфичные блоки:
  - `.service-check-*`
  - `.contract-board-*`
  - `.vciom-*`
  - `.chart-*`
- React `LoginPage.tsx`, потому что наш проект без React.

## 15. Рекомендованная схема внедрения в наш проект

### Шаг 1. Design tokens

Добавить в наш `static/css/styles.css` блок переменных из Dashboard, но адаптировать радиусы под рабочий интерфейс:

- `--radius: 18px`
- `--radius-sm: 12px`
- `--shadow` оставить мягкий.

### Шаг 2. Компоненты

Создать классы-аналоги:

- `.app-panel`
- `.app-button`
- `.app-button--ghost`
- `.app-button--danger`
- `.app-form-grid`
- `.app-table-wrap`
- `.app-sortable-th`

Лучше не конфликтовать напрямую с Bootstrap-классами.

### Шаг 3. Навигация

Переехать с верхнего меню на layout:

```html
<div class="layout layout--with-sidebar">
  <aside class="sidebar">...</aside>
  <main class="content">...</main>
</div>
```

### Шаг 4. Таблицы

Обновить:

- список VPN-анкет;
- список анкет мессенджеров;
- контроль анкет;
- экспорт.

### Шаг 5. Login

Сделать упрощенную login-страницу:

- grid background;
- центральная карточка;
- логотип;
- поля и кнопка в стиле Dashboard.

## 16. Быстрый CSS-скелет для переноса

```css
:root {
  --app-bg: #ffffff;
  --app-bg-soft: #e8eaf0;
  --app-line: #cfd8ee;
  --app-line-strong: #97ace6;
  --app-text: #050505;
  --app-muted: #5d6785;
  --app-brand: #3207ff;
  --app-brand-dark: #2812b1;
  --app-brand-deep: #0e0066;
  --app-danger: #bf1736;
  --app-radius: 18px;
  --app-radius-sm: 12px;
  --app-shadow: 0 24px 60px rgba(14, 0, 102, 0.08);
}

.app-panel {
  background: var(--app-bg);
  border: 1px solid rgba(151, 172, 230, 0.45);
  border-radius: var(--app-radius);
  box-shadow: var(--app-shadow);
  padding: 20px;
}

.app-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  padding: 10px 16px;
  border: 1px solid transparent;
  border-radius: var(--app-radius-sm);
  background: linear-gradient(135deg, var(--app-brand) 0%, var(--app-brand-dark) 100%);
  color: #fff;
  cursor: pointer;
}

.app-button--ghost {
  background: #fff;
  color: var(--app-text);
  border-color: rgba(151, 172, 230, 0.8);
}

.app-button--danger {
  background: var(--app-danger);
}

.app-form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.app-table-wrap {
  overflow-x: auto;
}

.app-table {
  width: 100%;
  min-width: 840px;
  border-collapse: collapse;
}

.app-table th,
.app-table td {
  padding: 14px 12px;
  border-bottom: 1px solid rgba(207, 216, 238, 0.9);
  text-align: left;
  vertical-align: top;
}

.app-table th {
  color: var(--app-muted);
  font-size: 0.92rem;
  font-weight: 600;
}
```

## 17. Итоговая дизайн-формула

Dashboard держится на пяти вещах:

1. Светлая холодная палитра с сильным brand-акцентом.
2. Большие скругления и мягкие тени.
3. Sidebar вместо верхнего меню.
4. Таблицы с чистыми линиями и спокойной плотностью.
5. Аккуратные формы с мягким focus и крупными кнопками.

Для нашего сервиса это хорошо подходит, но переносить нужно дозированно: анкеты должны остаться быстрыми и рабочими, а “премиальность” лучше оставить для входа, главной, контроля и экспорта.
