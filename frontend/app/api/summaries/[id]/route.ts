import { NextResponse } from 'next/server';
import { getSummaryById, getArticlesBySessionId } from '@/lib/db';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const summaryId = parseInt(id);

    if (isNaN(summaryId)) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid summary ID'
        },
        { status: 400 }
      );
    }

    const summary = await getSummaryById(summaryId);

    if (!summary) {
      return NextResponse.json(
        {
          success: false,
          error: 'Summary not found'
        },
        { status: 404 }
      );
    }

    const articles = await getArticlesBySessionId(summaryId);

    return NextResponse.json({
      success: true,
      data: {
        ...summary,
        articles
      }
    });
  } catch (error) {
    console.error('Error fetching summary:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch summary'
      },
      { status: 500 }
    );
  }
}
