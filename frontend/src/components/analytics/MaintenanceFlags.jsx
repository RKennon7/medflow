import {useEffect, useState} from 'react';
import {Alert, CircularProgress, Table, TableBody, TableCell, TableContainer,
    TableHead, TableRow, Typography,
} from '@mui/material';
import apiClient from '../../api/client.js';

function MaintenanceFlags() {
    const [flags, setFlags] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        async function fetchFlags() {
            try {
                const response = await apiClient.get('/hospitals/maintenance');
                setFlags(response.data);
            } catch {
                setError('Could not load maintenance flags.');
            } finally {
                setLoading(false);
            }
        }
        fetchFlags();
    }, []);

    if (loading) return <CircularProgress />;
    if(error) return <Alert severity="error">{error}</Alert>;
    if (flags.length === 0) {
        return <Typography>No hospitals currently have more than 30% of their equipment flagged for maintenance</Typography>; 
    }

    return (
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Hospital</TableCell>
                <TableCell>Total Equipment</TableCell>
                <TableCell>In Maintenance</TableCell>
                <TableCell>Percentage</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {flags.map((row) => (
                <TableRow key={row.hospital_id}>
                  <TableCell>{row.hospital_name}</TableCell>
                  <TableCell>{row.total_equipment}</TableCell>
                  <TableCell>{row.maintenance_count}</TableCell>
                  <TableCell>{row.maintenance_percent}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
    );
}

export default MaintenanceFlags;