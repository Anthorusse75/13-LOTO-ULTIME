# 04 — Architecture Frontend

> **Projet** : LOTO ULTIME  
> **Version** : 1.0  
> **Date** : 2026-03-27  
> **Références croisées** : [02_Architecture_Globale](02_Architecture_Globale.md) · [06_API_Design](06_API_Design.md) · [13_Architecture_UI_UX](13_Architecture_UI_UX.md) · [12_Securite](12_Securite_et_Authentification.md)

---

## 1. Rôle du Frontend

Le frontend est un **client SPA (Single Page Application)** qui consomme l'API REST du backend. Il est responsable de :

| Responsabilité | Détail |
|---|---|
| Affichage des données | Tirages, statistiques, grilles |
| Visualisation | Graphiques interactifs, tableaux |
| Navigation | Routing côté client |
| Interaction utilisateur | Filtres, configuration, déclenchement actions |
| Authentification | Login, gestion session JWT |
| Monitoring | Suivi jobs scheduler, état système |

**Le frontend ne contient AUCUNE logique métier**. Tous les calculs sont effectués côté backend.

---

## 2. Stack Technique

| Composant | Technologie | Version | Justification |
|---|---|---|---|
| Framework | **React** | 18+ | Écosystème mature, composants |
| Langage | **TypeScript** | 5+ | Typage statique, maintenabilité |
| Build | **Vite** | 5+ | Build rapide, HMR, ESM natif |
| UI Kit | **Shadcn/ui** | latest | Composants accessibles, personnalisables |
| Styling | **Tailwind CSS** | 3+ | Utility-first, dark mode natif |
| Graphiques | **Recharts** | 2+ | React-natif, responsive |
| Graphiques avancés | **D3.js** | 7+ | Visualisations custom (graphes) |
| State management | **Zustand** | 4+ | Léger, simple, TypeScript |
| Data fetching | **TanStack Query** | 5+ | Cache, invalidation, optimistic |
| HTTP client | **Axios** | 1+ | Interceptors, retry |
| Routing | **React Router** | 6+ | Standard React SPA |
| Formulaires | **React Hook Form** | 7+ | Performance, validation |
| Validation | **Zod** | 3+ | Schémas TypeScript-first |
| Icônes | **Lucide React** | latest | Cohérent avec Shadcn |
| Notifications | **Sonner** | latest | Toast moderne |

---

## 3. Architecture du Code

```
frontend/src/
├── main.tsx                    # Point d'entrée React
├── App.tsx                     # Layout principal + routing
│
├── components/                 # Composants réutilisables
│   ├── ui/                     # Shadcn/ui (auto-généré)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── table.tsx
│   │   ├── dialog.tsx
│   │   ├── chart.tsx
│   │   └── ...
│   │
│   ├── layout/                 # Structure de page
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── MainLayout.tsx
│   │   └── Footer.tsx
│   │
│   ├── draws/                  # Composants tirages
│   │   ├── DrawTable.tsx
│   │   ├── DrawBalls.tsx       # Affichage boules numérotées
│   │   └── DrawFilters.tsx
│   │
│   ├── statistics/             # Composants statistiques
│   │   ├── FrequencyChart.tsx
│   │   ├── GapChart.tsx
│   │   ├── CooccurrenceMatrix.tsx
│   │   ├── TemporalTrend.tsx
│   │   └── DistributionChart.tsx
│   │
│   ├── grids/                  # Composants grilles
│   │   ├── GridCard.tsx
│   │   ├── GridScoreBreakdown.tsx
│   │   ├── TopGridsList.tsx
│   │   └── GridGenerator.tsx
│   │
│   ├── portfolio/              # Composants portefeuille
│   │   ├── PortfolioView.tsx
│   │   ├── CoverageMatrix.tsx
│   │   └── DiversityChart.tsx
│   │
│   ├── graph/                  # Composants graphes
│   │   ├── CooccurrenceGraph.tsx  # Visualisation D3
│   │   └── CommunityView.tsx
│   │
│   ├── jobs/                   # Composants scheduler
│   │   ├── JobList.tsx
│   │   ├── JobStatus.tsx
│   │   └── JobTrigger.tsx
│   │
│   └── common/                 # Composants partagés
│       ├── GameSelector.tsx
│       ├── LoadingSpinner.tsx
│       ├── ErrorBoundary.tsx
│       ├── Disclaimer.tsx      # Avertissement loterie
│       └── ProtectedRoute.tsx
│
├── pages/                      # Pages (une par route)
│   ├── DashboardPage.tsx
│   ├── DrawsPage.tsx
│   ├── StatisticsPage.tsx
│   ├── FrequenciesPage.tsx
│   ├── CooccurrencesPage.tsx
│   ├── TopGridsPage.tsx
│   ├── PortfoliosPage.tsx
│   ├── ScoringPage.tsx
│   ├── JobsPage.tsx
│   ├── ConfigPage.tsx
│   ├── AdminPage.tsx
│   ├── LoginPage.tsx
│   └── NotFoundPage.tsx
│
├── hooks/                      # Custom hooks
│   ├── useDraws.ts
│   ├── useStatistics.ts
│   ├── useGrids.ts
│   ├── usePortfolios.ts
│   ├── useJobs.ts
│   ├── useAuth.ts
│   ├── useGame.ts             # Jeu sélectionné courant
│   └── useTheme.ts
│
├── services/                   # Appels API
│   ├── api.ts                  # Instance Axios configurée
│   ├── authService.ts
│   ├── drawService.ts
│   ├── statisticsService.ts
│   ├── gridService.ts
│   ├── portfolioService.ts
│   ├── jobService.ts
│   └── gameService.ts
│
├── stores/                     # State management (Zustand)
│   ├── authStore.ts
│   ├── gameStore.ts           # Jeu sélectionné
│   └── settingsStore.ts       # Préférences UI
│
├── types/                      # Types TypeScript
│   ├── game.ts
│   ├── draw.ts
│   ├── statistics.ts
│   ├── grid.ts
│   ├── portfolio.ts
│   ├── job.ts
│   ├── user.ts
│   └── api.ts                 # Types génériques API
│
├── utils/                      # Utilitaires
│   ├── formatters.ts          # Formatage nombres, dates
│   ├── colors.ts              # Palette numéros
│   └── constants.ts
│
└── styles/
    └── globals.css            # Tailwind base + custom
```

