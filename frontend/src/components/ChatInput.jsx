import { ArrowUp } from "lucide-react"

function ChatInput({ value, onChange, onSubmit, disabled = false }) {
  const handleSubmit = (event) => {
    event.preventDefault()

    if (!value.trim() || disabled) {
      return
    }

    onSubmit()
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm transition focus-within:border-slate-300 focus-within:shadow-md">
        <input
          type="text"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Tulis pertanyaan..."
          disabled={disabled}
          className="flex-1 bg-transparent px-3 py-3 text-sm text-slate-900 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed disabled:opacity-60"
        />

        <button
          type="submit"
          disabled={!value.trim() || disabled}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          aria-label="Kirim pertanyaan"
        >
          <ArrowUp size={18} />
        </button>
      </div>

      <p className="mt-2 text-center text-xs text-slate-400">
        Jawaban berdasarkan basis pengetahuan Diskominsa Aceh.
      </p>
    </form>
  )
}

export default ChatInput
