import {useEffect, useState} from 'react';
import {DataGrid, GridActionsCellItem} from '@mui/x-data-grid';
import {Alert, Box, Button, CircularProgress, Grid, Dialog, DialogActions, DialogTitle} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import apiClient from '../../api/client.js';
import EquipmentFormDialog from './EquipmentFormDialog.jsx';

function EquipmentDataGrid({onSuccess}){
    const [equipment, setEquipment] = useState([]);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [editingRow, setEditingRow] = useState(null);
    const [deleteTarget, setDeleteTarget] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // handler for when add button is clicked
    const handleAddClick = () => {
        setEditingRow(null);
        setDialogOpen(true);
    };

    // click handler for edit button
    const handleEditClick = (row) => {
        setEditingRow(row);
        setDialogOpen(true);
    };

    const handleDeleteClick = (row) => {
        setDeleteTarget(row);
    };

    async function fetchEquipment(){
        setLoading(true);
        try {
            const response = await apiClient.get('/equipment');
            setEquipment(response.data);
            setError(null);
        } catch {
            setError('Could not load equipment data.');
        } finally {
            setLoading(false);
        }
    }
    useEffect(() => {
        fetchEquipment();
    }, []);

    // handler for saving form data
    // separate cases for edit vs. create:
    const handleSave = async (formData) => {
        let verb = "";
        if(editingRow) {
            // case for edit: use patch
            verb = "updated"
            await apiClient.patch(`/equipment/${editingRow.id}`, formData);
        } else {
            // case for create: post
            verb = "created";
            await apiClient.post('/equipment', formData);
        }
        setDialogOpen(false);
        // fetch equipment rows again
        onSuccess(`Equipment ${formData.serialNumber} ${verb} successfully`);
        await fetchEquipment();
    }

    // handler for delete confirmation
    const handleConfirmDelete = async () => {
        // await the delete call
        try{
            await apiClient.delete(`/equipment/${deleteTarget.id}`);
            setDeleteTarget(null);
            onSuccess(`Equipment deleted successfully`);
            // fetch equipment rows
            await fetchEquipment();
        } catch {
            setError('an issue occurred');
        }
    }

    // define DataGrid columns and map them to api response data
    const columns = [
        {field: 'id', headerName: 'ID', width: 70},
        {field: 'serial_number', headerName: 'Serial Number', width: 150},
        {field: 'model', headerName: 'Model', width: 180},
        {field: 'charge_level', headerName: 'Charge Level', width: 100, type:'number'},
        {field: 'status', headerName: 'Status', width: 120},
        {field: 'hospital_id', headerName: 'Hospital ID', width: 70, type: 'number'},
        {
            field: 'actions', headerName: 'Actions', width: 100, type:'actions',
            getActions: (params) => [
                <GridActionsCellItem
                  icon={<EditIcon />}
                  label="Edit"
                  onClick={() => handleEditClick(params.row)}
                />,
                <GridActionsCellItem
                  icon={<DeleteIcon />}
                  label="Delete"
                  onClick={() => handleDeleteClick(params.row)}
                />,
            ],
        },
    ];

    // spinning progress indicator if loading data
    if (loading) return <CircularProgress />;

    // show error alert if api call fails
    if (error) return <Alert severity="error">{error}</Alert>;

    // loads data grid component if successful
    return (
        <Box>
          <Button variant="contained" sx={{mb: 2}} onClick={handleAddClick}>Add Equipment</Button>
          <Box sx={{height: 400, width: '100%'}}>
            <DataGrid rows={equipment} columns={columns} getRowId={(row) => row.id} />
          </Box>
          <EquipmentFormDialog
            open={dialogOpen}
            initialValues={editingRow}
            onClose={() => setDialogOpen(false)}
            onSave={handleSave}
          />

          {/** dialog for delete button */}
          <Dialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)}>
            <DialogActions>
              <Button onClick={() => setDeleteTarget(null)}>Cancel</Button>
              <Button onClick={handleConfirmDelete} color="error">Delete</Button>
            </DialogActions>
          </Dialog>
        </Box>
    );

}
export default EquipmentDataGrid;