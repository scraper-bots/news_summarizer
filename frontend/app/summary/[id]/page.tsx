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
      {/* Hero Header */}
      <div className="relative bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-grid-white/10 [mask-image:linear-gradient(0deg,transparent,black)]"></div>

        <div className="container mx-auto px-4 py-8 md:py-12 relative">
          {/* Back Button */}
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-white/90 hover:text-white transition-colors mb-6 group"
          >
            <svg className="w-5 h-5 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span className="font-medium">Ana Səhifə</span>
          </Link>

          {/* Title Section */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div className="flex items-start gap-4">
              <div className="w-20 h-20 md:w-24 md:h-24 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center text-white font-bold text-3xl md:text-4xl flex-shrink-0 border border-white/30 shadow-xl">
                {new Date(summary.scraping_date).getDate()}
              </div>
              <div>
                <h1 className="text-3xl md:text-5xl font-bold text-white mb-2">
                  {formatDateVerbose(summary.scraping_date)}
                </h1>
                <p className="text-blue-100 text-lg">📊 Gündəlik Bank Sektoru Analizi</p>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="flex gap-3 md:gap-4">
              <div className="bg-white/10 backdrop-blur-sm px-4 py-3 rounded-xl border border-white/20">
                <p className="text-white/80 text-xs mb-1">Xəbərlər</p>
                <p className="text-white text-2xl font-bold">{summary.new_articles_count}</p>
              </div>
              <div className="bg-white/10 backdrop-blur-sm px-4 py-3 rounded-xl border border-white/20">
                <p className="text-white/80 text-xs mb-1">Mənbələr</p>
                <p className="text-white text-2xl font-bold">{summary.sources_count}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 md:py-12">
        {/* Enhanced Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-8 md:mb-12">
          <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 p-6 border border-blue-100 group">
            <div className="flex items-center justify-between mb-3">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
            </div>
            <p className="text-slate-500 text-sm font-medium mb-2">Yeni Xəbərlər</p>
            <p className="text-3xl font-bold text-slate-900">{summary.new_articles_count}</p>
          </div>

          <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 p-6 border border-indigo-100 group">
            <div className="flex items-center justify-between mb-3">
              <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <p className="text-slate-500 text-sm font-medium mb-2">Ümumi Xəbərlər</p>
            <p className="text-3xl font-bold text-slate-900">{summary.articles_count}</p>
          </div>

          <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 p-6 border border-purple-100 group">
            <div className="flex items-center justify-between mb-3">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
            </div>
            <p className="text-slate-500 text-sm font-medium mb-2">Mənbələr</p>
            <p className="text-3xl font-bold text-slate-900">{summary.sources_count}</p>
          </div>

          <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 p-6 border border-green-100 group">
            <div className="flex items-center justify-between mb-3">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <p className="text-slate-500 text-sm font-medium mb-2">İcra Müddəti</p>
            <p className="text-3xl font-bold text-slate-900">{formatDuration(summary.scraping_duration_seconds)}</p>
          </div>
        </div>

        {/* AI Summary with Enhanced Design */}
        {summary.summary && (
          <div className="bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-xl p-6 md:p-10 mb-8 md:mb-12 border border-blue-200 relative overflow-hidden">
            {/* Decorative Elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-400/10 to-indigo-400/10 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-purple-400/10 to-pink-400/10 rounded-full blur-3xl"></div>

            <div className="relative">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 md:mb-8">
                <div className="flex items-center gap-4 mb-4 md:mb-0">
                  <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-2xl md:text-3xl font-bold text-slate-900">AI Analitik Hesabat</h2>
                    <p className="text-slate-600 text-sm mt-1">Süni intellekt tərəfindən yaradılmış xülasə</p>
                  </div>
                </div>
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full border border-blue-200 shadow-sm">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-slate-700">AI Generasiya</span>
                </div>
              </div>

              <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 md:p-8 border border-white/60 shadow-inner">
                <div className="text-slate-800 whitespace-pre-wrap leading-relaxed text-sm md:text-base font-medium">
                  {summary.summary}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Articles Section */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 md:mb-8 gap-4">
            <div>
              <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-2">
                Xəbərlər Kolleksiyası
              </h2>
              <p className="text-slate-600">
                Toplam <span className="font-semibold text-blue-600">{articles.length}</span> xəbər
              </p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-white rounded-full border border-slate-200 shadow-sm">
              <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
              <span className="text-sm font-medium text-slate-700">Kart Görünüşü</span>
            </div>
          </div>
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
