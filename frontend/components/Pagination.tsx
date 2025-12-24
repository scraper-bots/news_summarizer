'use client';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
  const pages = [];
  const maxVisible = 5;

  let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
  let endPage = Math.min(totalPages, startPage + maxVisible - 1);

  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1);
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }

  return (
    <div className="flex items-center justify-center gap-2 mt-8">
      {/* Previous Button */}
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className={`px-4 py-2 rounded-lg font-medium transition-all ${
          currentPage === 1
            ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
            : 'bg-white text-slate-700 hover:bg-blue-50 hover:text-blue-600 border border-slate-200'
        }`}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      {/* First Page */}
      {startPage > 1 && (
        <>
          <button
            onClick={() => onPageChange(1)}
            className="px-4 py-2 rounded-lg font-medium bg-white text-slate-700 hover:bg-blue-50 hover:text-blue-600 border border-slate-200 transition-all"
          >
            1
          </button>
          {startPage > 2 && (
            <span className="px-2 text-slate-400">...</span>
          )}
        </>
      )}

      {/* Page Numbers */}
      {pages.map((page) => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={`px-4 py-2 rounded-lg font-medium transition-all ${
            page === currentPage
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md'
              : 'bg-white text-slate-700 hover:bg-blue-50 hover:text-blue-600 border border-slate-200'
          }`}
        >
          {page}
        </button>
      ))}

      {/* Last Page */}
      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && (
            <span className="px-2 text-slate-400">...</span>
          )}
          <button
            onClick={() => onPageChange(totalPages)}
            className="px-4 py-2 rounded-lg font-medium bg-white text-slate-700 hover:bg-blue-50 hover:text-blue-600 border border-slate-200 transition-all"
          >
            {totalPages}
          </button>
        </>
      )}

      {/* Next Button */}
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className={`px-4 py-2 rounded-lg font-medium transition-all ${
          currentPage === totalPages
            ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
            : 'bg-white text-slate-700 hover:bg-blue-50 hover:text-blue-600 border border-slate-200'
        }`}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  );
}
