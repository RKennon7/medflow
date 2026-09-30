import {createTheme} from '@mui/material/styles';

const theme = createTheme({
  "palette": {
    "primary": {
      "main": "#a5daee"
    },
    "secondary": {
      "main": "#7ae697"
    },
    "background": {
      "default": "#020712",
      "paper": "#020712"
    },
    "mode": "dark"
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

export default theme;