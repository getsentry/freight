import React from 'react';

export const SvgIcon = React.forwardRef(function SvgIcon(
  {color = 'currentColor', size = '16px', viewBox = '0 0 16 16', ...props},
  ref
) {
  return (
    <svg {...props} viewBox={viewBox} fill={color} height={size} width={size} ref={ref} />
  );
});
