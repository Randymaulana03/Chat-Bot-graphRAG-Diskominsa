import { Bot } from "lucide-react"

function ChatHeader() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center gap-3 px-6 py-4">
        {/* Logo */}
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
          <Bot size={22} />
        </div>

        {/* Identity */}
        <div>
          <h1 className="text-sm font-semibold text-slate-900">
            Diskominsa Aceh
          </h1>

          <p className="text-xs text-slate-500">
            Asisten Informasi Diskominsa Aceh
          </p>
        </div>

        {/* Status */}
        <div className="ml-auto flex items-center gap-2 text-xs text-slate-500">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          Online
        </div>
      </div>
    </header>
  )
}

export default ChatHeader