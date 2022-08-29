import {useEffect, useRef} from 'react';

const MASK =
  'M28.61 8.24a1.51 1.51 0 0 0-.13-.33 1.76 1.76 0 0 0-.24-.3 4.31 4.31 0 0 0-1.35-1.23L16.71.58a4.4 4.4 0 0 0-4.36 0L2.19 6.38A4.24 4.24 0 0 0 .83 7.61a1.38 1.38 0 0 0-.24.3 1.56 1.56 0 0 0-.14.33 4.39 4.39 0 0 0-.45 1.9v11.6a4.33 4.33 0 0 0 2.18 3.76l10.18 5.8a4.27 4.27 0 0 0 1.49.52 1.41 1.41 0 0 0 .68.18 1.48 1.48 0 0 0 .69-.18 4.27 4.27 0 0 0 1.49-.52l10.17-5.8a4.36 4.36 0 0 0 2.19-3.76v-11.6a4.26 4.26 0 0 0-.46-1.9zM13.8 3.1a1.44 1.44 0 0 1 1.46 0l9.39 5.35-3.57 2.05-7.33-4.21A1.45 1.45 0 1 0 12.3 8.8l5.88 3.38-3.65 2.1L4.42 8.44zM3.63 23a1.44 1.44 0 0 1-.72-1.25V10.92l10.17 5.87v11.58zm21.8 0L16 28.37V16.79l10.17-5.87v10.82a1.45 1.45 0 0 1-.74 1.26z';

const PROGRESS_MASK =
  'M26.89 6.38L16.71.58a4.4 4.4 0 0 0-4.36 0L2.19 6.38A4.33 4.33 0 0 0 0 10.14v11.6a4.33 4.33 0 0 0 2.18 3.76l10.18 5.8a4.34 4.34 0 0 0 4.35 0l10.17-5.8a4.36 4.36 0 0 0 2.19-3.76v-11.6a4.39 4.39 0 0 0-2.18-3.76zm-.73 15.36a1.45 1.45 0 0 1-.73 1.26l-10.16 5.78a1.44 1.44 0 0 1-1.46 0L3.63 23a1.44 1.44 0 0 1-.72-1.25V10.14a1.44 1.44 0 0 1 .72-1.25L13.8 3.1a1.44 1.44 0 0 1 1.46 0l10.18 5.8a1.47 1.47 0 0 1 .72 1.25z';

const COLORS = {
  default: '#160f24',
  progress: '#e1567c',
  progressTrack: 'rgba(144, 147, 193, .5)',
  success: '#4eda90',
  fail: '#c73852',
  canceled: '#f4834f',
  pending: '#8c5393',
};

function d2r(input) {
  return input * (Math.PI / 180);
}

function getStatusColor(status) {
  switch (status) {
    case 'cancelled':
      return COLORS.canceled;
    case 'failed':
      return COLORS.fail;
    case 'finished':
      return COLORS.success;
    case 'pending':
      return COLORS.pending;
    case 'in_progress':
      return COLORS.progressTrack;
    default:
      return COLORS.default;
  }
}

function useFaviconStatus({status, progress}) {
  const faviconElementRef = useRef(null);
  const originalFaviconUrl = useRef(null);
  const originalTitle = useRef(null);

  useEffect(() => {
    faviconElementRef.current = document.querySelector('link[rel*=icon]');

    if (!faviconElementRef.current) {
      return () => {};
    }

    originalFaviconUrl.current = faviconElementRef.current.href;
    originalTitle.current = document.title;

    return () => {
      document.title = originalTitle.current;
      faviconElementRef.current.href = originalFaviconUrl.current;
    };
  }, []);

  // update page title as the status changes
  useEffect(() => {
    document.title =
      status === 'in_progress'
        ? `[${progress}%] ${originalTitle.current}`
        : originalTitle.current;
  }, [status, progress]);

  // Update favicon as the status changes
  useEffect(() => {
    if (!faviconElementRef.current) {
      return;
    }

    const pct = progress / 100;

    const canvas = document.createElement('canvas');
    canvas.width = 32;
    canvas.height = 32;

    const ctx = canvas.getContext('2d');

    ctx.transform(1, 0, 0, 1, 1.467, 0);
    ctx.clip(new Path2D(MASK));
    ctx.resetTransform();
    ctx.fillStyle = getStatusColor(status);
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    if (status === 'in_progress') {
      ctx.transform(1, 0, 0, 1, 1.467, 0);
      ctx.clip(new Path2D(PROGRESS_MASK));
      ctx.resetTransform();

      const start = d2r(-90);
      const end = start + d2r(360 * pct);
      ctx.fillStyle = COLORS.progress;
      ctx.beginPath();
      ctx.moveTo(16, 16);
      ctx.arc(16, 16, 32, start, end);
      ctx.closePath();
      ctx.fill();
    }

    faviconElementRef.current.href = canvas.toDataURL('image/png');
  }, [status, progress]);
}

export default useFaviconStatus;
