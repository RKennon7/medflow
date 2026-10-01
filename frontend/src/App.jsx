import {Container, Typography, Box, Tab, Tabs, Snackbar, Alert} from '@mui/material'
import AppHeader from './components/layout/AppHeader.jsx'
import {useState} from 'react';

import LoginForm from './components/auth/LoginForm.jsx';
import {AuthProvider, useAuth} from './context/AuthContext.jsx';
import EquipmentDataGrid from './components/equipment/EquipmentDataGrid.jsx';
import ReliabilityList from './components/equipment/ReliabilityList.jsx';
import DiscrepancyDataGrid from './components/work-orders/DiscrepancyDataList.jsx';
import MaintenanceFlags from './components/analytics/MaintenanceFlags.jsx';
import ReportingLines from './components/analytics/ReportingLines.jsx';

function Dashboard(){
  const {user, logout} = useAuth()
  const [activeTab, setActiveTab] = useState(0);
  const [notification, setNotification] = useState(null);

  return(
    <>
      <AppHeader username={user?.sub} role={user?.role} onLogout={logout} />
      <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
        <Tab label="Equipment" />
        <Tab label="Work Orders" />
        <Tab label="Analytics" />
      </Tabs>
      <Container maxWidth="lg" sx={{mt: 4}}>
        {activeTab === 0 && (
          <><Typography variant="h5" color="primary" component="h2" gutterBottom>
            Medical Equipment
          </Typography>
           
          <Box sx={{mb: 4}}>
            <EquipmentDataGrid onSuccess={setNotification} />
          </Box>

          <Typography variant="h5" component="h2" color='primary' gutterBottom>
            Equipment Reliability Report
          </Typography>
          <Box mb={4}>
            <ReliabilityList />
          </Box>
          
          </>
        )}

        {activeTab === 1 && (
          <><Typography variant="h5" component="h2" color='primary' gutterBottom>
            Co-Location Discrepancies
          </Typography>
          <Box sx={{mb: 4}}>
            <DiscrepancyDataGrid />
          </Box>
          
          </>
        )}

        {activeTab === 2 && (
          <><Typography variant="h5" component="h2" color='primary' gutterBottom>
            Maintenance Flags
          </Typography>
          <Box sx={{mb: 4}}>
            <MaintenanceFlags />
          </Box>

          <Typography variant="h5" component="h2" color='primary' gutterBottom>
            Reporting Lines
          </Typography>
          <Box>
            <ReportingLines />
          </Box>
          
          </>
        )}
      </Container>
      <Snackbar
        open={Boolean(notification)}
        autoHideDuration={4000}
        onClose={() => setNotification(null)}>
          <Alert severity='success' onClose={() => setNotification(null)}>
            {notification}
          </Alert>
        </Snackbar>
    </>
  );
}

function AppContent() {
  const {isAuthenticated} = useAuth();
  return isAuthenticated ? <Dashboard /> : <LoginForm />;
}

function App(){
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App;