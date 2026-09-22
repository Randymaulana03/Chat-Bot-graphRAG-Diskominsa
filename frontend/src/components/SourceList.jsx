import { FileText } from "lucide-react"

function SourceList({ sources = [] }) {
  if (sources.length === 0) {
    return null
  }

  return (
    <div className="mt-3 border-t border-slate-100 pt-3">
      <div className="mb-2 flex items-center gap-1.5 text-xs font-medium text-slate-500">
        <FileText size={14} />
        <span>Sumber</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {sources.map((source, index) => (
          <div
            key={index}
            className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600"
          >
            <span className="font-medium text-slate-700">
              {source.regulation}
            </span>

            {source.pasal && (
              <>
                <span className="mx-1 text-slate-300">·</span>
                <span>{source.pasal}</span>
              </>
            )}

            {source.ayat && (
              <>
                <span className="mx-1 text-slate-300">·</span>
                <span>Ayat {source.ayat.replace(/[()]/g, "")}</span>
              </>
            )}

            {source.page && (
              <>
                <span className="mx-1 text-slate-300">·</span>
                <span>Halaman {source.page}</span>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default SourceList