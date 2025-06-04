export const formatTeamColor = (color: string): string => {
    if (!color) return '#333333';
    return color.startsWith('#') ? color : `#${color}`;
  };