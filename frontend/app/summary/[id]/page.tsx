import Link from 'next/link';
import { getSummaryById, getArticlesBySessionId } from '@/lib/db';
import { formatDateVerbose, formatDuration } from '@/lib/utils';
import { notFound } from 'next/navigation';
import ArticlesGrid from '@/components/ArticlesGrid';

export const dynamic = 'force-dynamic';

export default async function SummaryPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const summaryId = parseInt(id);

  if (isNaN(summaryId)) {
    notFound();
  }

  const summary = await getSummaryById(summaryId);
  const articles = await getArticlesBySessionId(summaryId);

  if (!summary) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200">
        <div className="container mx-auto px-4 py-6">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-slate-600 hover:text-blue-600 transition-colors mb-4"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Geri
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-2xl flex-shrink-0">
              {new Date(summary.scraping_date).getDate()}
            </div>
            <div>
              <h1 className="text-2xl md:text-4xl font-bold text-slate-900">
                {formatDateVerbose(summary.scraping_date)}
              </h1>
              <p className="text-slate-600 mt-1">Bank Sektoru Xülasəsi</p>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-4 border border-slate-200">
            <p className="text-slate-500 text-xs font-medium mb-1">Yeni Xəbərlər</p>
            <p className="text-2xl font-bold text-blue-600">{summary.new_articles_count}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 border border-slate-200">
            <p className="text-slate-500 text-xs font-medium mb-1">Ümumi Xəbərlər</p>
            <p className="text-2xl font-bold text-indigo-600">{summary.articles_count}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 border border-slate-200">
            <p className="text-slate-500 text-xs font-medium mb-1">Mənbələr</p>
            <p className="text-2xl font-bold text-purple-600">{summary.sources_count}</p>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 border border-slate-200">
            <p className="text-slate-500 text-xs font-medium mb-1">Müddət</p>
            <p className="text-2xl font-bold text-green-600">
              {formatDuration(summary.scraping_duration_seconds)}
            </p>
          </div>
        </div>

        {/* AI Summary */}
        {summary.summary && (
          <div className="bg-white rounded-xl shadow-sm p-6 md:p-8 mb-8 border border-slate-200">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-slate-900">Banking Intelligence Report</h2>
            </div>
            <div className="prose prose-slate max-w-none">
              <div className="text-slate-700 whitespace-pre-wrap leading-relaxed text-sm md:text-base">
                {summary.summary}
              </div>
            </div>
          </div>
        )}

        {/* Articles Grid with Pagination */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-6">
            Xəbərlər ({articles.length})
          </h2>
          <ArticlesGrid articles={articles} />
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white/80 backdrop-blur-sm border-t border-slate-200 mt-16">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-slate-500 text-sm">
            Azərbaycan Bank Sektoru Xəbərləri © {new Date().getFullYear()}
          </p>
        </div>
      </footer>
    </div>
  );
}
