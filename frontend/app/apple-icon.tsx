import { ImageResponse } from 'next/og';

// Image metadata
export const size = {
  width: 180,
  height: 180,
};
export const contentType = 'image/png';

// Apple icon component
export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexDirection: 'column',
          background: 'linear-gradient(135deg, #3B82F6 0%, #6366F1 100%)',
        }}
      >
        <div
          style={{
            fontSize: 80,
            display: 'flex',
            marginBottom: 10,
          }}
        >
          📊
        </div>
        <div
          style={{
            fontSize: 24,
            color: 'white',
            fontWeight: 'bold',
            display: 'flex',
          }}
        >
          Bank
        </div>
      </div>
    ),
    {
      ...size,
    }
  );
}
