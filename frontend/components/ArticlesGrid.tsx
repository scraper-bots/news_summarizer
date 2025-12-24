'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Article } from '@/types';
import { formatDateTime, getPlaceholderImage, truncateText } from '@/lib/utils';
import Pagination from './Pagination';

interface ArticlesGridProps {
  articles: Article[];
}

const ITEMS_PER_PAGE = 9;

export default function ArticlesGrid({ articles }: ArticlesGridProps) {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(articles.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const currentArticles = articles.slice(startIndex, endIndex);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (articles.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p className="text-slate-500">Hələ heç bir xəbər yoxdur</p>
      </div>
    );
  }

  return (
    <div>
      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {currentArticles.map((article, index) => (
          <div
            key={article.id}
            className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden border border-slate-200 flex flex-col group"
          >
            {/* Image */}
            <div className="relative h-48 bg-gradient-to-br from-slate-100 to-slate-200 overflow-hidden">
              <Image
                src={getPlaceholderImage(startIndex + index)}
                alt={article.title}
                fill
                className="object-cover group-hover:scale-105 transition-transform duration-300"
              />
              <div className="absolute top-3 right-3 bg-blue-600 text-white text-xs px-3 py-1 rounded-full font-medium shadow-lg">
                {article.source}
              </div>
            </div>

            {/* Content */}
            <div className="p-5 flex flex-col flex-grow">
              {/* Title */}
              <h3 className="font-bold text-slate-900 text-lg mb-3 line-clamp-2 group-hover:text-blue-600 transition-colors">
                {article.title}
              </h3>

              {/* Description */}
              <p className="text-slate-600 text-sm mb-4 line-clamp-3 flex-grow">
                {truncateText(article.content, 150)}
              </p>

              {/* Footer */}
              <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>{formatDateTime(article.published_date)}</span>
                </div>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-medium hover:underline"
                >
                  <span>Oxu</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
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
          Səhifə {currentPage} / {totalPages} • Toplam {articles.length} xəbər
        </p>
      </div>
    </div>
  );
}
