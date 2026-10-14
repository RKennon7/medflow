import {useState, useEffect} from 'react';
import {Dialog, DialogTitle, DialogContent, InputLabel, Select, MenuItem,
    FormControl, DialogActions, TextField, Button,
    Typography} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

function ServiceReportFormDialog({open, initialValues, onClose, onSave}) {
    const [formData, setFormData] = useState({work_order_id: '', notes: '', file: null});

    useEffect(() => {
        setFormData(initialValues || {work_order_id: '', notes: '', file: null});
    }, [initialValues, open]);

    // handle changing form value of a specified field:
    const handleChange = (field) => (e) => {
        setFormData({...formData, [field]: e.target.value});
    };

    const handleSave = () => {
        const body = new FormData();
        body.append("work_order_id", formData.work_order_id);
        if (formData.notes) body.append("notes", formData.notes);
        body.append("file", formData.file);
        onSave(body);
    };

    return (
        <Dialog open={open} onClose={onClose} fullWidth>
          <DialogTitle>{initialValues ? 'Edit Service Report' : 'Add New Service Report'}</DialogTitle>
          <DialogContent>
            <TextField label="Work Order ID" value={formData.work_order_id} type='number'
                onChange={handleChange('work_order_id')} fullWidth margin='dense' />
            <TextField label="Notes" value={formData.notes} multiline
                onChange={handleChange('notes')} fullWidth margin='dense' />

            <Button
                component="label"
                variant="contained"
                tabIndex={-1}
                startIcon={<CloudUploadIcon />}
                >
                Upload file
                <input
                    hidden
                    type="file"
                    onChange={(e) =>
                        setFormData((prev) => ({...prev, file: e.target.files?.[0] ?? null }))
                    }
                />
            </Button>
            <Typography variant='body2'>
                {formData.file ? formData.file.name : "No file selected"}
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={onClose}>Cancel</Button>
            <Button onClick={handleSave} disabled={!formData.file}>Save</Button>
          </DialogActions>
        </Dialog>
    )

}
export default ServiceReportFormDialog;