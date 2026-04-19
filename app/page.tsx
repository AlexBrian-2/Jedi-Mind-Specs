import dynamic from 'next/dynamic';

// Disable SSR for the orchestrator dashboard since it uses zustand store
// which can cause hydration issues with SSR
const OrchestratorDashboard = dynamic(
  () => import('@/components/orchestrator/orchestrator-dashboard').then(mod => mod.OrchestratorDashboard),
  { 
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground">Loading orchestrator...</p>
        </div>
      </div>
    )
  }
);

export default function Home() {
  return <OrchestratorDashboard />;
}
