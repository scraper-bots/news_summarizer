# Azərbaycan Bank Sektoru - Frontend

Next.js frontend for displaying daily news summaries from the Azerbaijan banking sector.

## Features

- 📊 **Daily Summaries**: View AI-generated banking intelligence reports
- 📱 **Mobile-Friendly**: Fully responsive design optimized for all devices
- 🎨 **Modern UI**: Clean, attractive interface with Tailwind CSS
- ⚡ **Fast**: Built with Next.js App Router and Server Components
- 🌐 **Azerbaijani**: Full support for Azerbaijani language and characters

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Database**: PostgreSQL (via pg)
- **Deployment**: Vercel

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Access to the PostgreSQL database

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
```

3. Edit `.env.local` and add your database connection string:
```env
DATABASE_URL=postgresql://user:password@host:5432/database?sslmode=require
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── api/
│   │   ├── summaries/       # API routes for summaries
│   │   └── stats/           # API routes for statistics
│   ├── summary/[id]/        # Individual summary page
│   ├── layout.tsx           # Root layout with metadata
│   └── page.tsx             # Homepage with summaries list
├── lib/
│   ├── db.ts                # Database utilities
│   └── utils.ts             # Helper functions
├── types/
│   └── index.ts             # TypeScript types
└── public/
    └── icon.svg             # App icon/favicon
```

## API Routes

### GET /api/summaries
Get list of all summaries (most recent first)

**Query Parameters:**
- `limit` (optional): Number of summaries to return (default: 30)

**Response:**
```json
{
  "success": true,
  "data": [...],
  "count": 30
}
```

### GET /api/summaries/[id]
Get a single summary with its articles

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "scraping_date": "2024-12-24",
    "summary": "...",
    "articles": [...]
  }
}
```

### GET /api/stats
Get overall statistics

**Response:**
```json
{
  "success": true,
  "data": {
    "total_articles": 1234,
    "total_sources": 10,
    "latest_article_date": "2024-12-24"
  }
}
```

## Deployment to Vercel

### Method 1: Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Add environment variable in Vercel dashboard:
   - Go to Project Settings → Environment Variables
   - Add `DATABASE_URL` with your PostgreSQL connection string

### Method 2: GitHub Integration

1. Push your code to GitHub
2. Import project in [Vercel Dashboard](https://vercel.com/new)
3. Add `DATABASE_URL` environment variable
4. Deploy

### Environment Variables (Vercel)

Add these in your Vercel project settings:

- `DATABASE_URL`: PostgreSQL connection string

## Pages

### Homepage (`/`)
- Displays statistics (total articles, sources, latest article date)
- Lists all daily summaries with preview
- Responsive grid layout

### Summary Detail (`/summary/[id]`)
- Shows full AI-generated banking intelligence report
- Lists all articles from that scraping session
- Session statistics (articles count, sources, duration)

## Database Schema

The frontend reads from these PostgreSQL tables:

### `news.articles`
- Article content from news sources
- Links to scraping sessions

### `news.scraping_summaries`
- AI-generated summaries for each scraping session
- Statistics and metadata

## Features

### Responsive Design
- Mobile-first approach
- Adaptive layouts for all screen sizes
- Touch-friendly interactions

### Performance
- Server-side rendering with Next.js
- Optimized database queries
- Fast page loads

### Internationalization
- Full Azerbaijani language support
- UTF-8 encoding for special characters
- Azerbaijani date formatting

## License

Private project - All rights reserved
