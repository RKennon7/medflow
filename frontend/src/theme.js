import {createTheme} from '@mui/material/styles';

const palettes = {
  dark: {
    primary: { main: '#a5daee' },
    secondary: { main: '#7ae697' },
    background: { default: '#020712', paper: '#020712' },
    title: { main: '#a5daee' },
  },
  light: {
    primary: { main: '#1a7a99' },
    secondary: { main: '#7ae697' },
    background: { default: '#dfdddf', paper: 'rgb(241, 240, 241)' },
    title: { main: 'rgb(241, 240, 241)' },
  },
};

export const getTheme = (mode) => createTheme({
  palette: {
    mode,
    ...palettes[mode],
  },
  "typography": {
    "fontFamily": "Space Grotesk",
    "fontWeightLight": 100,
    "fontWeightRegular": 200,
    "fontWeightMedium": 300,
    "fontWeightBold": 500
  },
  "spacing": 11,
  "shape": {
    "borderRadius": 12
  }
});

export default getTheme;