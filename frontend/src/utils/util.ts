export const formatTeamColor = (color: string): string => {
  if (!color) {
    return '#333333';
  }
  return color.startsWith('#') ? color : `#${color}`;
};

/**
 * Gets the URL for a country's flag using the country code
 * Uses the flagcdn.com service which provides SVG flags
 * @param {string} countryCode - Two letter ISO country code (e.g., 'GB', 'DE', 'ES')
 * @returns {string} URL to the country's flag image
 */
export const getCountryFlagUrl = (countryCode: string): string => {
  if (!countryCode) {
    return 'https://flagcdn.com/ca.svg';
  }

  // Convert country code to lowercase as required by the API
  const code = countryCode.toLowerCase();

  // Using flagcdn.com which provides free SVG flags
  return `https://flagcdn.com/${code}.svg`;
};