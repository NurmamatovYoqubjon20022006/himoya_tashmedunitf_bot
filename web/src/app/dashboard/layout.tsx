import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";
import { Sidebar } from "@/components/sidebar";
import { TopBar } from "@/components/top-bar";
import { NewReportNotifier } from "@/components/new-report-notifier";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();
  if (!session) redirect("/login");

  return (
    <div className="lg:flex min-h-screen bg-white dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 min-w-0 flex flex-col">
        <TopBar />
        <main className="flex-1 bg-gray-50/30 dark:bg-gray-950">
          <div className="px-4 py-5 sm:px-6 sm:py-6 lg:px-8 lg:py-8 max-w-[1400px] mx-auto">
            {children}
          </div>
        </main>
      </div>
      <NewReportNotifier />
    </div>
  );
}
