import { AppBar, Toolbar, Typography, Box, Button } from '@mui/material';
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart';

function AppHeader({username, role, onLogout}) {
    return(
        <AppBar position='static'>
            <Toolbar>
                <MonitorHeartIcon color="secondary" sx={{mr: 2}}/>
                <Typography variant='h5' component="h2" color="primary" sx={{mr: 4}}>
                    MedFlow Clinical Equipment Command Center
                </Typography>

                {username && (
                    <Box sx={{ display: 'flex', alignItems: 'right', gap: 2}}>
                        <Typography variant="body2">{username}({role})</Typography>
                        <Button color="inherit" onClick={onLogout}>Log Out</Button>
                    </Box>
                )}
            </Toolbar>
        </AppBar>
    );
}

export default AppHeader;