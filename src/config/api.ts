/**
 * API Configuration
 * =================
 * Centralized API endpoint definitions and configuration constants.
 * All frontend network requests use these endpoints to communicate
 * with the FastAPI backend.
 *
 * Environment Variable:
 *   VITE_API_URL — Override the default backend URL (default: http://localhost:8000)
 */

/** 
 * Base URL for all API requests. Falls back to localhost for development.
 * Note: Render free tier sleeps after 15 mins of inactivity. 
 * The first request after sleep can take 30-60s. This is expected behavior.
 * A keep-alive cron job (hitting /api/health) is used to minimize this.
 */
export const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * API endpoint definitions.
 * Static endpoints are strings; dynamic endpoints are functions
 * that accept parameters and return the full URL.
 */
export const API_ENDPOINTS = {
  /** Health check — returns feature flags, uptime, and LLM provider status */
  health: `${API_BASE}/api/health`,

  /** List all available stadiums */
  stadiums: `${API_BASE}/api/stadiums`,

  /** Get all zones for a stadium */
  zones: (stadiumId: string) => `${API_BASE}/api/zones?stadium_id=${stadiumId}`,

  /** Get a specific zone's details */
  zone: (stadiumId: string, zoneId: string) =>
    `${API_BASE}/api/zones/${zoneId}?stadium_id=${stadiumId}`,

  /** Get the stadium connectivity graph (adjacency list) */
  graph: (stadiumId: string) => `${API_BASE}/api/graph?stadium_id=${stadiumId}`,

  /** Get zone coordinates for the SVG map visualization */
  coordinates: (stadiumId: string) =>
    `${API_BASE}/api/coordinates?stadium_id=${stadiumId}`,

  /** Multi-agent AI route calculation (POST) */
  route: `${API_BASE}/api/route`,

  /** Simplified route lookup (POST, query-param based) */
  routeSimple: `${API_BASE}/api/route/simple`,

  /** Process a stadium announcement into an accessible caption (POST) */
  caption: `${API_BASE}/api/caption`,

  /** Quick caption endpoint (POST, query-param based) */
  captionQuick: `${API_BASE}/api/caption/quick`,

  /** Conversational AI chat (POST) */
  chat: `${API_BASE}/api/chat`,

  /** Streaming conversational AI via SSE (POST) */
  chatStream: `${API_BASE}/api/chat/stream`,

  /** AI crowd density predictions for a stadium */
  predictions: (stadiumId: string) =>
    `${API_BASE}/api/predictions/${stadiumId}`,

  /** Comprehensive stadium analytics with AI insights */
  analytics: (stadiumId: string) =>
    `${API_BASE}/api/analytics/${stadiumId}`,

  /** Upload zone data via CSV/JSON (POST) */
  dataUpload: (stadiumId: string) =>
    `${API_BASE}/api/data/upload?stadium_id=${stadiumId}`,

  /** Trigger demo scenarios for presentation (POST) */
  demoScenario: `${API_BASE}/api/demo/scenario`,

  /** Get recent announcement history */
  announcements: `${API_BASE}/api/announcements`,

  /** Batch update multiple zone statuses (POST) */
  batchUpdate: `${API_BASE}/api/zones/batch-update`,
} as const;

/** Default stadium ID used on first load */
export const DEFAULT_STADIUM = "metlife";

/** How often (ms) zone data is auto-refreshed from the backend */
export const REFRESH_INTERVAL = 5000;
