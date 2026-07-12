// API Configuration
export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const API_ENDPOINTS = {
  health: `${API_BASE}/api/health`,
  stadiums: `${API_BASE}/api/stadiums`,
  zones: (stadiumId: string) => `${API_BASE}/api/zones?stadium_id=${stadiumId}`,
  zone: (stadiumId: string, zoneId: string) => `${API_BASE}/api/zones/${zoneId}?stadium_id=${stadiumId}`,
  graph: (stadiumId: string) => `${API_BASE}/api/graph?stadium_id=${stadiumId}`,
  coordinates: (stadiumId: string) => `${API_BASE}/api/coordinates?stadium_id=${stadiumId}`,
  route: `${API_BASE}/api/route`,
  routeSimple: `${API_BASE}/api/route/simple`,
  caption: `${API_BASE}/api/caption`,
  captionQuick: `${API_BASE}/api/caption/quick`,
  chat: `${API_BASE}/api/chat`,
  chatStream: `${API_BASE}/api/chat/stream`,
  predictions: (stadiumId: string) => `${API_BASE}/api/predictions/${stadiumId}`,
  analytics: (stadiumId: string) => `${API_BASE}/api/analytics/${stadiumId}`,
  dataUpload: (stadiumId: string) => `${API_BASE}/api/data/upload?stadium_id=${stadiumId}`,
  demoScenario: `${API_BASE}/api/demo/scenario`,
  announcements: `${API_BASE}/api/announcements`,
  batchUpdate: `${API_BASE}/api/zones/batch-update`,
} as const;

export const DEFAULT_STADIUM = "metlife";
export const REFRESH_INTERVAL = 5000;
