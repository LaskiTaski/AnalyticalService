# Архитектура фронтенда

## Принципы

1. **Фронтенд не считает** — все расчёты, фильтрация, сортировка, агрегация выполняются на бэкенде. Фронтенд получает готовые данные и отрисовывает.
2. **Server state ≠ client state** — данные с сервера живут в TanStack Query (кэш, фоновое обновление). Локальный UI-стейт (модалки, формы) — в useState/Zustand.
3. **Типизация везде** — TypeScript strict mode. API-типы генерируются из OpenAPI схемы.
4. **Компоненты владеют своим стилем** — Tailwind CSS утилиты, никаких глобальных CSS файлов (кроме переменных темы).

## Структура

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── api/                    # HTTP-клиент и типы
│   │   ├── client.ts           # Axios instance с interceptors
│   │   ├── bonds.ts            # getBonds(), getBond(), getMarketOverview()
│   │   └── types.ts            # TypeScript типы (из OpenAPI)
│   ├── components/
│   │   ├── ui/                 # shadcn/ui компоненты (Button, Input, Table, Card...)
│   │   ├── layout/             # Header, Sidebar, Footer, Layout
│   │   ├── bonds/              # BondTable, BondCard, BondFilters, BondDetail
│   │   ├── dashboard/          # MarketOverview, Charts, TopBonds
│   │   └── common/             # Loading, Error, Pagination, EmptyState
│   ├── pages/                  # Страницы (1 файл = 1 route)
│   │   ├── ScreenerPage.tsx    # /screener — таблица + фильтры
│   │   ├── BondPage.tsx        # /bonds/:secid — детали облигации
│   │   ├── DashboardPage.tsx   # /dashboard — обзор рынка
│   │   ├── LandingPage.tsx     # / — лендинг
│   │   ├── LoginPage.tsx       # /login
│   │   └── PricingPage.tsx     # /pricing — тарифы
│   ├── hooks/                  # Кастомные хуки
│   │   ├── useBonds.ts         # useQuery обёртка для облигаций
│   │   ├── useFilters.ts       # Состояние фильтров (URL search params)
│   │   └── useAuth.ts          # Авторизация
│   ├── lib/                    # Утилиты
│   │   ├── utils.ts            # cn(), formatCurrency(), formatDate()
│   │   └── constants.ts        # FILTER_PRESETS, SORT_OPTIONS
│   ├── styles/
│   │   └── globals.css         # Tailwind directives, CSS variables для темы
│   ├── App.tsx                 # Корневой компонент с роутером
│   └── main.tsx                # Entry point
├── index.html
├── tailwind.config.ts
├── tsconfig.json
├── vite.config.ts
└── package.json
```

## Ключевые компоненты

### ScreenerPage (главная ценность)
```
┌─────────────────────────────────────────────────────────────┐
│  Header (лого, навигация, тема, профиль)                   │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│  Фильтры     │  Таблица облигаций                          │
│  (sidebar)   │                                              │
│              │  ┌─────┬────────┬──────┬──────┬──────┬─────┐ │
│  Доходность  │  │Назв.│ Тикер  │ Цена │ Дох. │Купон │Дней │ │
│  [от] [до]   │  ├─────┼────────┼──────┼──────┼──────┼─────┤ │
│              │  │ ... │  ...   │ ...  │ ...  │ ...  │ ... │ │
│  Купон       │  │ ... │  ...   │ ...  │ ...  │ ...  │ ... │ │
│  [от] [до]   │  │ ... │  ...   │ ...  │ ...  │ ...  │ ... │ │
│              │  └─────┴────────┴──────┴──────┴──────┴─────┘ │
│  Срок        │                                              │
│  [от] [до]   │  Пагинация: < 1 2 3 ... 115 >              │
│              │                                              │
│  Тип         │                                              │
│  ☑ ОФЗ       │                                              │
│  ☑ Корп.     │                                              │
│  ☑ Муни.     │                                              │
│              │                                              │
│  Листинг     │                                              │
│  ○ 1 ○ 2 ○ 3│                                              │
│              │                                              │
│  Квал.       │                                              │
│  ☐ Только    │                                              │
│    неквал.   │                                              │
│              │                                              │
│  [Сбросить]  │                                              │
│              │                                              │
├──────────────┴──────────────────────────────────────────────┤
│  Footer                                                     │
└─────────────────────────────────────────────────────────────┘
```

### BondPage (детали)
```
┌─────────────────────────────────────────────────────────────┐
│  ← Назад к скринеру                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Магнит4P05 (RU000A10A9Z1)                    🏢 Корп.     │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Цена     │  │ Доход.   │  │ Купон    │  │ Дней     │   │
│  │ 98.92%   │  │ 16.85%   │  │ 38.01₽   │  │ 1348     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  [Основное] [Купоны] [История] [Похожие]                   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Детальная информация / графики / таблицы             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```typescript
// 1. Пользователь меняет фильтр
const [filters, setFilters] = useFilters() // синхронизирует с URL search params

// 2. TanStack Query автоматически делает запрос
const { data, isLoading } = useQuery({
  queryKey: ['bonds', filters],
  queryFn: () => api.getBonds(filters),
  keepPreviousData: true, // показывает старые данные пока грузятся новые
})

// 3. Компонент отрисовывает
<BondTable data={data.items} loading={isLoading} />
```

## Дизайн-система

Вдохновление: Snowball Income.

- **Тёмная тема** как основная (светлая — переключатель)
- **Цвета:** нейтральная база (zinc/slate), зелёный для роста, красный для падения
- **Типографика:** Inter или Manrope — чистые, современные шрифты
- **Отступы:** 4px grid system (Tailwind default)
- **Карточки:** скруглённые углы, subtle shadow, border
- **Таблицы:** zebra striping, sticky header, hover highlight
- **Анимации:** минимальные, только для переходов и loading states

## Взаимодействие с API

```typescript
// api/client.ts
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// api/bonds.ts
export const getBonds = (params: BondFilterParams) =>
  api.get<BondListResponse>('/api/v1/bonds', { params })

export const getBond = (secid: string) =>
  api.get<BondResponse>(`/api/v1/bonds/${secid}`)

export const getMarketOverview = () =>
  api.get<MarketOverview>('/api/v1/stats/market-overview')
```

## Фильтры через URL

Фильтры хранятся в URL search params. Это позволяет:
- Делиться ссылкой с настроенными фильтрами
- Работать кнопка "Назад" в браузере
- Bookmarking конкретных настроек

```
/screener?yield_min=10&days_max=365&type=corp&sort=yield_at_prev_wa_price&order=desc
```
