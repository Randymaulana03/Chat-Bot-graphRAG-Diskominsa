import { User } from "lucide-react";
import ReactMarkdown from "react-markdown";
import SourceList from "./SourceList";

function ChatMessage({ role, content, sources = [] }) {
  const isUser = role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <img
          src="/Coat_of_arms_of_Aceh.svg"
          alt="Logo Aceh"
          className="h-8 w-auto shrink-0 object-contain"
        />
      )}

      <div
        className={`max-w-2xl rounded-2xl px-4 py-3 text-sm leading-relaxed ${isUser
          ? "rounded-br-md bg-slate-900 text-white"
          : "rounded-bl-md border border-slate-200 bg-white text-slate-800 shadow-sm"
          }`}
      >
        <div
          className={
            isUser
              ? ""
              : "prose prose-slate max-w-none text-sm [&>p]:mb-3 [&>p:last-child]:mb-0 [&>ul]:list-disc [&>ul]:pl-5 [&>ul]:mb-4 [&>ol]:list-decimal [&>ol]:pl-5 [&>ol]:mb-4"
          }
        >
          <ReactMarkdown
            components={{
              // Netralkan tag <strong> / **bold** menjadi teks biasa (normal weight)
              strong: ({ ...props }) => (
                <span className="font-normal text-slate-800" {...props} />
              ),
              // Hilangkan garis mendatar kasar (<hr>) jika ada
              hr: () => <div className="my-3 border-t border-slate-100" />,
            }}
          >
            {content}
          </ReactMarkdown>
        </div>

        {!isUser && <SourceList sources={sources} />}
      </div>

      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-700 shadow-sm">
          <User size={18} />
        </div>
      )}
    </div>
  );
}

export default ChatMessage;