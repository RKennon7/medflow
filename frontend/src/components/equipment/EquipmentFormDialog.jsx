import {useState, useEffect} from 'react';
import {Dialog, DialogTitle, DialogContent, InputLabel, Select, MenuItem,
    FormControl, DialogActions, TextField, Button} from '@mui/material';
import RoleGate from '../auth/RoleGate';

const STATUS_OPTIONS = ['Available', 'In-Use', 'Maintenance', 'Offline'];

function EquipmentFormDialog({open, initialValues, onClose, onSave}){
    const [formData, setFormData] = useState({serial_number: '', model: '', charge_level: '', status: '', hospital_id: ''});

    useEffect(() => {
        setFormData(initialValues || {serial_number: '', model: '', charge_level: '', status: '', hospital_id: ''});
    }, [initialValues, open]);

    // handle changing form value of a specified field:
    const handleChange = (field) => (e) => {
        setFormData({...formData, [field]: e.target.value});
    };

    // validate charge level on change:
    const handleChargeChange = (e) => {
        const value = Math.min(100, Math.max(0, Number(e.target.value)));
        setFormData({...formData, charge_level: value});
    };

    return (
        <Dialog open={open} onClose={onClose} fullWidth>
          <DialogTitle>{initialValues ? 'Edit Equipment' : 'Add New Equipment'}</DialogTitle>
          <DialogContent>
            <RoleGate roles={["Clinical Admin"]}>
              <TextField label="Serial Number" value={formData.serial_number}
                onChange={handleChange('serial_number')} fullWidth margin='dense' />
              <TextField label="Model" value={formData.model}
                onChange={handleChange('model')} fullWidth margin='dense' />
              <TextField label="Charge Level %" value={formData.charge_level}
                onChange={handleChargeChange} fullWidth margin='dense' />
              <TextField label="Hospital ID" value={formData.hospital_id}
                onChange={handleChange('hospital_id')} fullWidth margin='dense' type='number' />
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

export default EquipmentFormDialog;