---

## 4. Routing

```typescript
// App.tsx
const routes = [
  { path: "/login", element: <LoginPage />, public: true },
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { path: "/", element: <DashboardPage /> },
      { path: "/draws", element: <DrawsPage /> },
      { path: "/statistics", element: <StatisticsPage /> },
      { path: "/frequencies", element: <FrequenciesPage /> },
      { path: "/cooccurrences", element: <CooccurrencesPage /> },
      { path: "/top-grids", element: <TopGridsPage /> },
      { path: "/portfolios", element: <PortfoliosPage /> },
      { path: "/scoring", element: <ScoringPage /> },
      { path: "/jobs", element: <JobsPage />, roles: ["ADMIN"] },
      { path: "/config", element: <ConfigPage />, roles: ["ADMIN"] },
      { path: "/admin", element: <AdminPage />, roles: ["ADMIN"] },
    ],
  },
  { path: "*", element: <NotFoundPage /> },
];
```

### Accès par rôle

| Page | ADMIN | UTILISATEUR | CONSULTATION |
|---|:---:|:---:|:---:|
| Dashboard | ✅ | ✅ | ✅ |
| Tirages | ✅ | ✅ | ✅ |
| Statistiques | ✅ | ✅ | ✅ |
| Fréquences | ✅ | ✅ | ✅ |
| Cooccurrences | ✅ | ✅ | ✅ |
| Top Grilles | ✅ | ✅ | ❌ |
| Portefeuilles | ✅ | ✅ | ❌ |
| Scoring | ✅ | ✅ | ❌ |
| Jobs | ✅ | ❌ | ❌ |
| Configuration | ✅ | ❌ | ❌ |
| Administration | ✅ | ❌ | ❌ |

---

## 5. Data Fetching Pattern

### 5.1 Configuration Axios

```typescript
// services/api.ts
import axios from "axios";
import { useAuthStore } from "@/stores/authStore";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 5.2 Pattern TanStack Query

```typescript
// hooks/useDraws.ts
import { useQuery } from "@tanstack/react-query";
import { drawService } from "@/services/drawService";
import { useGameStore } from "@/stores/gameStore";

export function useDraws(page = 0, limit = 50) {
  const gameId = useGameStore((s) => s.currentGameId);

  return useQuery({
    queryKey: ["draws", gameId, page, limit],
    queryFn: () => drawService.getDraws(gameId, page, limit),
    enabled: !!gameId,
    staleTime: 5 * 60 * 1000, // 5 min
  });
}

export function useLatestDraw() {
  const gameId = useGameStore((s) => s.currentGameId);

  return useQuery({
    queryKey: ["draws", gameId, "latest"],
    queryFn: () => drawService.getLatest(gameId),
    enabled: !!gameId,
    refetchInterval: 60 * 1000, // Poll toutes les minutes
  });
}
```

---

## 6. State Management

### 6.1 Auth Store

```typescript
// stores/authStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AuthState {
  token: string | null;
  user: User | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
  hasRole: (role: string) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      login: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null }),
      isAuthenticated: () => !!get().token,
      hasRole: (role) => get().user?.role === role,
    }),
    { name: "auth-storage" }
  )
);
```

### 6.2 Game Store

```typescript
// stores/gameStore.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface GameState {
  currentGameId: number | null;
  currentGameSlug: string | null;
  setGame: (id: number, slug: string) => void;
}

