import { useState, useEffect, useMemo } from "react";
import { DataGrid, GridActionsCellItem } from "@mui/x-data-grid";
import { Box, Button, Alert, Dialog, DialogTitle, DialogActions } from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import apiClient from '../../api/client.js';

/** Modular CRUD data grid that can be used as a base for different data models */

function CrudDataGrid({
    endpoint,
    entityName,
    columns,
    FormComponent,
    canAdd=true,
    canEdit=true,
    canDelete=true,
    getUpdateUrl = (row) => `${endpoint}/${row.id}`,
    getLabel = () => "", // label used in success message
    onSuccess = () => {},
    height = 400,
}) {
    const [rows, setRows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [editingRow, setEditingRow] = useState(null);
    const [deleteTarget, setDeleteTarget] = useState(null);

    async function fetchRows() {
        setLoading(true);
        try {
            const response = await apiClient.get(endpoint);
            setRows(response.data);
            setError(null);
        } catch {
            setError(`Could not load ${entityName.toLowerCase()} data.`);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { fetchRows(); }, [endpoint]);

    const handleAddClick = () => {setEditingRow(null); setDialogOpen(true); };
    const handleEditClick = (row) => { setEditingRow(row); setDialogOpen(true); };

    const handleSave = async (formData) => {
        if (editingRow) {
            await apiClient.patch(getUpdateUrl(editingRow), formData);
        } else {
            await apiClient.post(endpoint, formData);
        }
        const verb = editingRow ? "updated" : "created";
        setDialogOpen(false);
        onSuccess(`${entityName} ${getLabel(formData)} ${verb} successsfully`.replace("  ", " "));
        await fetchRows();
    };

    const handleConfirmDelete = async () => {
        try {
            await apiClient.delete(`${endpoint}/${deleteTarget.id}`);
            setDeleteTarget(null);
            onSuccess(`${entityName} deleted successfully`);
            await fetchRows();
        } catch {
            setDeleteTarget(null);
            setError(`Could not delete ${entityName.toLowerCase()}.`);
        }
    };

    const allColumns = useMemo(() => {
        if (!canEdit && !canDelete) return columns;
        return [
            ...columns,
            {
                field: "actions", headerName: "Actions", width: 100, type: "actions",
                getActions: (params) =>
                [
                    canEdit && (
                        <GridActionsCellItem key="edit" icon={<EditIcon />} label="Edit"
                          onClick={() => handleEditClick(params.row)} />
                    ),
                    canDelete && (
                        <GridActionsCellItem key="delete" icon={<DeleteIcon />} label="Delete"
                          onClick={() => setDeleteTarget(params.row)} />
                    ),
                ].filter(Boolean),
            },
        ];
    }, [columns, canEdit, canDelete]);

    return (
        <Box>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {canAdd && (
            <Button variant="contained" sx={{ mb: 2 }} onClick={handleAddClick}>
                Add {entityName}
            </Button>
          )}

          <Box sx={{ height, width: "100% "}}>
            <DataGrid rows={rows} columns={allColumns} loading={loading}
              getRowId={(row) => row.id} />
          </Box>

          <FormComponent
            open={dialogOpen}
            initialValues={editingRow}
            onClose={() => setDialogOpen(false)}
            onSave={handleSave}
          />

          <Dialog open={!!deleteTarget} onClose={() => setDeleteTarget(null)}>
            <DialogTitle>Delete this {entityName.toLowerCase()}?</DialogTitle>
            <DialogActions>
              <Button onClick={() => setDeleteTarget(null)}>Cancel</Button>
              <Button onClick={handleConfirmDelete} color="error">Delete</Button>
            </DialogActions>
          </Dialog>
        </Box>
    );

}
export default CrudDataGrid;