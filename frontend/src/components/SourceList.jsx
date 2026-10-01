import { FileText } from "lucide-react"

function SourceList({ sources = [] }) {
  if (sources.length === 0) {
    return null
  }

  const groupedSources = sources.reduce((groups, source) => {
    const question = source.question || "Sumber"

    if (!groups[question]) {
      groups[question] = []
    }

    groups[question].push(source)

    return groups
  }, {})

  return (
    <div className="mt-3 border-t border-slate-100 pt-3">
      <div className="mb-3 flex items-center gap-1.5 text-xs font-medium text-slate-500">
        <FileText size={14} />
        <span>Sumber</span>
      </div>

      <div className="space-y-3">
        {Object.entries(groupedSources).map(
          ([question, questionSources]) => (
            <div key={question}>
              <p className="mb-1.5 text-xs font-medium text-slate-600">
                {question}
              </p>

              <div className="flex flex-wrap gap-2 items-center">
                {questionSources.map((source, index) => (
                  <div key={index} className="flex items-center gap-1.5">
                    {/* Chip Utama Sumber */}
                    <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600">
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
                          <span>
                            Ayat {source.ayat.replace(/[()]/g, "")}
                          </span>
                        </>
                      )}

                      {source.page && (
                        <>
                          <span className="mx-1 text-slate-300">·</span>
                          <span>Halaman {source.page}</span>
                        </>
                      )}
                    </div>

                    {/* Badge +N di luar chip sumber */}
                    {source.more_count > 0 && (
                      <span className="inline-flex items-center justify-center rounded-lg bg-blue-50 px-2.5 py-2 text-xs font-bold text-blue-600 border border-blue-200 shadow-sm">
                        +{source.more_count}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )
        )}
      </div>
    </div>
  )
}

export default SourceList