import { useState, useEffect, useCallback } from "react";
import { Toaster } from "@/components/ui/sonner";
import { Header } from "@/components/Header";
import { Sidebar, type Page } from "@/components/Sidebar";
import { Dashboard } from "@/pages/Dashboard";
import { ChatPage } from "@/pages/ChatPage";
import { AnalyticsPage } from "@/pages/AnalyticsPage";
import { API_ENDPOINTS, DEFAULT_STADIUM } from "@/config/api";
import { toast } from "sonner";

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");
  const [stadiumId, setStadiumId] = useState(DEFAULT_STADIUM);
  const [connected, setConnected] = useState(false);
  const [stadiumName, setStadiumName] = useState("MetLife Stadium");

  // Health check
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(API_ENDPOINTS.health, { signal: AbortSignal.timeout(5000) });
        if (res.ok) {
          setConnected(true);
          const data = await res.json();
          if (data.features) {
            const enabled = Object.entries(data.features)
              .filter(([, v]) => v)
              .map(([k]) => k);
            if (enabled.length > 0) {
              // toast.success(`Features: ${enabled.join(", ")}`);
            }
          }
        } else {
          setConnected(false);
        }
      } catch {
        setConnected(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  // Update stadium name when stadium changes
  useEffect(() => {
    const names: Record<string, string> = {
      metlife: "MetLife Stadium",
      sofi: "SoFi Stadium",
      azteca: "Estadio Azteca",
    };
    setStadiumName(names[stadiumId] || stadiumId);
  }, [stadiumId]);

  const handleStadiumChange = useCallback((id: string) => {
    setStadiumId(id);
    toast.info(`Switched to ${id}`);
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard stadiumId={stadiumId} />;
      case "chat":
        return <ChatPage stadiumId={stadiumId} />;
      case "analytics":
        return <AnalyticsPage stadiumId={stadiumId} />;
      default:
        return <Dashboard stadiumId={stadiumId} />;
    }
  };

  return (
    <div
      className="min-h-screen text-white bg-mesh relative"
      data-stadium={stadiumId}
    >
      {/* Animated parallax orb layer (rendered as sibling so ::before/::after keep working) */}
      <div className="bg-orb" aria-hidden />

      <Header
        connected={connected}
        stadiumName={stadiumName}
        onMenuClick={() => setSidebarOpen(!sidebarOpen)}
        sidebarOpen={sidebarOpen}
        stadiumId={stadiumId}
      />

      <Sidebar
        open={sidebarOpen}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        stadiumId={stadiumId}
        onStadiumChange={handleStadiumChange}
      />

      <main
        className={`relative z-10 transition-all duration-300 ${
          sidebarOpen ? "ml-64" : "ml-0"
        }`}
      >
        {renderPage()}
      </main>

      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "rgba(8, 12, 28, 0.75)",
            backdropFilter: "blur(24px) saturate(180%)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            borderTopColor: "rgba(255, 255, 255, 0.25)",
            color: "#e2e8f0",
            boxShadow:
              "0 30px 60px -10px rgba(0,0,0,0.9), inset 0 1px 0 rgba(255,255,255,0.2)",
          },
        }}
      />
    </div>
  );
}
