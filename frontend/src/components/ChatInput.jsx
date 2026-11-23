import { ArrowUp } from "lucide-react";

function ChatInput({ value, onChange, onSubmit, disabled }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim() && !disabled) onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative flex items-center rounded-2xl border border-slate-200 bg-white p-2 shadow-sm transition-all focus-within:border-slate-400 focus-within:shadow-md">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Tanyakan Tupoksi AI Diskominsa..."
          disabled={disabled}
          className="w-full bg-transparent px-3 py-2 text-sm text-slate-900 outline-none placeholder:text-slate-400 disabled:opacity-50"
        />

        <button
          type="submit"
          disabled={!value.trim() || disabled}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white transition-all hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
        >
          <ArrowUp size={18} />
        </button>
      </div>
      <p className="mt-2 text-center text-[11px] text-slate-400">
        Respon dihasilkan berdasarkan basis data Regulasi Gubernur Aceh.
      </p>
    </form>
  );
}

export default ChatInput;