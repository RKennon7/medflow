import CrudDataGrid from "../general/CrudDataGrid";
import { GridActionsCellItem } from "@mui/x-data-grid";
import FileOpenIcon from '@mui/icons-material/FileOpen';
import { can } from "../../context/permissions";
import { useAuth } from "../../context/AuthContext";
import apiClient from "../../api/client";
import ServiceReportFormDialog from "./ServiceReportFormDialog";



function ServiceReportDataGrid({ onSuccess }) {
    const { user } = useAuth();
    const role = user?.role;

    const handleViewFile = async (reportId) => {
        const { data } = await apiClient.get(`/service-reports/${reportId}/file`);
        window.open(data.url, "_blank");
    }

    const columns = [
        { field: "id", headerName: "ID", width: 70 },
        { field: "work_order_id", headerName: "Work Order ID", width: 70},
        { field: "notes", headerName: "Notes", flex: 1},
        { field: "timestamp", headerName: "Uploaded", width: 180,
            valueFormatter: (value) => new Date(value).toLocaleString(),
        },
        { field: "view_file", type: "actions", headerName: "File", width: 80,
            getActions: (params) => [
                <GridActionsCellItem
                icon={<FileOpenIcon />}
                label="View file"
                onClick={() => handleViewFile(params.row.id)}
                />,
            ],
        },
    ];

    return (
        <CrudDataGrid
          endpoint="/service-reports"
          entityName="Service Report"
          columns={columns}
          FormComponent={ServiceReportFormDialog}
          canAdd={can.uploadServiceReport(role)}
          canEdit={can.edit(role)}
          canDelete={can.delete(role)}
          getUpdateUrl={(row) =>
            can.editAllFields(role) ? `/service-reports/${row.id}` : `/service-reports/${row.id}/status`
          }
          getLabel={(formData) => formData.title}
          onSuccess={onSuccess}
        />
    )

}
export default ServiceReportDataGrid;