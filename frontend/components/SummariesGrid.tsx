'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { ScrapingSummary } from '@/types';
import { getPlaceholderImage, truncateText, getShortMonth } from '@/lib/utils';
import Pagination from './Pagination';

interface SummariesGridProps {
  summaries: ScrapingSummary[];
}

const ITEMS_PER_PAGE = 9;

export default function SummariesGrid({ summaries }: SummariesGridProps) {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(summaries.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const currentSummaries = summaries.slice(startIndex, endIndex);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (summaries.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-12 text-center border border-slate-200">
        <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-slate-900 mb-2">Hələ heç bir xülasə yoxdur</h3>
        <p className="text-slate-500">İlk xülasə yaradıldıqdan sonra burada görünəcək.</p>
      </div>
    );
  }

  return (
    <div>
      {/* Summaries Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {currentSummaries.map((summary, index) => (
          <Link
            key={summary.id}
            href={`/summary/${summary.id}`}
            className="group"
          >
            <div className="bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-slate-200 hover:border-blue-300 flex flex-col h-full">
              {/* Image Header */}
              <div className="relative h-48 bg-gradient-to-br from-blue-50 to-indigo-100 overflow-hidden">
                <Image
                  src={getPlaceholderImage(startIndex + index)}
                  alt="Gündəlik Bank Xülasəsi"
                  fill
                  className="object-cover group-hover:scale-105 transition-transform duration-300"
                />
                {/* Date Badge */}
                <div className="absolute top-4 left-4 w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex flex-col items-center justify-center text-white shadow-lg">
                  <span className="text-2xl font-bold leading-none">
                    {new Date(summary.scraping_date).getDate()}
                  </span>
                  <span className="text-xs uppercase mt-1">
                    {getShortMonth(summary.scraping_date)}
                  </span>
                </div>
              </div>

              {/* Content */}
              <div className="p-5 flex flex-col flex-grow">
                {/* Title */}
                <h3 className="text-xl font-bold text-slate-900 mb-3 group-hover:text-blue-600 transition-colors">
                  Gündəlik Xülasə
                </h3>

                {/* Stats */}
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-medium flex items-center gap-1">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    {summary.new_articles_count} xəbər
                  </span>
                  <span className="text-xs bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full font-medium flex items-center gap-1">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                    </svg>
                    {summary.sources_count} mənbə
                  </span>
                </div>

                {/* Summary Preview */}
                {summary.summary && (
                  <div className="flex-grow">
                    <p className="text-slate-600 text-sm line-clamp-4 leading-relaxed">
                      {truncateText(summary.summary, 200)}
                    </p>
                  </div>
                )}

                {/* Footer */}
                <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-xs text-slate-500 font-medium">
                    Banking Intelligence
                  </span>
                  <div className="flex items-center gap-1 text-blue-600 group-hover:text-blue-700 font-medium text-sm">
                    <span>Oxu</span>
                    <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
        />
      )}

      {/* Results Info */}
      <div className="text-center mt-6">
        <p className="text-sm text-slate-500">
          Səhifə {currentPage} / {totalPages} • Toplam {summaries.length} xülasə
        </p>
      </div>
    </div>
  );
}