export const useGameStore = create<GameState>()(
  persist(
    (set) => ({
      currentGameId: null,
      currentGameSlug: null,
      setGame: (id, slug) => set({ currentGameId: id, currentGameSlug: slug }),
    }),
    { name: "game-storage" }
  )
);
```

---

## 7. Composants Clés

### 7.1 Dashboard

Le dashboard affiche une vue synthétique :

```
┌──────────────────────────────────────────────────────────┐
│  LOTO ULTIME                    [Loto ▾]  [user] [🌙]  │
├──────────┬───────────────────────────────────────────────┤
│          │                                               │
│ Dashboard│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│ Tirages  │  │ Dernier │ │ Total   │ │ Dernière│        │
│ Stats    │  │ Tirage  │ │ Tirages │ │ MAJ     │        │
│ Freq.    │  └─────────┘ └─────────┘ └─────────┘        │
│ Cooccur. │                                               │
│ Top 10   │  ┌────────────────────┐ ┌──────────────────┐ │
│ Portef.  │  │                    │ │                  │ │
│ Scoring  │  │ Fréquences (chart) │ │ Top 5 Grilles   │ │
│ ──────── │  │                    │ │                  │ │
│ Jobs     │  └────────────────────┘ └──────────────────┘ │
│ Config   │                                               │
│ Admin    │  ┌────────────────────┐ ┌──────────────────┐ │
│          │  │                    │ │                  │ │
│          │  │ Gaps (chart)       │ │ Jobs Status      │ │
│          │  │                    │ │                  │ │
│          │  └────────────────────┘ └──────────────────┘ │
└──────────┴───────────────────────────────────────────────┘
```

### 7.2 Affichage des boules

```typescript
// components/draws/DrawBalls.tsx
interface DrawBallsProps {
  numbers: number[];
  stars?: number[];
  starName?: string;
}

function DrawBalls({ numbers, stars, starName }: DrawBallsProps) {
  return (
    <div className="flex gap-2 items-center">
      {numbers.map((n) => (
        <div
          key={n}
          className="w-10 h-10 rounded-full bg-blue-600 text-white 
                     flex items-center justify-center font-bold text-sm"
        >
          {n}
        </div>
      ))}
      {stars?.map((s) => (
        <div
          key={`star-${s}`}
          className="w-10 h-10 rounded-full bg-yellow-500 text-black 
                     flex items-center justify-center font-bold text-sm"
        >
          {s}
        </div>
      ))}
    </div>
  );
}
```

---

## 8. Thème et Dark Mode

### 8.1 Configuration Tailwind

```typescript
// tailwind.config.ts
export default {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Palette personnalisée
        primary: { /* blue shades */ },
        accent: { /* yellow/gold for stars */ },
        surface: {
          DEFAULT: "#0f172a",   // dark background
          card: "#1e293b",      // card background
          hover: "#334155",     // hover state
        },
      },
    },
  },
};
```

Le dark mode est le **mode par défaut**. Un toggle permet de basculer en mode clair.

---

## 9. Graphiques

### 9.1 Recharts — Graphiques standards

Utilisé pour : fréquences bar chart, gaps line chart, distributions, tendances temporelles.

```typescript
// components/statistics/FrequencyChart.tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function FrequencyChart({ data }: { data: FrequencyData[] }) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data}>
        <XAxis dataKey="number" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="frequency" fill="#3b82f6" />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

### 9.2 D3.js — Visualisations avancées

Utilisé pour : graphe de cooccurrence (force-directed), heatmaps, visualisations réseau.

---

## 10. Build et Déploiement

### 10.1 Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext ts,tsx",
    "format": "prettier --write src"
  }
}
```

### 10.2 Variables d'environnement

```
# .env.local
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=LOTO ULTIME
```

---

## 11. Références

| Document | Contenu |
|---|---|
| [02_Architecture_Globale](02_Architecture_Globale.md) | Stack complète |
| [06_API_Design](06_API_Design.md) | Endpoints consommés |
| [12_Securite_et_Authentification](12_Securite_et_Authentification.md) | JWT côté client |
| [13_Architecture_UI_UX](13_Architecture_UI_UX.md) | Design détaillé, wireframes |

---

*Fin du document 04_Architecture_Frontend.md*
