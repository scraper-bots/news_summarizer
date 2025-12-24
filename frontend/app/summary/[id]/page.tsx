import Link from 'next/link';
import { getSummaryById, getArticlesBySessionId } from '@/lib/db';
import { formatDate, formatDateTime, formatDuration } from '@/lib/utils';
import { notFound } from 'next/navigation';

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
                {formatDate(summary.scraping_date)}
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

        {/* Articles */}
        {articles.length > 0 && (
          <div className="bg-white rounded-xl shadow-sm p-6 md:p-8 border border-slate-200">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">
              Xəbərlər ({articles.length})
            </h2>
            <div className="space-y-4">
              {articles.map((article) => (
                <div
                  key={article.id}
                  className="border-l-4 border-blue-500 bg-slate-50 rounded-r-lg p-4 hover:bg-slate-100 transition-colors"
                >
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-2 mb-2">
                    <h3 className="font-semibold text-slate-900 text-sm md:text-base">
                      {article.title}
                    </h3>
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium w-fit">
                      {article.source}
                    </span>
                  </div>
                  <p className="text-slate-600 text-sm line-clamp-2 mb-3">
                    {article.content.substring(0, 200)}...
                  </p>
                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {formatDateTime(article.published_date)}
                    </span>
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-blue-600 hover:text-blue-700 hover:underline"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                      Əsl xəbər
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
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
