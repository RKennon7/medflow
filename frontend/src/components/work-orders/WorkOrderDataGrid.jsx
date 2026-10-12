import CrudDataGrid from "../general/CrudDataGrid";
import { can } from "../../context/permissions";
import { useAuth } from "../../context/AuthContext";
import WorkOrderFormDialog from "./WorkOrderFormDialog";

const columns = [
    { field: "id", headerName: "ID", width: 70 },
    { field: "title", headerName: "Title", width: 230 },
    { field: "priority", headerName: "Priority", width: 120 },
    { field: "status", headerName: "Status", width: 120 },
    { field: "equipment_id", headerName: "Equipment ID", width: 70 },
    { field: "technician_id", headerName: "Technician ID", width: 70 },
];

function WorkOrderDataGrid({ onSuccess }) {
    const { user } = useAuth();
    const role = user?.role;

    return (
      <CrudDataGrid
        endpoint="/work-orders"
        entityName="Work Order"
        columns={columns}
        FormComponent={WorkOrderFormDialog}
        canAdd={role === "Clinical Admin"}
        canEdit={can.edit(role)}
        canDelete={can.delete(role)}
        getUpdateUrl={(row) =>
            can.editAllFields(role) ? `/work-orders/${row.id}` : `/work-orders/${row.id}/status`
        }
        getLabel={(formData) => formData.title}
        onSuccess={onSuccess}
      />
    );
}
export default WorkOrderDataGrid;