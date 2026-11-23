import { FileText } from "lucide-react";

function SourceList({ sources = [] }) {
  if (!sources || sources.length === 0) return null;

  // Kelompokkan sumber berdasarkan pertanyaan
  const groupedSources = sources.reduce((groups, source) => {
    const question = source.question || "Sumber Regulasi";
    if (!groups[question]) groups[question] = [];
    groups[question].push(source);
    return groups;
  }, {});

  return (
    <div className="mt-3 border-t border-slate-100 pt-3">
      <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-slate-500">
        <FileText size={14} />
        <span>Sumber Regulasi</span>
      </div>

      <div className="space-y-3">
        {Object.entries(groupedSources).map(([question, itemSources]) => {
          // Batasi maksimal 2 sumber yang ditampilkan secara visual
          const visibleSources = itemSources.slice(0, 2);
          const hiddenCount = itemSources.length - visibleSources.length;
          
          // Hitung total akumulasi extra dari API + sisa array lokal
          const totalExtra = visibleSources.reduce(
            (acc, curr) => acc + (curr.more_count || 0), 
            0
          ) + hiddenCount;

          return (
            <div key={question} className="text-xs">
              <p className="mb-1.5 font-medium text-slate-600">{question}</p>

              <div className="flex flex-wrap items-center gap-2">
                {visibleSources.map((source, idx) => (
                  <div
                    key={idx}
                    className="rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1.5 text-slate-700 font-mono text-[11px]"
                  >
                    <span className="font-semibold">{source.regulation}</span>
                    {source.pasal && <span className="ml-1">· {source.pasal}</span>}
                    {source.ayat && <span className="ml-1">· Ayat {source.ayat.replace(/[()]/g, "")}</span>}
                    {source.page && <span className="ml-1">· Hal. {source.page}</span>}
                  </div>
                ))}

                {totalExtra > 0 && (
                  <span className="inline-flex items-center rounded-lg border border-blue-200 bg-blue-50 px-2.5 py-1.5 text-[11px] font-bold text-blue-600">
                    +{totalExtra}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default SourceList;