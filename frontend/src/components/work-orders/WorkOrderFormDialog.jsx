import {useState, useEffect} from 'react';
import {Dialog, DialogTitle, DialogContent, InputLabel, Select, MenuItem,
    FormControl, DialogActions, TextField, Button} from '@mui/material';
import RoleGate from '../auth/RoleGate';

const PRIORITY_OPTIONS = ['Low', 'Medium', 'Critical'];
const STATUS_OPTIONS = ['Pending', 'In-Progress', 'Completed', 'Failed'];

function WorkOrderFormDialog({open, initialValues, onClose, onSave}) {
    const [formData, setFormData] = useState({title: '', priority: '', status: '', equipment_id: '', technician_id: ''});

    useEffect(() => {
        setFormData(initialValues || {title: '', priority: '', status: '', equipment_id: '', technician_id: ''});
    }, [initialValues, open]);

    // handle changing form value of a specified field:
    const handleChange = (field) => (e) => {
        setFormData({...formData, [field]: e.target.value});
    };

    return (
        <Dialog open={open} onClose={onClose} fullWidth>
          <DialogTitle>{initialValues ? 'Edit Work Order' : 'Add New Work Order'}</DialogTitle>
          <DialogContent>
            <RoleGate roles={["Clinical Admin"]}>
              <TextField label="Title" value={formData.title}
                onChange={handleChange('title')} fullWidth margin='dense' />
              <TextField label="Equipment ID" value={formData.equipment_id}
                onChange={handleChange('equipment_id')} fullWidth margin='dense' />
              <TextField label="Technician ID" value={formData.technician_id}
                onChange={handleChange('technician_id')} fullWidth margin='dense' type='number' />
              <TextField select label="Priority" value={formData.priority}
                onChange={handleChange('priority')} fullWidth margin='dense' >
                {PRIORITY_OPTIONS.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </TextField>
            </RoleGate>
            <TextField select label="Status" value={formData.status}
              onChange={handleChange('status')} fullWidth margin='dense' >
                {STATUS_OPTIONS.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
            </TextField>
          </DialogContent>
          <DialogActions>
            <Button onClick={onClose}>Cancel</Button>
            <Button onClick={() => onSave(formData)}>Save</Button>
          </DialogActions>
        </Dialog>
    );
}
export default WorkOrderFormDialog;