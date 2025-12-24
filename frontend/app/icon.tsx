import { ImageResponse } from 'next/og';

// Image metadata
export const size = {
  width: 32,
  height: 32,
};
export const contentType = 'image/png';

// Icon component
export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #3B82F6 0%, #6366F1 100%)',
          borderRadius: '6px',
        }}
      >
        <div
          style={{
            fontSize: 20,
            color: 'white',
            fontWeight: 'bold',
            display: 'flex',
          }}
        >
          📊
        </div>
      </div>
    ),
    {
      ...size,
    }
  );
}
