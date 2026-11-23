
function ThinkingIndicator() {
  return (
    <div className="flex gap-3 justify-start animate-in fade-in duration-200">
      <img
        src="/Coat_of_arms_of_Aceh.svg"
        alt="Logo Aceh"
        className="h-8 w-auto shrink-0 object-contain"
      />

      <div className="rounded-2xl rounded-bl-md border border-slate-200 bg-white px-4 py-3 shadow-sm flex items-center gap-2">
        <span className="text-xs font-medium text-slate-500">
          Sedang berpikir
        </span>
        <div className="flex items-center gap-1">
          <span className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.32s]" />
          <span className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.16s]" />
          <span className="h-1.5 w-1.5 rounded-full bg-slate-400 animate-bounce" />
        </div>
      </div>
    </div>
  );
}

export default ThinkingIndicator;