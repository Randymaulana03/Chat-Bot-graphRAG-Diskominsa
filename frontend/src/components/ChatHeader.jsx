import { Menu } from "lucide-react";

function ChatHeader({ onToggleSidebar, onNewChat }) {
  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3 sm:px-6">
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
            aria-label="Toggle Sidebar"
          >
            <Menu size={20} />
          </button>

          {/* Area Logo + Judul dapat diklik untuk obrolan baru */}
          <button
            onClick={onNewChat}
            className="flex cursor-pointer items-center gap-3 text-left focus:outline-none"
          >
            <img
              src="/Coat_of_arms_of_Aceh.svg"
              alt="Logo Aceh"
              className="h-9 w-auto object-contain"
            />

            <div>
              <h1 className="text-sm font-bold text-slate-900">TUPOKSI AI</h1>
              <p className="text-[11px] text-slate-500">
                Asisten Regulasi & Tata Kerja
              </p>
            </div>
          </button>
        </div>

        <div className="flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          Online
        </div>
      </div>
    </header>
  );
}

export default ChatHeader;