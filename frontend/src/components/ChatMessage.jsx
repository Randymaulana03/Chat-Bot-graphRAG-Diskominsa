import { Bot, User } from "lucide-react"
import SourceList from "./SourceList"

function ChatMessage({ role, content, sources = [] }) {
  const isUser = role === "user"

  return (
    <div
      className={`flex gap-3 ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-900 text-white">
          <Bot size={17} />
        </div>
      )}

      <div
        className={`max-w-2xl rounded-2xl px-4 py-3 text-sm leading-6 ${
          isUser
            ? "rounded-br-md bg-slate-900 text-white"
            : "rounded-bl-md border border-slate-200 bg-white text-slate-700 shadow-sm"
        }`}
      >
        <div>{content}</div>

        {!isUser && <SourceList sources={sources} />}
      </div>

      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600">
          <User size={17} />
        </div>
      )}
    </div>
  )
}

export default ChatMessage