import React, { useEffect, useState } from 'react';
import { Grid, Box, CircularProgress, Alert } from '@mui/material';
import ReliabilityCard from './ReliabilityCard';
import apiClient from '../../api/client.js';

function ReliabilityList(){
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let isMounted = true;
        //console.log("equipment status grid mounted, starting fetch");
        setLoading(true);
        // fetch function
        async function fetchReliability() {
            try {
                const response = await apiClient.get('/equipment/reliability');
                if (isMounted) setData(response.data);
            } catch {
                if (isMounted) setError('Could not load reliability report');
            } finally {
                if (isMounted) setLoading(false);
            }
        }
        fetchReliability();
        return () => {
            isMounted = false;
        };

    }, []);

    if (loading) return <CircularProgress />;
    if (error) return <Alert severity="error">{error}</Alert>;

    return(
        <Grid container spacing={3}>
          {data.map((item) => (
            <Grid item key={item.equipment_model} xs={12} sm={6} md={4}>
              <ReliabilityCard
                equipmentModel={item.equipment_model}
                completedCount={item.completed_count}
                failedCount={item.failed_count}
              />
            </Grid>
          ))}
        </Grid>
    );
}

export default ReliabilityList;