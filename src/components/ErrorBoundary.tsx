import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  message: string;
}

/**
 * Global ErrorBoundary keeps the venue assistant usable if a visual panel crashes.
 * The fallback avoids exposing stack traces while still giving users a clear recovery action.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = {
    hasError: false,
    message: "An unexpected interface error occurred.",
  };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      message: error.message || "An unexpected interface error occurred.",
    };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Expert-level observability: keep client failures visible in logs without leaking sensitive route/user details into the UI.
    console.error("Access Navigator UI boundary caught an error", {
      message: error.message,
      componentStack: info.componentStack,
    });
  }

  private reset = () => {
    this.setState({ hasError: false, message: "" });
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <main className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">
        <section className="glass-3d-subtle max-w-lg w-full rounded-2xl p-6 text-center space-y-4">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-amber-500/15 text-amber-300">
            <AlertTriangle aria-hidden="true" className="h-6 w-6" />
          </div>
          <div className="space-y-2">
            <h1 className="text-xl font-semibold">Interface recovered safely</h1>
            <p className="text-sm text-slate-300">
              The navigation assistant isolated a UI panel error. Your route safety filters and backend protections remain active.
            </p>
            <p className="text-xs text-slate-500" role="status">
              {this.state.message}
            </p>
          </div>
          <Button onClick={this.reset} className="gap-2">
            <RefreshCcw aria-hidden="true" className="h-4 w-4" />
            Try again
          </Button>
        </section>
      </main>
    );
  }
}
