import { NextResponse } from 'next/server';
import { getSummaries } from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '30');

    const summaries = await getSummaries(limit);

    return NextResponse.json({
      success: true,
      data: summaries,
      count: summaries.length
    });
  } catch (error) {
    console.error('Error fetching summaries:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch summaries'
      },
      { status: 500 }
    );
  }
}
