import {Box, Card, CardContent, Typography, Stack} from '@mui/material';
import { PieChart } from '@mui/x-charts/PieChart';

function ReliabilityCard({equipmentModel, completedCount, failedCount}) {
    const total = completedCount + failedCount;
    const successRate = total > 0 ? ((completedCount / total) * 100).toFixed(1) : 0;

    const chartData = [
        { id: 0, value: completedCount, label: 'Completed', color: '#2e7d32'}, // green
        { id: 1, value: failedCount, label: 'Failed', color: '#d32f2f'}, // red
    ];

    return (
        <Card elevation={2} sx={{maxWidth: 360, borderRadius: 3, p: 1}}>
          <CardContent>
            {/** Header & success metric */}
            <Stack direction="row" sx={{justifyContent: 'space-between', alignItems: "center", mb: 1, mr: 1}}>
              <Box>
                <Typography variant="h6" fontWeight="bold">{equipmentModel}: </Typography>
                <Typography variant="body2" color="text.secondary">Total Work Orders: {total}</Typography>
              </Box>
              <Box sx={{width: '30%'}}>
                <Typography variant="h5" fontWeight="bold" color="success.main">
                    {successRate}%
                </Typography>
                <Typography variant="caption" color="text.secondary">Success Rate</Typography>
              </Box>
            </Stack>

            {/** Pie chart */}
            {total > 0 ? (
              <Box sx={{height: 180, width: '100%', display: 'flex', justifyContent: 'center'}}>
                <PieChart
                  series={[
                    {
                      data: chartData,
                      innerRadius: 35, // donut style
                      outerRadius: 70,
                      paddingAngle: 2,
                      cornerRadius: 4,
                    },
                  ]}
                  height={180}
                  margin={{top: 10, bottom: 10, left: 10, right: 10}}
                  slotProps={{
                    legend: {
                      direction: 'row',
                      position: {vertical: 'bottom', horizontal: 'center'},
                    },
                  }}
                />
              </Box>    
            ) : (
              <Typography variant="body2" color="text.secondary" align="center" sx={{py: 4}}>
                No completed or failed work orders recorded.
              </Typography>
            )}
          </CardContent>
        </Card>
    );
}

export default ReliabilityCard;